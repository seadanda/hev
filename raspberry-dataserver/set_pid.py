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

    async def update_llipacket(self):
        while True:
            payload = await self._lli._payloadrecv.get()
            global fsm
            #logging.info(f"payload received: {payload}")
            #if payload.getType() == PAYLOAD_TYPE.ALARM.value:
            #    logging.info(f"Alarm: {payload.alarm_code} of priority: {payload.alarm_type}")
        
            if payload.getType() == PAYLOAD_TYPE.DATA.value:
                #logging.info(f"payload received: {payload}")
                fsm = payload.fsm_state
            if payload.getType() == PAYLOAD_TYPE.READBACK.value:
                logging.info(f"PID:  kp {payload.kp} ki  {payload.ki} kd {payload.kd} ")
            if payload.getType() == PAYLOAD_TYPE.TARGET.value:
                logging.info(f"GAIN: {payload.pid_gain} ") 
            self._llipacket = payload.getDict() # returns a dict

def send_cmd(cmd_type, cmd_code, param=0.0):
    try:
        cmd = CommandFormat(cmd_type=CMD_TYPE[cmd_type].value, cmd_code=CMD_MAP[cmd_type].value[cmd_code].value, param=param)
        comms.writePayload(cmd)
    except Exception as e:
        logging.critical(e)
        exit(1)
    else:
        return cmd

def send_personal(name, patient_id, age, sex, height, weight):
    try:
        cmd = PersonalFormat(name=name.encode(), patient_id=patient_id.encode(), age=int(age), sex=sex.encode(), height=int(height), weight=int(weight))
        logging.info(f' payload sent {cmd}')
        comms.writePayload(cmd)
    except Exception as e:
        logging.critical(e)
        exit(1)
    else:
        return cmd

# initialise as start command, automatically executes toByteArray()
async def commsDebug():
    await asyncio.sleep(1)
    send_cmd(cmd_type="SET_PID", cmd_code="KP", param=0.001)
    send_cmd(cmd_type="SET_PID", cmd_code="KI", param=0.0005)
    send_cmd(cmd_type="SET_PID", cmd_code="KD", param=0.001)
    send_cmd(cmd_type="SET_TARGET_CURRENT", cmd_code="PID_GAIN", param=2.) 
    while True:
        await asyncio.sleep(1)

try:
    # setup serial device and init server
    loop = asyncio.get_event_loop()
    comms = CommsLLI(loop)
    dep = Dependant(comms)
    deppoll = dep.update_llipacket()

    # create tasks
    lli = comms.main(getTTYPort(), 115200)
    debug = commsDebug()
    tasks = [lli, debug, deppoll]

    # run tasks
    asyncio.gather(*tasks, return_exceptions=True)
    loop.run_forever()
except asyncio.CancelledError:
    pass
except KeyboardInterrupt:
    logging.info("Closing LLI")

finally:
    loop.close()
