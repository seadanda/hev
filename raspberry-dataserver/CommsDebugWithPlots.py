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
from collections import deque


from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint

class LabPlots(QtWidgets.QMainWindow):

    def __init__(self, lli, *args, **kwargs):
        super(LabPlots, self).__init__(*args, **kwargs)

        self._lli = lli
        self.cnt = 0
        self._lli.bind_to(self.update_llipacket)

        history_length = 5000

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.timestamp = list(0 for el in range(history_length))
        self.pressure_buffer = list(0 for el in range(history_length))
        self.pressure_inhale = list(0 for el in range(history_length))
        self.PID_P = list(0 for el in range(history_length))
        self.PID_I = list(0 for el in range(history_length))
        self.PID_D = list(0 for el in range(history_length))

        #Add Background colour to white
        self.graphWidget.setBackground('w')
        #Add Title
        self.graphWidget.setTitle("HEV Lab plots", color='blue', size=30)
        #Add Axis Labels
        self.graphWidget.setLabel('left', 'Readings', color='red', size=30)
        self.graphWidget.setLabel('bottom', 'Timestamp (ms)', color='red', size=30)
        #Add legend
        self.graphWidget.addLegend()
        #Add grid
        self.graphWidget.showGrid(x=True, y=True)
        #Set Range
        self.graphWidget.setXRange(0, 10, padding=0)
        self.graphWidget.setYRange(-20, 300, padding=0)

        self.line1 = self.graphWidget.plot(self.timestamp, self.pressure_inhale, "Buffer", 'r')
        self.line2 = self.graphWidget.plot(self.timestamp, self.pressure_buffer, "Inhale", 'b')
        self.line3 = self.graphWidget.plot(self.timestamp, self.PID_D, "Proportional", 'b')
        self.line4 = self.graphWidget.plot(self.timestamp, self.PID_I, "Integral", 'b')
        self.line5 = self.graphWidget.plot(self.timestamp, self.PID_D, "Derivative", 'b')

        self.qtimestamp = asyncio.Queue(history_length)
        self.qpressure_buffer = asyncio.Queue(history_length)
        self.qpressure_inhale = asyncio.Queue(history_length)
        self.qPID_P = asyncio.Queue(history_length)
        self.qPID_I = asyncio.Queue(history_length)
        self.qPID_D = asyncio.Queue(history_length)


    def update_llipacket(self, payload):
        #logging.info(f"payload received: {payload}")
        if payload.getType() == 1:
            self.cnt += 1
            logging.info(f"payload received: {payload}")
            if self.cnt % 20 == 0 :
                self.qtimestamp.put_nowait(payload.timestamp)
                self.qpressure_buffer.put_nowait(payload.pressure_buffer)
                self.qpressure_inhale.put_nowait(payload.pressure_inhale)
                self.qPID_D.put_nowait(payload.flow)
                self.qPID_I.put_nowait(payload.volume)
                self.qPID_P.put_nowait(payload.airway_pressure)
            #logging.info(f"Fsm state: {payload.fsm_state}")
        #if hasattr(payload, 'ventilation_mode'):
        #    logging.info(f"payload received: {payload.ventilation_mode}")
        #if hasattr(payload, 'duration_inhale'):
        #    logging.info(f"payload received: inhale duration = {payload.duration_inhale} ")
        print("data acquired")

        #build_history_plots(payload.getDict())
        #if self.counter % 10 == 0: draw_plots()

    async def redraw(self):
        while True:
            # append new value
            self.timestamp.append(await self.qtimestamp.get())
            self.pressure_inhale.append(await self.qpressure_inhale.get())
            self.pressure_buffer.append(await self.qpressure_buffer.get())
            self.PID_D.append(await self.qPID_D.get())
            self.PID_I.append(await self.qPID_I.get())
            self.PID_P.append(await self.qPID_P.get())
            # clear leftmost value
            self.pressure_buffer = self.pressure_buffer[1:]
            self.pressure_inhale = self.pressure_inhale[1:]
            self.PID_D = self.PID_D[1:]
            self.PID_I = self.PID_I[1:]
            self.PID_P = self.PID_P[1:]
            # clear from queue
            self.qtimestamp.task_done()
            self.qpressure_inhale.task_done()
            self.qpressure_buffer.task_done()
            self.qPID_D.task_done()
            self.qPID_I.task_done()
            self.qPID_P.task_done()
            print("Running draw plots finished ", self.pressure_inhale.qsize())
            self.line1.setData(self.timestamp, self.pressure_buffer)
            self.line2.setData(self.timestamp, self.pressure_inhale)
            self.line3.setData(self.timestamp, self.PID_D)
            self.line4.setData(self.timestamp, self.PID_I)
            self.line5.setData(self.timestamp, self.PID_P)


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

    # setup pyqtplot widget
    app = QtWidgets.QApplication(sys.argv)
    dep = LabPlots(comms)
    dep.show()

    # create tasks
    lli = comms.main(getTTYPort(), 115200)
    debug = commsDebug()
    plot = dep.redraw()
    tasks = [lli, debug, plot]

    # run tasks
    asyncio.gather(*tasks, return_exceptions=True)
    loop.run_forever()
except asyncio.CancelledError:
    pass
except KeyboardInterrupt:
    logging.info("Closing LLI")
finally:
    loop.close()
    sys.exit(app.exec_())
