#!/usr/bin/env python3
from CommsLLI import CommsLLI
from CommsCommon import *
import asyncio
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from serial.tools import list_ports
import sys
import time

import matplotlib.pyplot as plt
import numpy as np
import queue

plt.ion()

history_length = 5000

pressure_buffer = asyncio.Queue(history_length)
pressure_inhale = asyncio.Queue(history_length)
PID_P = asyncio.Queue(history_length)
PID_I = asyncio.Queue(history_length)
PID_D = asyncio.Queue(history_length)

pressure_buffer = asyncio.Queue(history_length)
pressure_inhale = asyncio.Queue(history_length)
PID_P = asyncio.Queue(history_length)
PID_I = asyncio.Queue(history_length)
PID_D = asyncio.Queue(history_length)

fig = plt.figure()

ax = fig.add_subplot(111)

h1, = ax.plot([],[], label="buffer")
h2, = ax.plot([],[], label="inhale")
h3, = ax.plot([],[], label="Proportional")
h4, = ax.plot([],[], label="Integral")
h5, = ax.plot([],[], label="Derivative")
#plt.axes()
#an = []

#for i in range(history_length):
#    pressure_buffer.put(-1)
#    pressure_inhale.put(-1)
#    PID_P.put(-1)
#    PID_I.put(-1)
#    PID_D.put(-1)

last_data = 0
last_build_time = time.time()

async def draw_plots():

    while True:

         #asyncio.sleep(1)

        if(pressure_inhale.qsize() == 0): continue

        print("Running draw plots finished ", pressure_inhale.qsize())

        h1.set_xdata(np.array(range(pressure_inhale.qsize())))
        h1.set_ydata(list(await pressure_inhale.queue.get()))#list(pressure_inhale.queue))

        h2.set_xdata(np.array(range(pressure_buffer.qsize())))
        h2.set_ydata(list(pressure_buffer.queue.get_nowait()))#list(pressure_buffer.queue))

        h3.set_xdata(np.array(range(PID_P.qsize())))
        h3.set_ydata(list(PID_P.queue.get_nowait()))#list(pressure_buffer.queue))

        h4.set_xdata(np.array(range(PID_I.qsize())))
        h4.set_ydata(list(PID_I.queue.get_nowait()))#list(pressure_buffer.queue))

        h5.set_xdata(np.array(range(PID_D.qsize())))
        h5.set_ydata(list(PID_D.queue.get_nowait()))#list(pressure_buffer.queue))

        pressure_inhale.queue.task_done()
        pressure_buffer.queue.task_done()
        PID_D.queue.task_done()
        PID_I.queue.task_done()
        PID_P.queue.task_done()

        plt.legend()
        #plt.ylim(-2,20)

        ax.relim()
        ax.autoscale_view(True,True,True)
        fig.canvas.draw()
        fig.canvas.flush_events()
        #time.sleep(60)
        #time.sleep(0.1)

        #ai, = ax.plot(range(10), range(10))
        #an.append(ai)

        fig.canvas.draw()
        plt.show(block=False)


def FILO(_queue, newitem):
    if _queue.full(): _queue.get_nowait()
    _queue.put_nowait(newitem)

