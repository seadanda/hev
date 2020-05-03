#!/usr/bin/env python3
from CommsControl import CommsControl
from CommsCommon import *
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from serial.tools import list_ports
import sys
import time

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
comms = CommsControl(port = port_device)


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
        #logging.info(f"payload received: {payload.timestamp}")
        if hasattr(payload, 'fsm_state'):
            logging.info(f"payload received: {payload.fsm_state}")
        if hasattr(payload, 'duration_inhale'):
            logging.info(f"payload received: inhale duration = {payload.duration_inhale} ")
        self._llipacket = payload.getDict() # returns a dict
        # pop from queue - protects against Dependant going down and not receiving packets
        self._lli.pop_payloadrecv()

dep = Dependant(comms)

# initialise as start command, automatically executes toByteArray()
#cmd = CommandFormat(cmd_type=CMD_TYPE.GENERAL.value, cmd_code=CMD_GENERAL.START.value, param=0)
#cmd = CommandFormat(cmd_type=CMD_TYPE.SET_TIMEOUT.value, cmd_code=CMD_SET_TIMEOUT.INHALE.value, param=1111)
time.sleep(4)
cmd = CommandFormat(cmd_type=CMD_TYPE.GENERAL.value, cmd_code=CMD_GENERAL.START.value, param=0)
comms.writePayload(cmd)
print('sent cmd purge')
cmd = CommandFormat(cmd_type=CMD_TYPE.SET_MODE.value, cmd_code=VENTILATION_MODE.LAB_MODE_PURGE.value, param=0)
comms.writePayload(cmd)
print('sent cmd set inhale duration 1111')
while True:
    time.sleep(30)
    cmd.cmd_code = CMD_GENERAL.STOP.value # automatically executes toByteArray()
    comms.writePayload(cmd)
    print('sent cmd stop')
    pass

