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
        logging.info(f"payload received: {payload}")
        #logging.info(f"payload received: {payload.fsm_state}")
        #logging.info(f"payload received: {payload.timestamp}")
        #logging.info(f"payload received: {payload.readback_valve_o2_in} {payload.readback_valve_inhale} {payload.readback_valve_exhale} {payload.readback_valve_purge} {payload.fsm_state}")
        self._llipacket = payload.getDict() # returns a dict
        # pop from queue - protects against Dependant going down and not receiving packets
        self._lli.pop_payloadrecv()

dep = Dependant(comms)

# initialise as start command, automatically executes toByteArray()
cmd = CommandFormat(cmd_type=CMD_TYPE.GENERAL.value, cmd_code=CMD_GENERAL.START.value, param=0)
time.sleep(4)
comms.writePayload(cmd)
print('sent cmd start')
while True:
    time.sleep(20)
    cmd.cmd_code = CMD_GENERAL.STOP.value # automatically executes toByteArray()
    comms.writePayload(cmd)
    print('sent cmd stop')
    pass

