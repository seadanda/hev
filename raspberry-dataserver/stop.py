#!/usr/bin/env python3
from CommsLLI import CommsLLI
from CommsCommon import *
import asyncio
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from serial.tools import list_ports
import sys
import time
import binascii

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


fsm=''

class Dependant(object):
    def __init__(self, lli):
        self._llipacket = None
        self._lli = lli
        self._lli.bind_to(self.update_llipacket)

    def update_llipacket(self, payload):
        global fsm
        if payload.getType() == PAYLOAD_TYPE.DATA.value:
            logging.info(f"Fsm state: {payload.fsm_state}")

def send_cmd(cmd_type, cmd_code, param=0.0):
    try:
        cmd = CommandFormat(cmd_type=CMD_TYPE[cmd_type].value, cmd_code=CMD_MAP[cmd_type].value[cmd_code].value, param=param)
        comms.writePayload(cmd)
    except Exception as e:
        logging.critical(e)
        exit(1)
    else:
        return cmd

# initialise as start command, automatically executes toByteArray()
async def commsDebug():

    cmd = send_cmd(cmd_type="GENERAL", cmd_code="STOP", param=0)
    print('sent cmd stop')
    cmd = send_cmd(cmd_type="GENERAL", cmd_code="RESET", param=0)
    print('sent cmd reset')
    await asyncio.sleep(1)
    loop.stop()

try:
    # setup serial device and init server
    loop = asyncio.get_event_loop()
    comms = CommsLLI(loop)
    #dep = Dependant(comms)

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
   
#finally:
#    loop.close()
