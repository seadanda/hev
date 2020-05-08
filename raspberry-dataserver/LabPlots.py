#!/usr/bin/env python3
from CommsLLI import CommsLLI
from CommsCommon import *
import asyncio
import logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
from serial.tools import list_ports
import sys
import time
import argparse

import threading
from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot, mkColor
import pyqtgraph as pg
import sys
import os

class LabPlots(QtWidgets.QMainWindow):

    def __init__(self, dark=False, throttle=20, *args, **kwargs):
        super(LabPlots, self).__init__(*args, **kwargs)

        self.history_length = 500
        self.throttle = throttle

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.timestamp = list(el*(-1) for el in range(self.history_length))[::-1]
        self.pressure_buffer = list(0 for _ in range(self.history_length))
        self.pressure_inhale = list(0 for _ in range(self.history_length))
        self.PID_P = list(0 for _ in range(self.history_length))
        self.PID_I = list(0 for _ in range(self.history_length))
        self.PID_D = list(0 for _ in range(self.history_length))

        if dark:
            # dark theme
            self.graphWidget.setBackground(mkColor(30,30,30))
        else:
            # light theme
            self.graphWidget.setBackground('w')

        #Add Title
        self.graphWidget.setTitle("HEV Lab Plots")
        #Add Axis Labels
        #self.graphWidget.setLabel('left', 'Readings', size=40)
        #self.graphWidget.setLabel('bottom', 'Time', size=40)
        #Add legend
        self.graphWidget.addLegend()
        #Add grid
        self.graphWidget.showGrid(x=True, y=True)
        #Set Range
        self.graphWidget.setXRange(self.history_length * (-1) * 0.1, 0, padding=0)
        self.graphWidget.setYRange(0, 40, padding=0)

        self.line1 = self.plot(self.timestamp, self.pressure_inhale, "Buffer", "F00")
        self.line2 = self.plot(self.timestamp, self.pressure_buffer, "Inhale", "0F0")
        self.line3 = self.plot(self.timestamp, self.PID_D, "Proportional", "00F")
        self.line4 = self.plot(self.timestamp, self.PID_I, "Integral", "707")
        self.line5 = self.plot(self.timestamp, self.PID_D, "Derivative", "077")

        # get data in another thread
        self.worker = threading.Thread(target=self.polling, daemon=True)
        self.worker.start()

    def polling(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            comms = CommsLLI(loop, throttle=self.throttle)

            # create tasks
            lli = comms.main(getTTYPort(), 115200)
            plot = self.redraw(comms)
            debug = commsDebug(comms)
            tasks = [lli, debug, plot]

            # run tasks
            asyncio.gather(*tasks, return_exceptions=True)
            loop.run_forever()
        except asyncio.CancelledError:
            pass
        finally:
            loop.close()

    def plot(self, x, y, plotname, color):
           pen = pg.mkPen(color=color, width=3)
           return self.graphWidget.plot(x, y, name=plotname, pen=pen)

    async def redraw(self, lli):
        while True:
            payload = await lli._payloadrecv.get()
            if payload.getType() == 1:
                logging.info(f"payload received: {payload}")
                logging.debug("data acquired")
                self.pressure_buffer.append(payload.pressure_buffer)
                self.pressure_inhale.append(payload.pressure_inhale)
                self.PID_D.append(payload.flow)
                self.PID_I.append(payload.volume)
                self.PID_P.append(payload.airway_pressure)
                if len(self.pressure_buffer) > self.history_length:
                    self.pressure_buffer = self.pressure_buffer[1:]
                    self.pressure_inhale = self.pressure_inhale[1:]
                    self.PID_D = self.PID_D[1:]
                    self.PID_I = self.PID_I[1:]
                    self.PID_P = self.PID_P[1:]
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
async def commsDebug(comms):
    #cmd = CommandFormat(cmd_type=CMD_TYPE.GENERAL.value, cmd_code=CMD_GENERAL.START.value, param=0)
    #cmd = CommandFormat(cmd_type=CMD_TYPE.SET_TIMEOUT.value, cmd_code=CMD_SET_TIMEOUT.INHALE.value, param=1111)

    #Defining the PID parameters, derivative not implemented yet
    await asyncio.sleep(1)
    cmd = CommandFormat(cmd_type=CMD_TYPE.SET_PID.value, cmd_code=CMD_SET_PID.KP.value, param=0.01) # to set Kp=0.0002, param=200 i.e., micro_Kp
    comms.writePayload(cmd)
    await asyncio.sleep(1)
    cmd = CommandFormat(cmd_type=CMD_TYPE.SET_PID.value, cmd_code=CMD_SET_PID.KI.value, param=0.0004)#0002) # to set Kp=0.0002, param=200 i.e., micro_Kp
    comms.writePayload(cmd)
    await asyncio.sleep(1)
    cmd = CommandFormat(cmd_type=CMD_TYPE.SET_PID.value, cmd_code=CMD_SET_PID.KD.value, param=0.0011) # to set Kp=0.0002, param=200 i.e., micro_Kp
    comms.writePayload(cmd)
    await asyncio.sleep(1)

    #Start command
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


if __name__ == "__main__":
    # parse args and setup logging
    parser = argparse.ArgumentParser(description='Plotting script for the HEV lab setup')
    parser.add_argument('-d', '--debug', action='count', default=0, help='Show debug output')
    parser.add_argument('--throttle', type=int, default=20, help='Reduce rate from LLI')
    parser.add_argument('--dark', action='store_true', help='Use dark mode')

    args = parser.parse_args()
    if args.debug == 0:
        logging.getLogger().setLevel(logging.WARNING)
    elif args.debug == 1:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.DEBUG)

    # setup pyqtplot widget
    app = QtWidgets.QApplication(sys.argv)
    dep = LabPlots(dark=args.dark, throttle=args.throttle)
    dep.show()
    sys.exit(app.exec_())
