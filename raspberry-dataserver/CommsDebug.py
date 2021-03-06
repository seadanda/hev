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
                logging.info(f"payload received: {payload.timestamp} pc {payload.flow:3.6f} dc {payload.flow_calc:3.6f} fsm {payload.fsm_state}")
            #    #logging.info(f"payload received: {payload.timestamp} pc {payload.flow:3.6f} dc {payload.volume:3.6f} fsm {payload.fsm_state}")
            #    #logging.info(f"payload received: {payload.pressure_buffer:3.6f}  fsm {payload.fsm_state}")
            #    #logging.info(f"Fsm state: {payload.fsm_state}")
            #    fsm = payload.fsm_state
            #if payload.getType() == PAYLOAD_TYPE.IVT.value:
            #    logging.info(f"payload received:  {payload} ")
                #logging.info(f"IV: air {payload.air_in_current:.3f} o2 {payload.o2_in_current:.3f} purge {payload.purge_current:.3f} inhale {payload.inhale_current:.3f} exhale {payload.exhale_current:.3f} fsm {fsm} ")
            #logging.info(f"payload received: {payload}")
            #if hasattr(payload, 'inhale_exhale_ratio'):
            #    logging.info(f"payload received: inhale exhale ratio = {payload.inhale_exhale_ratio} ")
            #if payload.getType() == PAYLOAD_TYPE.CYCLE.value:
            #   logging.info(f"payload received:  {payload} ")
            #if payload.getType() == PAYLOAD_TYPE.LOOP_STATUS.value:
            #   logging.info(f"payload received:  {payload} ")
            #if payload.getType() == PAYLOAD_TYPE.READBACK.value:
            #    #logging.info(f"payload received:  {payload} ")
            #    logging.info(f" READBACK PID {payload.kp:3.6f} {payload.ki:3.6f} {payload.kd:3.6f} ")
            #if payload.getType() == PAYLOAD_TYPE.DEBUG.value:
                #logging.info(f" PID {payload.kp:3.6f} {payload.ki:3.6f} {payload.kd:3.6f} {payload.proportional:3.6f} {payload.integral:3.6f} {payload.derivative:3.6f} {payload.valve_duty_cycle:3.6f} {payload.target_pressure:3.6f} {payload.process_pressure:3.6f} fsm {fsm}")
            #    logging.info(f" DEBUG PID {payload.kp:3.6f} {payload.ki:3.6f} {payload.kd:3.6f} ")
            #if payload.getType() == PAYLOAD_TYPE.LOGMSG.value:
            #    logging.info(f"LOGMSG {payload.timestamp}:{payload.message} {fsm}") 
            #if payload.getType() == PAYLOAD_TYPE.TARGET.value:
            #    logging.info(f"LOGMSG {payload} {fsm}") 
            #if hasattr(payload, 'ventilation_mode'):
            #    logging.info(f"payload received: {payload.ventilation_mode}")
            #if hasattr(payload, 'duration_inhale'):
            #    logging.info(f"payload received: inhale duration = {payload.duration_inhale} ")
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

# initialise as start command, automatically executes toByteArray()
async def commsDebug():
    send_cmd(cmd_type="GET_TARGETS", cmd_code="TEST", param=0)
    send_cmd(cmd_type="GET_TARGETS", cmd_code="PC_AC", param=0)
    send_cmd(cmd_type="SET_MODE", cmd_code="TEST", param=0)

    #send_cmd(cmd_type="SET_PID", cmd_code="KP", param=0.001)#
    #send_cmd(cmd_type="SET_PID", cmd_code="KI", param=0.0003)#5)# 0.0005
    #send_cmd(cmd_type="SET_PID", cmd_code="KD", param=0.)#01)# 0.001
    #await asyncio.sleep(1)
    send_cmd(cmd_type="SET_PID", cmd_code="KP", param=0.001)#
    send_cmd(cmd_type="SET_PID", cmd_code="KI", param=0.0005)#5)# 0.0005
    send_cmd(cmd_type="SET_PID", cmd_code="KD", param=0.001)#01)# 0.001
    #send_cmd(cmd_type="SET_TARGET_CURRENT", cmd_code="PID_GAIN", param=2) 
    #send_cmd(cmd_type="GET_TARGETS", cmd_code="TEST", param=0)
    send_cmd(cmd_type="SET_PID", cmd_code="NSTEPS", param=3) # 
    
  #  # Change TIMEOUT of breathing cycle (BUFF-PRE-INHALE)
    send_cmd(cmd_type="SET_DURATION", cmd_code="BUFF_PRE_INHALE", param=10.) # 
    send_cmd(cmd_type="SET_DURATION", cmd_code="PAUSE", param=10.) #

    send_cmd(cmd_type="SET_TARGET_CURRENT", cmd_code="RESPIRATORY_RATE", param=5.0) 
    send_cmd(cmd_type="SET_TARGET_CURRENT", cmd_code="INHALE_TIME", param=1.0)   # changed to seconds
    send_cmd(cmd_type="SET_TARGET_CURRENT", cmd_code="INSPIRATORY_PRESSURE", param=15)#
    send_cmd(cmd_type="SET_TARGET_CURRENT", cmd_code="INHALE_TRIGGER_THRESHOLD", param=0.05) # 
    send_cmd(cmd_type="SET_TARGET_CURRENT", cmd_code="EXHALE_TRIGGER_THRESHOLD", param=0.25) # 

    #await asyncio.sleep(1)
    send_cmd(cmd_type="SET_VALVE", cmd_code="INHALE_OPEN_MIN", param=0.53) 

    ### NOTE : THESE ARE FOR TESTING ONLY, AS THEY OVERRIDE THE VALUES SET BY THE VENTILATION MODE
    send_cmd(cmd_type="SET_TARGET_CURRENT", cmd_code="INHALE_TRIGGER_ENABLE", param=0) 
    send_cmd(cmd_type="SET_TARGET_CURRENT", cmd_code="EXHALE_TRIGGER_ENABLE", param=0) 
    send_cmd(cmd_type="SET_TARGET_CURRENT", cmd_code="VOLUME_TRIGGER_ENABLE", param=0) 

    send_cmd(cmd_type="SET_VALVE", cmd_code="AIR_IN_ENABLE", param=1) 
    send_cmd(cmd_type="SET_VALVE", cmd_code="O2_IN_ENABLE", param=1) 

    print('sent cmd start')
    send_cmd(cmd_type="GENERAL", cmd_code="START", param=1000) 

    toggle = "STOP"
    while True:
        await asyncio.sleep(300)
        await asyncio.sleep(300)
        send_cmd(cmd_type="GENERAL", cmd_code=toggle, param=0)
        if toggle == "STOP" :
            toggle = "START"
        else : 
            toggle = "STOP"

        print('sent cmd stop')

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
