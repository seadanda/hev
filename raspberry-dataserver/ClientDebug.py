#!/usr/bin/env python3
import asyncio
import logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
import sys
import time
import argparse
import json

import threading
from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot, mkColor
import pyqtgraph as pg
import sys
import os

from hevclient import HEVClient

class ClientPlots(QtWidgets.QMainWindow):
    def __init__(self, light=False, port=54322, *args, **kwargs):
        super(ClientPlots, self).__init__(*args, **kwargs)

        self.history_length = 300
        self.xrange = 300
        self.port = port

        self.setWindowTitle("HEV socket debug")
        self.graphWidget = pg.GraphicsLayoutWidget()
        self.setCentralWidget(self.graphWidget)
        self.statusBar().showMessage("Waiting for data")

        self.pressurePlot = self.graphWidget.addPlot(title="Pressure")
        self.graphWidget.nextRow()
        self.flowPlot = self.graphWidget.addPlot(title="Flow")
        self.graphWidget.nextRow()
        self.volumePlot = self.graphWidget.addPlot(title="Volume")
        self.graphWidget.nextRow()

        self.timestamp = list(el*(-1) for el in range(self.history_length))[::-1]
        self.PID_P = list(0 for _ in range(self.history_length))
        self.PID_I = list(0 for _ in range(self.history_length))
        self.PID_D = list(0 for _ in range(self.history_length))

        if light:
            # light theme
            self.graphWidget.setBackground('w')
        else:
            # dark theme
            self.graphWidget.setBackground(mkColor(30,30,30))

        # Add grid
        self.flowPlot.showGrid(x=True, y=True)
        self.volumePlot.showGrid(x=True, y=True)
        self.pressurePlot.showGrid(x=True, y=True)
        # Set Range
        self.flowPlot.setXRange(self.xrange * (-1), 0, padding=0)
        self.volumePlot.setXRange(self.xrange * (-1), 0, padding=0)
        self.pressurePlot.setXRange(self.xrange * (-1), 0, padding=0)
        self.flowPlot.enableAutoRange('y', True)
        self.volumePlot.enableAutoRange('y', True)
        self.pressurePlot.enableAutoRange('y', True)
        # Plot styles
        self.line1 = self.plot(self.flowPlot, self.timestamp, self.PID_D, "Flow", "00F")
        self.line2 = self.plot(self.volumePlot, self.timestamp, self.PID_I, "Volume", "707")
        self.line3 = self.plot(self.pressurePlot, self.timestamp, self.PID_P, "Airway Pressure", "077")

        # get data in another thread
        self.worker = threading.Thread(target=self.polling, daemon=True)
        self.worker.start()

    def polling(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # create tasks
            plot = self.redraw()
            debug = self.cmdDebug()
            tasks = [debug, plot]

            # run tasks
            asyncio.gather(*tasks, return_exceptions=True)
            loop.run_forever()
        except asyncio.CancelledError:
            pass
        finally:
            loop.close()

    def plot(self, canvas, x, y, plotname, color):
           pen = pg.mkPen(color=color, width=3)
           return canvas.plot(x, y, name=plotname, pen=pen)

    async def redraw(self):
        while True:
            try:
                reader, writer = await asyncio.open_connection("127.0.0.1", self.port)
                print("Connected successfully")
                while True:
                    try:
                        data = await reader.readuntil(separator=b'\0')
                        data = data[:-1] # snip off nullbyte
                        packet = json.loads(data.decode("utf-8"))
                        brtype = packet["type"]
                        if brtype == "keepalive":
                            continue

                        payload = packet[packet["type"]]
                        logging.debug(f"Received {brtype} packet: {payload}")
                        if brtype == "DATA":
                            self.statusBar().showMessage(f"Got data for timestamp {payload['timestamp']}")
                            logging.info("data acquired")
                            self.PID_D.append(payload["flow"])
                            self.PID_I.append(payload["volume"])
                            self.PID_P.append(payload["airway_pressure"])
                            if len(self.PID_D) > self.history_length:
                                self.PID_D = self.PID_D[1:]
                                self.PID_I = self.PID_I[1:]
                                self.PID_P = self.PID_P[1:]
                            self.line1.setData(self.timestamp, self.PID_D)
                            self.line2.setData(self.timestamp, self.PID_I)
                            self.line3.setData(self.timestamp, self.PID_P)
                        elif brtype == "READBACK":
                            pass
                        elif brtype == "CYCLE":
                            pass
                        elif brtype == "THRESHOLDS":
                            pass
                        elif brtype == "ALARM":
                            logging.error(f"received ALARM {payload}")
                        elif brtype == "IVT":
                            pass
                        elif brtype == "DEBUG":
                            pass
                        else:
                            raise KeyError

                        self._alarms = packet["alarms"]
                    except json.decoder.JSONDecodeError:
                        logging.warning(f"Could not decode packet: {data}")
                    except KeyError as e:
                        logging.warning(f"Invalid payload: {data}")
                        logging.error(e)
                    except Exception as e:
                        logging.error(e)
                        raise

                # close connection
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                logging.error(e)
                await asyncio.sleep(2)

    async def cmdDebug(self):
        """Put debug code here"""
        try:
            client = HEVClient(polling=False) # just use hevclient for requests
            await asyncio.sleep(2)
            # trigger an alarm
            await client.send_request("CMD", cmdtype="SET_THRESHOLD_MIN", cmd="APNEA",param=0)
            while True:
                await asyncio.sleep(60)
        except Exception as e:
            # otherwise never propagated
            print(e)

if __name__ == "__main__":
    # parse args and setup logging
    parser = argparse.ArgumentParser(description='Plotting script for the HEV lab setup')
    parser.add_argument('-d', '--debug', action='count', default=0, help='Show debug output')
    parser.add_argument('--native', action='store_true', help="Use a port that doesn't clash with NativeUI")
    parser.add_argument('--light', action='store_true', help='Use light mode')

    args = parser.parse_args()
    if args.debug == 0:
        logging.getLogger().setLevel(logging.WARNING)
    elif args.debug == 1:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.DEBUG)

    # setup pyqtplot widget
    app = QtWidgets.QApplication(sys.argv)
    port = 54320 if args.native else 54322
    dep = ClientPlots(light=args.light, port=port)
    dep.show()
    sys.exit(app.exec_())