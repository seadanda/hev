#!/usr/bin/env python3
# © Copyright CERN, Riga Technical University and University of Liverpool 2020.
# All rights not expressly granted are reserved. 
# 
# This file is part of hev-sw.
# 
# hev-sw is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public Licence as published by the Free
# Software Foundation, either version 3 of the Licence, or (at your option)
# any later version.
# 
# hev-sw is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public Licence
# for more details.
# 
# You should have received a copy of the GNU General Public License along
# with hev-sw. If not, see <http://www.gnu.org/licenses/>.
# 
# The authors would like to acknowledge the much appreciated support
# of all those involved with the High Energy Ventilator project
# (https://hev.web.cern.ch/).



import asyncio
import serial_asyncio
import logging
import binascii
import time
import argparse
from collections import deque
from enum import Enum, IntEnum
from dataclasses import asdict
from struct import error as StructError
from CommsCommon import PayloadFormat, PAYLOAD_TYPE, HEVVersionError
from CommsFormat import CommsPacket, CommsACK, CommsNACK, CommsChecksumError, generateAlarm, generateCmd, generateData

# Set up logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)

class SequenceReceiveMismatch(Exception):
    pass

class CommsLLI:
    def __init__(self, loop, throttle=1, file='', number=10000):
        super().__init__()
        # IO
        self._loop = loop
        self._reader = None
        self._writer = None
        self._connected = False

        # dump
        self._dumpfile = file
        self._dumpcount = number
        if self._dumpfile != '':
            with open(self._dumpfile,'w'):
                # create file
                pass

        # send
        self._queue_size = 32
        self._alarms   = asyncio.Queue(maxsize=self._queue_size, loop=self._loop)
        self._commands = asyncio.Queue(maxsize=self._queue_size, loop=self._loop)
        self._data     = asyncio.Queue(maxsize=self._queue_size, loop=self._loop)

        # acks from arduino
        self._dv_alarms   = asyncio.Event(loop=self._loop)
        self._dv_commands = asyncio.Event(loop=self._loop)
        self._dv_data     = asyncio.Event(loop=self._loop)
        # maps between address and queues/events/timeouts 
        self._queues   = {0xC0: self._alarms, 0x80: self._commands, 0x40: self._data}
        self._timeouts = {0xC0: 15, 0x80: 15, 0x40: 15}
        self._acklist  = {0xC0: self._dv_alarms, 0x80: self._dv_commands, 0x40: self._dv_data}
        
        # receive
        self._payloadrecv = asyncio.Queue(maxsize=5)
        # for reducing the rate for use in the lab
        self._packet_count = 0
        self._throttle = throttle

        # packet counting
        self._sequence_send    = 0
        self.resetReceiver(0)

    async def main(self, device, baudrate):
        try:
            self._reader, self._writer = await serial_asyncio.open_serial_connection(url=device, baudrate=baudrate, timeout = 2, dsrdtr = True)
            self._connected = True
            while self._connected:
                sendAlarm = self.send(0xC0)
                sendCmd = self.send(0x80)
                sendData = self.send(0x40)
                receiver = self.recv()
                await asyncio.gather(*[receiver, sendCmd, sendAlarm, sendData], return_exceptions=True)
        except Exception:
            raise

    async def send(self, address):
        queue = self._queues[address]
        while self._connected:
            logging.debug("Waiting for Command")
            packet = await queue.get()
            packet.setSequenceSend(self._sequence_send)
            for send_attempt in range(10):
                # try to send the packet 10 times
                try:
                    await self.sendPacket(packet)
                    await asyncio.wait_for(self._acklist[address].wait(), timeout=self._timeouts[address] / 1000)
                    self._acklist[address].clear()
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
                7: generateData,
                8: generateData,
                9: generateData,
                10:generateData,
                11:generateData,
                12:generateData,
                13:generateData
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
                7: qlist[2],
                8: qlist[2],
                9: qlist[2],
                10:qlist[2],
                11:qlist[2],
                12:qlist[2],
                13:qlist[2]
            }
            queue = PAYLOAD_TYPE_TO_QUEUE[payload.getType()]
            queue.put_nowait(tmp_comms)

            return True
        except KeyError:
            return False
        except asyncio.queues.QueueFull:
            try:
                queue.get_nowait()
                queue.task_done()
                queue.put_nowait(tmp_comms)
            except Exception as e:
                logging.error(e)
                return False
            else:
                return True

    async def sendPacket(self, packet):
        if isinstance(packet, CommsACK):
            # don't log acks
            logging.debug(f"Sending ACK: {binascii.hexlify(packet.encode())}")
            pass
        elif isinstance(packet, CommsNACK):
