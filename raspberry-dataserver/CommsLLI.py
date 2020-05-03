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
        self._queue_size = 16
        self._alarms   = deque(maxlen = self._queue_size)
        self._commands = deque(maxlen = self._queue_size)
        self._data     = deque(maxlen = self._queue_size)
        # map of {timeout: queue}
        self._queues = {10: self._alarms, 50: self._commands, 200: self._data}
        self._datavalid = asyncio.Event()
        self._timeLastTransmission = int(round(time.time() * 1000)) # in seconds
        
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
            sender = self.send()
            receiver = self.recv()
            await asyncio.gather(*[receiver, sender], return_exceptions=True)

    async def send(self):
        while self._connected:
            await self._datavalid.wait()
            for timeout, queue in self._queues:
                if len(queue) > 0:
                    logging.debug(f'Queue length: {len(queue)}')
                    current_time = int(round(time.time() * 1000))
                    if current_time > (self._timeLastTransmission + timeout):
                        self._timeLastTransmission = current_time
                        queue[0].setSequenceSend(self._sequence_send)
                        self.sendPacket(queue[0])
            if len([packet for queue in self._queues.values() for packet in queue]) == 0:
                self._datavalid.clear()

    def writePayload(self, payload):
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

        PAYLOAD_TYPE_TO_QUEUE = {
            1: self._queues[2],
            2: self._queues[2],
            3: self._queues[2],
            4: self._queues[2],
            5: self._queues[1],
            6: self._queues[0],
        }
        queue = PAYLOAD_TYPE_TO_QUEUE[payload.getType()]
        queue.append(tmp_comms)
        self._datavalid.set()
            
        return True

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

    def finishPacket(self, address):
        ADDRESS_TO_QUEUE = {
            0x40: self._queues[2],
            0x80: self._queues[1],
            0xC0: self._queues[0],
        }
        queue = ADDRESS_TO_QUEUE[address]
        if len(queue) > 0:
            # 0x7F to deal with possible overflows (0 should follow after 127)
            if ((queue[0].getSequenceSend() + 1) & 0x7F) == self._sequence_receive:
                self._sequence_send = (self._sequence_send + 1) % 128
                queue.popleft()

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
                    logging.debug("Received ACK")
                    #pop packet from sending queue
                    self.finishPacket(packet.address)
                else:
                    logging.debug("Received NACK")
            else:
                # packet should contain valid data
                try:
                    payload = PayloadFormat.fromByteArray(packet.byteArray)
                    self.payloadrecv = payload
                    logging.info(f"Received payload type {payload.getType()} for timestamp {payload.timestamp}")
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
        self._payloadrecv.append(payload)
        logging.debug(f"Pushed {payload} to FIFO")
        for callback in self._observers:
            # peek at the leftmost item, don't pop until receipt confirmed
            callback(self._payloadrecv[0])

    def bind_to(self, callback):
        self._observers.append(callback)

    def pop_payloadrecv(self):
        # from callback. confirmed receipt, pop value
        poppedval = self._payloadrecv.popleft()
        logging.debug(f"Popped {poppedval} from FIFO")
        if len(self._payloadrecv) > 0:
            # purge full queue if Dependant goes down when it comes back up
            for callback in self._observers:
                callback(self._payloadrecv[0])


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