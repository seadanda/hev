#!/usr/bin/env python3

import asyncio
import serial_asyncio
import logging
import binascii
from struct import error as StructError
from CommsCommon import PayloadFormat, DataFormat
from CommsFormat import CommsPacket, CommsACK, CommsNACK

# Set up logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.DEBUG)

class CommsLLI:
    def __init__(self, loop, queue):
        super().__init__()
        self._queue = queue
        self._dv = asyncio.Event()
        self._connected = False
        self._loop = loop
        self._reader = None
        self._writer = None

    async def main(self):
        self._reader, self._writer = await serial_asyncio.open_serial_connection(url='/dev/ttyACM0', baudrate=115200)
        self._connected = True
        while self._connected:
            #sent = self.send()
            receiver = self.recv()
            await asyncio.gather(*[receiver], return_exceptions=True)

    async def send(self, packet):
        #for msg in self._queue:
        logging.info(f"Sending {packet}")
        await self._writer.write(packet)
        logging.info(f"Sent {packet}")

    def getPayload(self, packet):
        payload = None
        comms_response = None
        #FIXME quick hack to get the new class method working
        for i in range(1,7):
            try:
                payload = PayloadFormat.fromByteArray(bytes([i]) + packet.byteArray)
            except StructError:
                continue
            else:
                break

        # prepare ack/nack
        if payload is None:
            logging.error(f"Invalid payload: {payload}")
            comms_response = CommsNACK(packet.address)
        else:
            logging.debug(f"Received payload type {payload.getType()} for timestamp {payload.timestamp}")
            comms_response = CommsACK(packet.address)

        comms_response.setSequenceReceive(packet.sequence)

        return payload, comms_response

    async def recv(self):
        while self._connected:
            while True:
                rawdata = await self._reader.readuntil(CommsPacket.separator)
                # valid packets are minimum 6 bytes excluding start flag
                if len(rawdata) >= 6:
                    # replace start flag which was stripped
                    rawdata = CommsPacket.separator + rawdata
                    break

            data = bytearray()
            for el in rawdata:
                data.extend(bytes([el]))

            packet = CommsPacket(data)
            if packet.decode():
                # packet contains data
                payload, response = self.getPayload(packet)
                print(binascii.hexlify(response.encode()))
                logging.debug(f"Received packet {binascii.hexlify(payload)}")
                await self.send(response.encode())
            else:
                # packet is an ack/nack from previously sent data
                if packet.acked:
                    logging.debug("Received ACK")
                    #pop packet from sending queue
                else:
                    logging.debug("Received NACK")
                    #trigger another send, if anything is there

    @property
    def queue(self):
        return self._queue
    
    @queue.setter
    def queue(self, packet):
        self._queue.put(packet)
        self._dv.set()


if __name__ == "__main__":
    # setup sender and receiver
    read_queue = asyncio.Queue()
    write_queue = asyncio.Queue()

    # schedule async tasks
    loop = asyncio.get_event_loop()

    # setup serial devices
    comms = CommsLLI(loop, read_queue)

    try:
        asyncio.gather(comms.main(), return_exceptions=True)
        loop.run_forever()
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        logging.info("Closing LLI")
    finally:
        loop.close()