#!/usr/bin/env python3

import asyncio
import serial_asyncio
import logging
import binascii
import time
from collections import deque
from struct import error as StructError
from CommsCommon import PayloadFormat, PAYLOAD_TYPE
from CommsFormat import CommsPacket, CommsACK, CommsNACK, CommsChecksumError, generateAlarm, generateCmd, generateData

# Set up logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)

class CommsLLI:
    def __init__(self, loop):
        super().__init__()
        # IO
        self._loop = loop
        self._reader = None
        self._writer = None
        self._connected = False

        # send
        self._queue_size = 16
        self._alarms   = asyncio.Queue(maxsize=self._queue_size, loop=self._loop)
        self._commands = asyncio.Queue(maxsize=self._queue_size, loop=self._loop)
        self._data     = asyncio.Queue(maxsize=self._queue_size, loop=self._loop)

        # acks from arduino
        self._dv_alarms   = asyncio.Event(loop=self._loop)
        self._dv_commands = asyncio.Event(loop=self._loop)
        self._dv_data     = asyncio.Event(loop=self._loop)
        # maps between address and queues/events/timeouts 
        self._queues   = {0xC0: self._alarms, 0x80: self._commands, 0x40: self._data}
        self._timeouts = {0xC0: 10, 0x80: 50, 0x40: 200}
        self._acklist  = {0xC0: self._dv_alarms, 0x80: self._dv_commands, 0x40: self._dv_data}
        
        # receive
        #self._payloadrecv = asyncio.Queue(maxsize=self._queue_size, loop=self._loop)
        self._payloadrecv = deque(maxlen = self._queue_size)
        self._observers = []

        # packet counting
        self._sequence_send    = 0
        self._sequence_receive = 0

    async def main(self, device, baudrate):
        self._reader, self._writer = await serial_asyncio.open_serial_connection(url=device, baudrate=baudrate, timeout = 2, dsrdtr = True)
        self._connected = True
        while self._connected:
            #sendAlarm = self.send(0xC0)
            sendCmd = self.send(0x80)
            #sendData = self.send(0x40)
            receiver = self.recv()
            await asyncio.gather(*[receiver, sendCmd], return_exceptions=True)

    async def send(self, address):
        queue = self._queues[address]
        while self._connected:
            logging.debug("Waiting for Command")
            packet = await queue.get()
            packet.setSequenceSend(self._sequence_send)
            for send_attempt in range(5):
                # try to send the packet 5 times
                try:
                    await self.sendPacket(packet)
                    await asyncio.wait_for(self._acklist[address].wait(), timeout=self._timeouts[address] / 1000)
                except asyncio.TimeoutError:
                    pass
                except Exception:
                    # catch everything else and propagate it
                    raise
                else:
                    # acknowledged
                    break

    def writePayload(self, payload):
        try:
            # TODO replace these two dicts with address mappings like everywhere else
            PAYLOAD_TYPE_TO_GEN = {
                1: generateData,
                2: generateData,
                3: generateData,
                4: generateData,
                5: generateCmd,
                6: generateAlarm,
            }
            generatePacket = PAYLOAD_TYPE_TO_GEN[payload.getType()]
            tmp_comms = generatePacket(payload)

            qlist = [v for v in self._queues.values()]
            PAYLOAD_TYPE_TO_QUEUE = {
                1: qlist[2],
                2: qlist[2],
                3: qlist[2],
                4: qlist[2],
                5: qlist[1],
                6: qlist[0],
            }
            queue = PAYLOAD_TYPE_TO_QUEUE[payload.getType()]
            queue.put_nowait(tmp_comms)

            return True
        except KeyError:
            return False

    async def sendPacket(self, packet):
        if isinstance(packet, CommsACK):
            # don't log acks
            pass
        elif isinstance(packet, CommsNACK):
            logging.warning(f"Sending NACK: {binascii.hexlify(packet.encode())}")
        else:
            logging.info(f"Sending {binascii.hexlify(packet.encode())}")
        self._writer.write(packet.encode())

    async def readPacket(self):
        while True:
            rawdata = await self._reader.readuntil(CommsPacket.start_flag)
            # valid packets are minimum 6 bytes excluding start flag
            if len(rawdata) >= 6:
                # replace start flag which was stripped while searching
                rawdata = CommsPacket.start_flag + rawdata
                break
        return CommsPacket(bytearray(rawdata))

    def finishPacket(self, address):
        self._sequence_send = (self._sequence_send + 1) % 128
        self._queues[address].task_done()
        self._acklist[address].set()

    async def recv(self):
        while self._connected:
            packet = await self.readPacket()

            try:
                data = packet.decode()
            except CommsChecksumError:
                # checksum failed! wait for it to be resent
                logging.warning(f"Packet did not match checksum: {packet._data}")
                continue

            if data is None:
                # packet is an ack/nack from previously sent data
                if packet.acked:
                    logging.info("Received ACK")
                    # increase packet counter
                    self.finishPacket(packet.address)
                else:
                    logging.debug("Received NACK")
            else:
                # packet should contain valid data
                try:
                    payload = PayloadFormat.fromByteArray(packet.byteArray)
                    self.payloadrecv = payload
                    logging.debug(f"Received payload type {payload.getType()} for timestamp {payload.timestamp}")
                    comms_response = CommsACK(packet.address)
                except (StructError, ValueError):
                    # invalid payload, but valid checksum - this is bad!
                    logging.error(f"Invalid payload: {payload}")
                    # restart/reflash/swap to redundant microcontroller?
                    comms_response = CommsNACK(packet.address)
                finally:
                    comms_response.setSequenceReceive(packet.sequence_receive)
                    await self.sendPacket(comms_response)

    # callback to dependants to read the received payload
    @property
    def payloadrecv(self):
        return self._payloadrecv

    @payloadrecv.setter
    def payloadrecv(self, payload):
        for callback in self._observers:
            callback(payload)

    def bind_to(self, callback):
        self._observers.append(callback)


if __name__ == "__main__":
    try:
        # schedule async tasks
        loop = asyncio.get_event_loop()

        # setup serial devices
        comms = CommsLLI(loop)

        asyncio.gather(comms.main("/dev/ttyUSB0", 115200), return_exceptions=True)
        loop.run_forever()
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        logging.info("Closing LLI")
    finally:
        loop.close()