async def build_history_plots():

    """
    2020-05-06 10:45:55,948 - INFO - payload received: DataFormat(version=163, timestamp=231682, payload_type=<PAYLOAD_TYPE.DATA: 1>, fsm_state=<BL_STATES.STOP: 11>, pressure_air_supply=41, pressure_air_regulated=453.0, pressure_o2_supply=30, pressure_o2_regulated=451.0, pressure_buffer=242.0, pressure_inhale=0.0, pressure_patient=0.0, temperature_buffer=659, pressure_diff_patient=1331.0, ambient_pressure=0, ambient_temperature=0, airway_pressure=-0.14404296875, flow=0.0, volume=0.0)
{'version': 163, 'timestamp': 231682, 'payload_type': 'DATA', 'fsm_state': 'STOP', 'pressure_air_supply': 41, 'pressure_air_regulated': 453.0, 'pressure_o2_supply': 30, 'pressure_o2_regulated': 451.0, 'pressure_buffer': 242.0, 'pressure_inhale': 0.0, 'pressure_patient': 0.0, 'temperature_buffer': 659, 'pressure_diff_patient': 1331.0, 'ambient_pressure': 0, 'ambient_temperature': 0, 'airway_pressure': -0.14404296875, 'flow': 0.0, 'volume': 0.0}
0.0
2020-05-06 10:45:55,959 - INFO - payload received: DataFormat(version=163, timestamp=231737, payload_type=<PAYLOAD_TYPE.DATA: 1>, fsm_state=<BL_STATES.STOP: 11>, pressure_air_supply=48, pressure_air_regulated=453.0, pressure_o2_supply=30, pressure_o2_regulated=452.0, pressure_buffer=242.0, pressure_inhale=0.0, pressure_patient=0.0, temperature_buffer=659, pressure_diff_patient=1325.0, ambient_pressure=0, ambient_temperature=0, airway_pressure=-0.14404296875, flow=0.0, volume=0.0)
{'version': 163, 'timestamp': 231737, 'payload_type': 'DATA', 'fsm_state': 'STOP', 'pressure_air_supply': 48, 'pressure_air_regulated': 453.0, 'pressure_o2_supply': 30, 'pressure_o2_regulated': 452.0, 'pressure_buffer': 242.0, 'pressure_inhale': 0.0, 'pressure_patient': 0.0, 'temperature_buffer': 659, 'pressure_diff_patient': 1325.0, 'ambient_pressure': 0, 'ambient_temperature': 0, 'airway_pressure': -0.14404296875, 'flow': 0.0, 'volume': 0.0}
0.0
    """

    print("Starting Build data")

    global last_build_time
    
    while True:

        if time.time() - last_build_time < 0.1 or last_build_time == 0:
            continue

        last_build_time = time.time()

        #if last_data == 0: continue

        try:

            _pressure_inhale = last_data["pressure_inhale"]
            _pressure_buffer = last_data["pressure_buffer"]
            _PID_P = last_data["airway_pressure"]
            _PID_I = last_data["volume"]
            _PID_D = last_data["flow"]

            FILO(pressure_inhale, _pressure_inhale)
            FILO(pressure_buffer, _pressure_buffer)
            FILO(PID_P, _PID_P)
            FILO(PID_I, _PID_I)
            FILO(PID_D, _PID_D)
            print("data acquired")

        except KeyError:
            pass


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
        global last_data
        #logging.info(f"payload received: {payload}")
        if payload.getType() == 1:
            logging.info(f"payload received: {payload}")
            #logging.info(f"Fsm state: {payload.fsm_state}")
        #if hasattr(payload, 'ventilation_mode'):
        #    logging.info(f"payload received: {payload.ventilation_mode}")
        #if hasattr(payload, 'duration_inhale'):
        #    logging.info(f"payload received: inhale duration = {payload.duration_inhale} ")
        self._llipacket = payload.getDict() # returns a dict
        last_data = self._llipacket #= payload.getDict() # returns a dict

        #build_history_plots(payload.getDict())
        #if self.counter % 10 == 0: draw_plots()

# initialise as start command, automatically executes toByteArray()
async def commsDebug():
    #cmd = CommandFormat(cmd_type=CMD_TYPE.GENERAL.value, cmd_code=CMD_GENERAL.START.value, param=0)
    #cmd = CommandFormat(cmd_type=CMD_TYPE.SET_TIMEOUT.value, cmd_code=CMD_SET_TIMEOUT.INHALE.value, param=1111)
    cmd = CommandFormat(cmd_type=CMD_TYPE.GENERAL.value, cmd_code=CMD_GENERAL.START.value, param=0)
    await asyncio.sleep(1)
    comms.writePayload(cmd)
    print('sent cmd start')
    toggle = 2
    while True:
        await asyncio.sleep(15)
        #cmd = CommandFormat(cmd_type=CMD_TYPE.SET_PID.value, cmd_code=CMD_SET_PID.KP.value, param=200) # to set Kp=0.2, param=200 i.e., milli_Kp
        #comms.writePayload(cmd)
        #print('sent cmd set Kp = 0.2')
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
    plot = draw_plots()
    getdata = build_history_plots()
    tasks = [lli, debug, getdata]#, plot]

    # run tasks
    asyncio.gather(*tasks, return_exceptions=True)
    loop.run_forever()
except asyncio.CancelledError:
    pass
except KeyboardInterrupt:
    logging.info("Closing LLI")
finally:
    loop.close()
