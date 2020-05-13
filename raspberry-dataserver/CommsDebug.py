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
        #logging.info(f"payload received: {payload}")
        if payload.getType() == 1:
            logging.info(f"payload received: {payload}")
            #logging.info(f"Fsm state: {payload.fsm_state} ")
        #if payload.getType() == PAYLOAD_TYPE.ALARM.value:
        #    logging.info(f"Alarm: {payload.alarm_code} of priority: {payload.alarm_type}")
        
        if payload.getType() == PAYLOAD_TYPE.DATA.value:
            #logging.info(f"payload received: {payload}")
            #logging.info(f"payload received: {payload.timestamp} pc {payload.flow:3.6f} dc {payload.volume:3.6f} fsm {payload.fsm_state}")
            #logging.info(f"Fsm state: {payload.fsm_state}")
            fsm = payload.fsm_state
        #if payload.getType() == PAYLOAD_TYPE.IVT.value:
        #    logging.info(f"IV: air {payload.air_in_current:.3f} o2 {payload.o2_in_current:.3f} purge {payload.purge_current:.3f} inhale {payload.inhale_current:.3f} exhale {payload.exhale_current:.3f} fsm {fsm} ")
        #logging.info(f"payload received: {payload}")
        #if hasattr(payload, 'inhale_exhale_ratio'):
        #    logging.info(f"payload received: inhale exhale ratio = {payload.inhale_exhale_ratio} ")
        if payload.getType() == PAYLOAD_TYPE.DEBUG.value:
            logging.info(f" PID {payload.kp:3.6f} {payload.ki:3.6f} {payload.kd:3.6f} {payload.proportional:3.6f} {payload.integral:3.6f} {payload.derivative:3.6f} {payload.valve_duty_cycle:3.6f} {payload.target_pressure:3.6f} {payload.process_pressure:3.6f} fsm {fsm}")
        # if payload.getType() == PAYLOAD_TYPE.LOGMSG.value:
        #     logging.info(f"LOGMSG {payload.message} ") 
        #if hasattr(payload, 'ventilation_mode'):
        #    logging.info(f"payload received: {payload.ventilation_mode}")
        #if hasattr(payload, 'duration_inhale'):
        #    logging.info(f"payload received: inhale duration = {payload.duration_inhale} ")
        self._llipacket = payload.getDict() # returns a dict


