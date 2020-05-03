#!/usr/bin/env python3
from CommsLLI import CommsLLI
from CommsCommon import *
import asyncio
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from serial.tools import list_ports
import sys
import time

def getTTYPort():
    port_device = "" 
    for port in list_ports.comports():
        vidpid = ""
        if port.pid != None and port.vid != None:
            vidpid = f"{ port.vid:04x}:{port.pid:04x}".upper()
            print(vidpid)
        if port.manufacturer and "ARDUINO" in port.manufacturer.upper():
            port_device = port.device 
        elif vidpid == "10C4:EA60" :
            port_device = port.device 
        elif len(sys.argv) > 1:
            port_device = sys.argv[1]
    return port_device


class Dependant(object):
    def __init__(self, lli):
        self._llipacket = None
        self._lli = lli
        self._lli.bind_to(self.update_llipacket)

    def update_llipacket(self, payload):
        #logging.info(f"payload received: {payload}")
        if hasattr(payload, 'ventilation_mode'):
            logging.info(f"payload received: {payload.ventilation_mode}")
        #logging.info(f"payload received: {payload.fsm_state}")
        if payload.getType() == 1:
            logging.info(f"Fsm state: {payload.fsm_state}")
        #logging.info(f"payload received: {payload.timestamp}")
        if hasattr(payload, 'duration_inhale'):
            logging.info(f"payload received: inhale duration = {payload.duration_inhale} ")
        self._llipacket = payload.getDict() # returns a dict


# initialise as start command, automatically executes toByteArray()
async def commsDebug():
    #cmd = CommandFormat(cmd_type=CMD_TYPE.GENERAL.value, cmd_code=CMD_GENERAL.START.value, param=0)
    #cmd = CommandFormat(cmd_type=CMD_TYPE.SET_TIMEOUT.value, cmd_code=CMD_SET_TIMEOUT.INHALE.value, param=1111)
    cmd = CommandFormat(cmd_type=CMD_TYPE.GENERAL.value, cmd_code=CMD_GENERAL.START.value, param=0)
    await asyncio.sleep(4)
    comms.writePayload(cmd)
    print('sent cmd start')
    while True:
        await asyncio.sleep(15)
        cmd = CommandFormat(cmd_type=CMD_TYPE.SET_MODE.value, cmd_code=VENTILATION_MODE.LAB_MODE_PURGE.value, param=0)
        comms.writePayload(cmd)
        print('sent cmd purge')
        await asyncio.sleep(15)
        cmd = CommandFormat(cmd_type=CMD_TYPE.GENERAL.value, cmd_code=CMD_GENERAL.STOP.value, param=0)
        comms.writePayload(cmd)
        print('sent cmd stop')

try:
    # setup serial device and init server
    loop = asyncio.get_event_loop()
    comms = CommsLLI(loop)
    dep = Dependant(comms)

    # create tasks
    lli = comms.main(getTTYPort(), 115200)
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