#             logging.debug(f"Sending NACK: {binascii.hexlify(packet.encode())}")
            pass
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

    def finishPacket(self, address, sequence_received):
        try:
            sequence = (self._sequence_send + 1) % 128
            if sequence == sequence_received:
                self._queues[address].task_done()
                self._sequence_send = sequence
        except ValueError:
            # task has already been purged from queue
            pass
        else:
            self._acklist[address].set()
            
    def resetReceiver(self, sequence_receive = -1):
        self._mismatch_counter = 0
        if sequence_receive >= 0:
            self._sequence_receive = sequence_receive
            
    def trackMismatch(self, sequence_receive):
        if self._mismatch_counter > 20 :
            self.resetReceiver(sequence_receive)
            logging.warning(f"Received more than 20 sequence_receive mismatches, resetting")
        else:
            self._mismatch_counter += 1

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
                    self.finishPacket(packet.address, packet.sequence_receive)
                else:
                    logging.info("Received NACK")
            else:
                # packet should contain valid data
                try:
                    payload = PayloadFormat.fromByteArray(packet.byteArray)
                    
                    self.sequence_receive = packet.sequence_send
                    self.resetReceiver()
                    self.payloadrecv = payload
#                     logging.debug(f"Received payload type {payload.getType()} for timestamp {payload.timestamp}")
                    comms_response = CommsACK(packet.address)
                except (StructError, ValueError):
                    # invalid payload, but valid checksum - this is bad!
                    logging.error(f"Invalid payload: {payload}")
                    # restart/reflash/swap to redundant microcontroller?
                    comms_response = CommsNACK(packet.address)
                except SequenceReceiveMismatch:
#                     logging.debug(f"Mismatch sequence receive, expected: {self.sequence_receive}; received: {packet.sequence_send}")
                    comms_response = CommsNACK(packet.address)
                    self.trackMismatch(packet.sequence_send)
                except HEVVersionError as e:
                    logging.critical(f"HEVVersionError: {e}")
                    exit(1)
                finally:
                    comms_response.setSequenceReceive(self.sequence_receive)
                    await self.sendPacket(comms_response)

    @property
    def sequence_receive(self):
        return self._sequence_receive
    
    @sequence_receive.setter
    def sequence_receive(self, sequence):
        if self._sequence_receive == sequence:
            self._sequence_receive = (self._sequence_receive + 1) % 128
        else:
            raise SequenceReceiveMismatch
                    
    @property
    def payloadrecv(self):
        return self._payloadrecv

    @payloadrecv.setter
    def payloadrecv(self, payload):
        if self._throttle > 0:
            if self._packet_count % self._throttle == 0:
                self._payloadrecv.put_nowait(payload)

        self._packet_count += 1
        
        if self._dumpfile != '':
            with open(self._dumpfile, 'a') as f:
                # dump the payload in a dict which can be unpacked directly into a payloadFormat object
                f.write(f"{binascii.hexlify(payload.byteArray)}\n")
            if self._packet_count >= self._dumpcount:
                logging.critical(f"Dump count reached. {self._packet_count} packets dumped to file {self._dumpfile}")
                exit(0)
    

if __name__ == "__main__":
    try:
        # schedule async tasks
        loop = asyncio.get_event_loop()
        parser = argparse.ArgumentParser(description='Arguments to run CommsLLI')
        parser.add_argument('--dump', action='store_true', help='Dump raw data to file')
        parser.add_argument('-f', '--file', type=str, default = '', help='File to dump to')
        parser.add_argument('-n', '--number', type=int, default = 10000, help='Number of packets to dump')
        args = parser.parse_args()

        # setup serial devices
        if args.dump:
            if args.file == '':
                logging.critical("No dump file specified")
                raise KeyboardInterrupt # fake ctrl+c
            logging.warning(f"Dumping {args.number} packets to {args.file}")
            comms = CommsLLI(loop, file=args.file, number=args.number)
        else:
            comms = CommsLLI(loop)

        asyncio.gather(comms.main("/dev/ttyUSB0", 115200), return_exceptions=True)
        loop.run_forever()
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        logging.info("Closing LLI")
    finally:
        try:
            loop.close()
        except (RuntimeError, NameError):
            #loop already closed
            pass
