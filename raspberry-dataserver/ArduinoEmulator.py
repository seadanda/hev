#!/usr/bin/env python3

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
            while True:
                with open(self._dumpfile,'r') as f:
                    for line in f:
                        # snip off the b''\n surrounding the hexstring
                        payload = PayloadFormat.fromByteArray(binascii.unhexlify(line[2:-2]))
                        if not self._lli.writePayload(payload):
                            logging.error(f"Failed to send payload: {payload}")
                        await asyncio.sleep(0.02)
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
        # set up and link interfaces
        logging.debug("Setting up devices")
        socat = Popen(f"/usr/bin/env socat -d -d pty,rawer,echo=0,link={str(Path.home())}/hev-sw/ttyEMU0 pty,rawer,echo=0,link={str(Path.home())}/hev-sw/ttyEMU1".split())
        time.sleep(2)
        logging.info("Setting up devices [DONE]")

        # schedule async tasks
        loop = asyncio.get_event_loop()

        parser = argparse.ArgumentParser(description='Arguments to run hevserver')
        parser.add_argument('-f', '--file', type=str, default = os.path.dirname(__file__)+'/share/dump.dump', help='File to load from')
        args = parser.parse_args()

        # setup serial devices
        logging.info(f"Using file {args.file}")
        comms = CommsLLI(loop)
        emulator = ArduinoEmulator(lli=comms, dumpfile=args.file)

        # queue tasks
        lli = comms.main(str(Path.home())+'/hev-sw/ttyEMU1', 115200)
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
