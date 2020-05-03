#!/usr/bin/env python3
from CommsLLI import CommsLLI
from CommsCommon import *
import asyncio
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
import sys
import time


class Dependant(object):
    def __init__(self, lli):
        self._llipacket = None
        self._lli = lli
        self._lli.bind_to(self.update_llipacket)

    def update_llipacket(self, payload):
        logging.info(f"payload received: {payload}")
        if payload.getType() == 1:
            logging.info(f"Fsm state: {payload.fsm_state}")
        #logging.info(f"payload received: {payload.timestamp}")
        #logging.info(f"payload received: {payload.readback_valve_o2_in} {payload.readback_valve_inhale} {payload.readback_valve_exhale} {payload.readback_valve_purge} {payload.fsm_state}")
        self._llipacket = payload.getDict() # returns a dict


# initialise as start command, automatically executes toByteArray()
async def commsDebug():
    cmd = CommandFormat(cmd_type=CMD_TYPE.GENERAL.value, cmd_code=CMD_GENERAL.START.value, param=0)
    await asyncio.sleep(4)
    comms.writePayload(cmd)
    print('sent cmd start')
    while True:
        await asyncio.sleep(20)
        cmd.cmd_code = CMD_GENERAL.STOP.value # automatically executes toByteArray()
        comms.writePayload(cmd)
        print('sent cmd stop')

try:
    # setup serial device and init server
    loop = asyncio.get_event_loop()
    comms = CommsLLI(loop)
    dep = Dependant(comms)

    # create tasks
    lli = comms.main(sys.argv[1], 115200)
    debug = commsDebug()
    tasks = [lli, debug]

    # run tasks
    asyncio.gather(*tasks, return_exceptions=True)
    loop.run_forever()
except asyncio.CancelledError:
    pass
except KeyboardInterrupt:
    logging.info("Closing LLI")
finally:
    loop.close()
