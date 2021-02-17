#!/usr/bin/env python3
import logging
import os

import numpy as np
import pyqtgraph as pg
from hevclient import HEVClient
from pyqtgraph import PlotWidget, mkColor, plot
from PySide2 import QtCore, QtWidgets

logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s"
)


class TabPlots(QtWidgets.QWidget):
    def __init__(self, NativeUI, port=54322, *args, **kwargs):
        super(TabPlots, self).__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        self.history_length = 500
        self.time_range = 30
        self.port = port

        layout = QtWidgets.QVBoxLayout()
        self.graphWidget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.graphWidget)

        self.pressurePlot = self.graphWidget.addPlot(title="Pressure")
        self.graphWidget.nextRow()
        self.flowPlot = self.graphWidget.addPlot(title="Flow")
        self.graphWidget.nextRow()
        self.volumePlot = self.graphWidget.addPlot(title="Volume")
        self.graphWidget.nextRow()

        self.timestamp = list(el * (-1) for el in range(self.history_length))[::-1]
        self.PID_P = list(0 for _ in range(self.history_length))
        self.PID_I = list(0 for _ in range(self.history_length))
        self.PID_D = list(0 for _ in range(self.history_length))

        self.graphWidget.setBackground(mkColor(30, 30, 30))

        # Add grid
        self.flowPlot.showGrid(x=True, y=True)
        self.volumePlot.showGrid(x=True, y=True)
        self.pressurePlot.showGrid(x=True, y=True)

        # Set Range
        self.flowPlot.setXRange(self.time_range * (-1), 0, padding=0)
        self.volumePlot.setXRange(self.time_range * (-1), 0, padding=0)
        self.pressurePlot.setXRange(self.time_range * (-1), 0, padding=0)
        self.flowPlot.enableAutoRange("y", True)
        self.volumePlot.enableAutoRange("y", True)
        self.pressurePlot.enableAutoRange("y", True)

        # Plot styles
        self.line1 = self.plot(
            self.pressurePlot, self.timestamp, self.PID_P, "Airway Pressure", "077"
        )
        self.line2 = self.plot(self.flowPlot, self.timestamp, self.PID_D, "Flow", "00F")
        self.line3 = self.plot(
            self.volumePlot, self.timestamp, self.PID_I, "Volume", "707"
        )

        self.setLayout(layout)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(16)  # just faster than 60Hz
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def plot(self, canvas, x, y, plotname, color):
        pen = pg.mkPen(color=color, width=3)
        return canvas.plot(x, y, name=plotname, pen=pen)

    def update_plot_data(self):
        # subtract latest timestamp and scale to seconds
        plots = self.NativeUI.get_plots_db()
        timestamp = np.true_divide(np.subtract(plots[:, 0], plots[-1, 0]), 1000)
        self.line1.setData(timestamp, plots[:, 1])
        self.line2.setData(timestamp, plots[:, 2])
        self.line3.setData(timestamp, plots[:, 3])
