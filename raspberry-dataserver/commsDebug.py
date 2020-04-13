#!/usr/bin/env python3
from commsControl import commsControl
from commsConstants import *
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
import sys
import time

comms = commsControl(port = sys.argv[1])


class Dependant(object):
    def __init__(self, lli):
        self._llipacket = None
        self._lli = lli
        self._lli.bind_to(self.update_llipacket)

    def update_llipacket(self, payload):
        # logging.info(f"payload received: {payload}")
        logging.info(f"payload received: {payload._readback_valve_inhale} {payload._readback_valve_exhale} {payload._readback_valve_purge} {payload._fsm_state}")
        self._llipacket = payload.getDict() # returns a dict
        # pop from queue - protects against Dependant going down and not receiving packets
        self._lli.pop_payloadrecv()

dep = Dependant(comms)
start = 0x1
stop =  0x2

cmd = commandFormat()
cmd.cmdCode = start
cmd.toByteArray()

time.sleep(4)
comms.writePayload(cmd)
#comms.sender()
while True:
    # time.sleep(1)
    # cmd.cmdCode = stop
    # cmd.toByteArray()
    # comms.writePayload(cmd)
    #comms.registerData(stop)
    pass

