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


class Dependant(object):
    def __init__(self, lli):
        self._llipacket = None
        self._lli = lli
        self._lli.bind_to(self.update_llipacket)

    def update_llipacket(self, payload):
        #logging.info(f"payload received: {payload}")
        if payload.getType() == PAYLOAD_TYPE.ALARM.value:
            logging.info(f"Alarm: {payload.alarm_code} of priority: {payload.alarm_type}")
        if payload.getType() == PAYLOAD_TYPE.DATA.value:
        #if payload.getType() == 1:
            logging.info(f"payload received: {payload}")
            #logging.info(f"Fsm state: {payload.fsm_state}")
        if payload.getType() == 8:
            logging.info(f"IV: {payload.air_in_current:.3f} {payload.o2_in_current:.3f} {payload.purge_current:.3f} {payload.inhale_current:.3f} {payload.exhale_current:.3f} ")
        #logging.info(f"payload received: {payload}")
        #if hasattr(payload, 'ventilation_mode'):
        #    logging.info(f"payload received: {payload.ventilation_mode}")
        #if hasattr(payload, 'duration_inhale'):
        #    logging.info(f"payload received: inhale duration = {payload.duration_inhale} ")
        #if hasattr(payload, 'inhale_exhale_ratio'):
        #    logging.info(f"payload received: inhale exhale ratio = {payload.inhale_exhale_ratio} ")
        #    logging.info(f"payload received: peep = {payload.peep} ")
        #    logging.info(f"payload received: valve air in = {payload.valve_air_in} ")
        #if hasattr(payload, 'respiratory_rate'):
        #    logging.info(f"payload received: RR = {payload.respiratory_rate} ")
            #print(binascii.hexlify(payload._byteArray))
        self._llipacket = payload.getDict() # returns a dict


# initialise as start command, automatically executes toByteArray()
async def commsDebug():
#     cmd = CommandFormat(cmd_type=CMD_TYPE.GENERAL.value, cmd_code=CMD_GENERAL.STOP.value, param=0)
    await asyncio.sleep(1)
    cmd = CommandFormat(cmd_type=CMD_TYPE.GENERAL.value, cmd_code=CMD_GENERAL.START.value, param=0)
    comms.writePayload(cmd)
    print('sent cmd start')
    toggle = 2
    while True:
        # alarm testing
        await asyncio.sleep(5)
        cmd = CommandFormat(cmd_type=CMD_TYPE.SET_THRESHOLD_MAX.value, cmd_code=ALARM_CODES.APNEA.value, param=-10)
        comms.writePayload(cmd)
        await asyncio.sleep(15)
        #cmd = CommandFormat(cmd_type=CMD_TYPE.SET_PID.value, cmd_code=CMD_SET_PID.KP.value, param=200) # to set Kp=0.2, param=200 i.e., milli_Kp
        #comms.writePayload(cmd)
        #print('sent cmd set Kp = 0.2')
        cmd = CommandFormat(cmd_type=CMD_TYPE.SET_TIMEOUT.value, cmd_code=CMD_SET_TIMEOUT.INHALE.value, param=1010)
        comms.writePayload(cmd)
        await asyncio.sleep(15)
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
