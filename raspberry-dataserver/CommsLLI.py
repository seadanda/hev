#!/usr/bin/env python3

import asyncio
import serial_asyncio
import logging
import binascii
import time
from collections import deque
from struct import error as StructError
from CommsCommon import PayloadFormat
from CommsFormat import CommsPacket, CommsACK, CommsNACK, CommsChecksumError

# Set up logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.DEBUG)

class CommsLLI:
    def __init__(self, loop, queue):
        super().__init__()
        # IO
        self._loop = loop
        self._reader = None
        self._writer = None
        self._connected = False
        # send
        self._alarms = deque(maxlen = 16)
        self._commands = deque(maxlen = 16)
        self._data = deque(maxlen = 16)
        self._datavalid = asyncio.Event()
        # receive
        self._sequence_send    = 0
        self._sequence_receive = 0
        self._timeLastTransmission = 0

    async def main(self, device, baudrate):
        self._reader, self._writer = await serial_asyncio.open_serial_connection(url=device, baudrate=baudrate, timeout = 2, dsrdtr = True)
        self._connected = True
        while self._connected:
            sender = self.send()
            receiver = self.recv()
            await asyncio.gather(*[receiver, sender], return_exceptions=True)

    def sendQueue(self, queue, timeout):
        if len(queue) > 0:
            logging.debug(f'Queue length: {len(queue)}')
            current_time = int(round(time.time() * 1000))
            if current_time > (self._timeLastTransmission + timeout):
                self._timeLastTransmission = current_time
                queue[0].setSequenceSend(self._sequence_send)
                self.sendPacket(queue[0])
                    
    async def send(self):
        while self._connected:
            await self._datavalid.wait()
            self.sendQueue(self._alarms, 10)
            self.sendQueue(self._commands, 50)
            self.sendQueue(self._data, 200)
            if self.finishedSending():
                self._datavalid.clear()

    async def sendPacket(self, packet):
        logging.debug(f"Sending {binascii.hexlify(packet.encode())}")
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


    async def recv(self):
        while self._connected:
            packet = await self.readPacket()

            try:
                data = packet.decode()
            except CommsChecksumError:
                # checksum failed! wait for it to be resent
                logging.warning(f"Packet did not match checksum: {packet._data}")
                break

            if data is None:
                # packet is an ack/nack from previously sent data
                if packet.acked:
                    logging.debug("Received ACK")
                    #pop packet from sending queue
                else:
                    logging.debug("Received NACK")
                    #trigger another send, if anything is there
            else:
                # packet should contain valid data
                try:
                    payload = PayloadFormat.fromByteArray(packet.byteArray)
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


if __name__ == "__main__":
    try:
        # setup sender and receiver
        read_queue = asyncio.Queue()
        write_queue = asyncio.Queue()

        # schedule async tasks
        loop = asyncio.get_event_loop()

        # setup serial devices
        comms = CommsLLI(loop, read_queue)

        asyncio.gather(comms.main("/dev/ttyUSB0", 115200), return_exceptions=True)
        loop.run_forever()
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        logging.info("Closing LLI")
    finally:
        loop.close()