# initialise as start command, automatically executes toByteArray()
async def commsDebug():
    #cmd = CommandFormat(cmd_type=CMD_TYPE.GENERAL.value, cmd_code=CMD_GENERAL.START.value, param=0)
    #cmd = CommandFormat(cmd_type=CMD_TYPE.SET_TIMEOUT.value, cmd_code=CMD_SET_TIMEOUT.INHALE.value, param=1000)
    #comms.writePayload(cmd)

    await asyncio.sleep(5)
    await asyncio.sleep(1)
    cmd = CommandFormat(cmd_type=CMD_TYPE.SET_PID.value, cmd_code=CMD_SET_PID.KP.value, param=0.002)#0.0108/5) # 108/4) # to set Kp=0.0002, param=200 i.e., micro_Kp
    comms.writePayload(cmd)
    await asyncio.sleep(1)
    cmd = CommandFormat(cmd_type=CMD_TYPE.SET_PID.value, cmd_code=CMD_SET_PID.KI.value, param=0.0006)#0.00162*0.4)#0.0054/2) # 0004)#0002) # to set Kp=0.0002, param=200 i.e., micro_Kp
    comms.writePayload(cmd)
    await asyncio.sleep(1)
    cmd = CommandFormat(cmd_type=CMD_TYPE.SET_PID.value, cmd_code=CMD_SET_PID.KD.value, param=0.0)#0.00162*1.5)#0.0054/2) # to set Kp=0.0002, param=200 i.e., micro_Kp
    comms.writePayload(cmd)
    await asyncio.sleep(1)
    cmd = CommandFormat(cmd_type=CMD_TYPE.SET_PID.value, cmd_code=CMD_SET_PID.TARGET_FINAL_PRESSURE.value, param=10.0) # to set Kp=0.0002, param=200 i.e., micro_Kp
    comms.writePayload(cmd)
    await asyncio.sleep(1)
    cmd = CommandFormat(cmd_type=CMD_TYPE.SET_PID.value, cmd_code=CMD_SET_PID.NSTEPS.value, param=3) # to set Kp=0.0002, param=200 i.e., micro_Kp
    comms.writePayload(cmd)
    await asyncio.sleep(1)
    # Enable inhale trigger
    cmd = CommandFormat(cmd_type=CMD_TYPE.SET_VALVE.value, cmd_code=CMD_SET_VALVE.INHALE_TRIGGER_ENABLE.value, param=1.) # to set Kp=0.0002, param=200 i.e., micro_Kp
    comms.writePayload(cmd)
    await asyncio.sleep(1)
    # Enable exhale trigger
    cmd = CommandFormat(cmd_type=CMD_TYPE.SET_VALVE.value, cmd_code=CMD_SET_VALVE.EXHALE_TRIGGER_ENABLE.value, param=1.) # to set Kp=0.0002, param=200 i.e., micro_Kp
    comms.writePayload(cmd)
    await asyncio.sleep(1)
    # Change TIMEOUT of breathing cycle (INHALE)
    cmd = CommandFormat(cmd_type=CMD_TYPE.SET_TIMEOUT.value, cmd_code=CMD_SET_TIMEOUT.INHALE.value, param=30000.) # to set Kp=0.0002, param=200 i.e., micro_Kp
    comms.writePayload(cmd)
    await asyncio.sleep(1)
    # Change TIMEOUT of breathing cycle (INHALE)
    cmd = CommandFormat(cmd_type=CMD_TYPE.SET_TIMEOUT.value, cmd_code=CMD_SET_TIMEOUT.EXHALE_FILL.value, param=1600.) # to set Kp=0.0002, param=200 i.e., micro_Kp
    comms.writePayload(cmd)
    await asyncio.sleep(1)
    # Change TIMEOUT of breathing cycle (INHALE)
    cmd = CommandFormat(cmd_type=CMD_TYPE.SET_TIMEOUT.value, cmd_code=CMD_SET_TIMEOUT.EXHALE.value, param=20000.) # to set Kp=0.0002, param=200 i.e., micro_Kp
    comms.writePayload(cmd)
    await asyncio.sleep(1)
    # Start the cycles
    cmd = CommandFormat(cmd_type=CMD_TYPE.GENERAL.value, cmd_code=CMD_GENERAL.START.value, param=0)
    comms.writePayload(cmd)
    print('sent cmd start')
    #await asyncio.sleep(1)
    #cmd = CommandFormat(cmd_type=CMD_TYPE.SET_VALVE.value, cmd_code=CMD_SET_VALVE.INHALE_TRIGGER_ENABLE.value, param=1) 
    #comms.writePayload(cmd)
    #cmd = CommandFormat(cmd_type=CMD_TYPE.SET_VALVE.value, cmd_code=CMD_SET_VALVE.EXHALE_TRIGGER_ENABLE.value, param=1) 
    #comms.writePayload(cmd)
    #print('sent inhale + exhale trigger -> 1')
    toggle = 2
    while True:
        await asyncio.sleep(300)
        #cmd = CommandFormat(cmd_type=CMD_TYPE.SET_PID.value, cmd_code=CMD_SET_PID.KP.value, param=5) # to set Kp=0.2, param=200 i.e., milli_Kp
        #comms.writePayload(cmd)
        #print('sent cmd set Kp = 0.2')
        await asyncio.sleep(300)
        cmd = CommandFormat(cmd_type=CMD_TYPE.GENERAL.value, cmd_code=toggle, param=0)
        if toggle == 2 :
            toggle = 1
        else : 
            toggle = 2

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
