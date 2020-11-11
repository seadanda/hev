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
import logging
import time
import argparse
import os
import binascii
from pathlib import Path
from subprocess import Popen
from CommsLLI import CommsLLI
from CommsCommon import PayloadFormat, HEVVersionError

# Set up logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.WARNING)

class ArduinoEmulator:
    def __init__(self, lli, dumpfile=os.path.dirname(__file__)+'/share/dump.dump'):
        self._lli = lli
        self._dumpfile = dumpfile

    async def generator(self):
        try:
            epochtime = 0 # make timestamps sequential through looped files
            while True:
                with open(self._dumpfile,'r') as f:
                    delay = 10 # ms
                    line = f.readline() # peek at first entry to get timestamp
                    prevpayload = PayloadFormat.fromByteArray(binascii.unhexlify(line[2:-2]))
                    prevpayload.timestamp += epochtime
                    i = 0
                    for line in f:
                        await asyncio.sleep(delay / 1000)
                        if not self._lli.writePayload(prevpayload):
                            logging.error(f"Failed to send payload: {prevpayload}")

                        if i == 0:
                            # first line in file is already processed. dump it
                            _ = f.readline()
                            starttime = prevpayload.timestamp # for epochtime calculation

                        payload = PayloadFormat.fromByteArray(binascii.unhexlify(line[2:-2]))
                        payload.timestamp += epochtime
                        delay = payload.timestamp - prevpayload.timestamp
                        if delay < 0:
                            # because of different priorities, some arrive out of time
                            delay = 0 # so we don't fall behind
                        i += 1
                        prevpayload = payload
                    # send out last packet
                    await asyncio.sleep(delay / 1000)
                    if not self._lli.writePayload(prevpayload):
                        logging.error(f"Failed to send payload: {prevpayload}")
                    epochtime += prevpayload.timestamp - starttime + 10 # add 10ms on for next loop
        except FileNotFoundError:
            logging.critical("File not found")
            exit(1)
        except HEVVersionError as e:
            logging.critical(f"HEVVersionError: {e}")
            exit(1)


    async def receiver(self):
        payload = await self._lli._payloadrecv.get()
        logging.info(f"received packet {payload}")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Arguments to run hevserver')
        parser.add_argument('-f', '--file', type=str, default = os.path.dirname(__file__)+'/share/dump.dump', help='File to load from')
        args = parser.parse_args()

        # set up and link interfaces
        logging.debug("Setting up devices")
        socat = Popen(f"/usr/bin/env socat -d -d pty,rawer,echo=0,link=/dev/shm/ttyEMU0 pty,rawer,echo=0,link=/dev/shm/ttyEMU1".split())
        time.sleep(2)
        logging.info("Setting up devices [DONE]")

        # schedule async tasks
        loop = asyncio.get_event_loop()

        # setup serial devices
        logging.info(f"Using file {args.file}")
        comms = CommsLLI(loop)
        emulator = ArduinoEmulator(lli=comms, dumpfile=args.file)

        # queue tasks
        lli = comms.main('/dev/shm/ttyEMU1', 115200)
        gen = emulator.generator()
        recv = emulator.receiver()
        tasks = [lli, gen, recv]

        # run tasks
        asyncio.gather(*tasks, return_exceptions=True)
        loop.run_forever()
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        logging.info("Closing Emulator")
    finally:
        try:
            socat.kill()
        except NameError:
            pass
        try:
            loop.close()
        except (RuntimeError, NameError):
            #loop already closed
            pass
