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

    async def update_llipacket(self):
        while True:
            payload = await self._lli._payloadrecv.get()
            global fsm
            #logging.info(f"payload received: {payload}")
            #if payload.getType() == PAYLOAD_TYPE.ALARM.value:
            #    logging.info(f"Alarm: {payload.alarm_code} of priority: {payload.alarm_type}")
        
            if payload.getType() == PAYLOAD_TYPE.DATA.value:
                #logging.info(f"payload received: {payload}")
                #logging.info(f"payload received: {payload.timestamp}") 
                #logging.info(f"Fsm state: {payload.fsm_state}")
                fsm = payload.fsm_state
            #if payload.getType() == PAYLOAD_TYPE.IVT.value:
            #    logging.info(f"payload received:  {payload} ")
                #logging.info(f"IV: air {payload.air_in_current:.3f} o2 {payload.o2_in_current:.3f} purge {payload.purge_current:.3f} inhale {payload.inhale_current:.3f} exhale {payload.exhale_current:.3f} fsm {fsm} ")
            #logging.info(f"payload received: {payload}")
            #if hasattr(payload, 'inhale_exhale_ratio'):
            #    logging.info(f"payload received: inhale exhale ratio = {payload.inhale_exhale_ratio} ")
            #if payload.getType() == PAYLOAD_TYPE.CYCLE.value:
            #   logging.info(f"payload received:  {payload} ")
            #if payload.getType() == PAYLOAD_TYPE.READBACK.value:
            #    logging.info(f"payload received:  {payload} {fsm}")
            if payload.getType() == PAYLOAD_TYPE.DEBUG.value:
                logging.info(f" PID {payload.kp:3.6f} {payload.ki:3.6f} {payload.kd:3.6f} {payload.proportional:3.6f} {payload.integral:3.6f} {payload.derivative:3.6f} {payload.valve_duty_cycle:3.6f} {payload.target_pressure:3.6f} {payload.process_pressure:3.6f} fsm {fsm}")
            #if payload.getType() == PAYLOAD_TYPE.PERSONAL.value:
            #   logging.info(f"payload received:  {payload} ")
            #if payload.getType() == PAYLOAD_TYPE.LOGMSG.value:
            #    logging.info(f"LOGMSG {payload.timestamp}:{payload.message} {fsm}") 
            #if payload.getType() == PAYLOAD_TYPE.TARGET.value:
            #    logging.info(f"TARGET {payload} {fsm}") 
            #if payload.getType() == PAYLOAD_TYPE.CMD.value:
            #    logging.info(f"CMD (alarm threshold) {payload} {fsm}") 
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

def send_personal(name, age, sex, height, weight):
    try:
        cmd = PersonalFormat(name=name.encode(), age=int(age), sex=sex.encode(), height=int(height), weight=int(weight))
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
  #  # Change TIMEOUT of breathing cycle (BUFF-PRE-INHALE)
    await asyncio.sleep(1)
    #print('get personal info')
    #send_cmd(cmd_type="GENERAL", cmd_code="GET_PERSONAL")

    #await asyncio.sleep(10)
    #print('send personal info')
    #send_personal("Jessica Jones", 29, 'F', 175, 58)

    send_cmd(cmd_type="GET_THRESHOLD_MAX", cmd_code="APNEA")
    await asyncio.sleep(1)
    print('set apnea max 10')
    send_cmd(cmd_type="SET_THRESHOLD_MAX", cmd_code="APNEA", param=10)
    send_cmd(cmd_type="SET_PID", cmd_code="KP", param=0.0015)
    send_cmd(cmd_type="SET_PID", cmd_code="KI", param=0.0016)
    send_cmd(cmd_type="SET_PID", cmd_code="KD", param=0.0017)
    #print('get targets pcac, current')
    #send_cmd(cmd_type="GET_TARGETS", cmd_code="PC_AC", param=0)
    #send_cmd(cmd_type="GET_TARGETS", cmd_code="TEST", param=0)
    #send_cmd(cmd_type="GET_TARGETS", cmd_code="CURRENT", param=0)
    #await asyncio.sleep(1)
    #print('set pcac rr=10, t_inh=1110')
    #send_cmd(cmd_type="SET_TARGET_PC_AC", cmd_code="RESPIRATORY_RATE", param=10.0) 
    #send_cmd(cmd_type="SET_TARGET_PC_AC", cmd_code="INHALE_TIME", param=1110) 
    #print('set curr rr=11 ')
    #send_cmd(cmd_type="SET_TARGET_CURRENT", cmd_code="RESPIRATORY_RATE", param=11.0) 

    #await asyncio.sleep(1)
    #print('get targets pcac, current')
    #send_cmd(cmd_type="GET_TARGETS", cmd_code="PC_AC", param=0)
    #send_cmd(cmd_type="GET_TARGETS", cmd_code="TEST", param=0)
    #send_cmd(cmd_type="GET_TARGETS", cmd_code="CURRENT", param=0)
    #await asyncio.sleep(1)
    #print('change mode to pcac')
    #send_cmd(cmd_type="SET_MODE", cmd_code="PC_AC", param=0)
    #await asyncio.sleep(1)
    #print('get targets pcac, current')
    #send_cmd(cmd_type="GET_TARGETS", cmd_code="PC_AC", param=0)
    #send_cmd(cmd_type="GET_TARGETS", cmd_code="TEST", param=0)
    #send_cmd(cmd_type="GET_TARGETS", cmd_code="CURRENT", param=0)

    await asyncio.sleep(1)

    send_cmd(cmd_type="SET_TARGET_CURRENT", cmd_code="PID_GAIN", param=2.3) 
    #send_cmd(cmd_type="SET_TARGET_CURRENT", cmd_code="INHALE_TIME", param=1.220) 
    #send_cmd(cmd_type="SET_TARGET_CURRENT", cmd_code="INSPIRATORY_PRESSURE", param=25)
    #await asyncio.sleep(1)
    #print('get all targets pcac')
    #send_cmd(cmd_type="GET_TARGETS", cmd_code="PC_AC", param=0)
    #send_cmd(cmd_type="GET_TARGETS", cmd_code="PC_PSV", param=0)
    #send_cmd(cmd_type="GET_TARGETS", cmd_code="PC_AC_PRVC", param=0)
    #send_cmd(cmd_type="GET_TARGETS", cmd_code="CPAP", param=0)
    #send_cmd(cmd_type="GET_TARGETS", cmd_code="TEST", param=0)
    #send_cmd(cmd_type="GET_TARGETS", cmd_code="CURRENT", param=0)
    ##cmd = send_cmd(cmd_type="GENERAL", cmd_code="START", param=0) 
    #print('send start')
    #print('sent inhale + exhale trigger -> 1')
    while True:
        await asyncio.sleep(1)
        print("get targets")
        send_cmd(cmd_type="GET_TARGETS", cmd_code="PC_AC", param=0)
        send_cmd(cmd_type="GET_TARGETS", cmd_code="PC_PSV", param=0)
        send_cmd(cmd_type="GET_TARGETS", cmd_code="PC_AC_PRVC", param=0)
        send_cmd(cmd_type="GET_TARGETS", cmd_code="CPAP", param=0)
        send_cmd(cmd_type="GET_TARGETS", cmd_code="TEST", param=0)
        send_cmd(cmd_type="GET_TARGETS", cmd_code="CURRENT", param=0)

        #send_cmd(cmd_type="GENERAL", cmd_code="STANDBY", param=0)

        print('sent cmd get targets')

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
