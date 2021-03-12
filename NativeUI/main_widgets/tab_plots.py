#!/usr/bin/env python3

"""
tab_plots.py

Part of NativeUI.
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Benjamin Mummery"
__email__ = "benjamin.mummery@stfc.ac.uk"
__status__ = "Development"

import logging

import numpy as np
import pyqtgraph as pg
from pyqtgraph import mkColor
from PySide2 import QtCore, QtWidgets


class TabPlots(QtWidgets.QWidget):
    def __init__(self, NativeUI, port=54322, *args, **kwargs):
        super(TabPlots, self).__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        self.history_length = 500
        self.time_range = 30
        self.port = port

        # Scaling for plot axes (helpful for keeping left axis lined up)
        self.__PID_I_scale = NativeUI.PID_I_plot_scale

        layout = QtWidgets.QVBoxLayout()
        self.graph_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.graph_widget)
        self.pressure_plot = self.graph_widget.addPlot(
            labels={"left": NativeUI.text["plot_axis_label_pressure"]}
        )
        self.pressure_plot.getAxis("bottom").setStyle(showValues=False)
        self.graph_widget.nextRow()

        self.flow_plot = self.graph_widget.addPlot(
            labels={"left": NativeUI.text["plot_axis_label_flow"]}
        )
        self.flow_plot.getAxis("bottom").setStyle(showValues=False)
        self.flow_plot.setXLink(self.pressure_plot)
        self.graph_widget.nextRow()

        self.volume_plot = self.graph_widget.addPlot(
            labels={
                "left": NativeUI.text["plot_axis_label_volume"],
                "bottom": NativeUI.text["plot_axis_label_time"],
            }
        )
        self.volume_plot.setXLink(self.pressure_plot)
        self.graph_widget.nextRow()

        self.plots = [self.pressure_plot, self.flow_plot, self.volume_plot]
        self.graph_widget.setContentsMargins(0.0, 0.0, 0.0, 0.0)

        self.timestamp = list(el * (-1) for el in range(self.history_length))[::-1]
        self.PID_P = list(0 for _ in range(self.history_length))
        self.PID_I = list(0 for _ in range(self.history_length))
        self.PID_D = list(0 for _ in range(self.history_length))

        self.graph_widget.setBackground(self.NativeUI.colors["background"])

        # Add grid, hide the autoscale button, and add the legend
        for plot in self.plots:
            plot.showGrid(x=True, y=True)
            plot.hideButtons()
            l = plot.addLegend(offset=(-1, 1))
            l.setLabelTextSize(self.NativeUI.text_size)

        # Set Range
        self.update_plot_time_range(60)

        # Plot styles
        self.pressure_line = self.plot(
            self.pressure_plot,
            self.timestamp,
            self.PID_P,
            NativeUI.text["plot_line_label_pressure"],
            NativeUI.colors["pressure_plot"].name(),
        )
        self.flow_line = self.plot(
            self.flow_plot,
            self.timestamp,
            self.PID_D,
            NativeUI.text["plot_line_label_flow"],
            NativeUI.colors["flow_plot"].name(),
        )
        self.volume_line = self.plot(
            self.volume_plot,
            self.timestamp,
            self.PID_I,
            NativeUI.text["plot_line_label_volume"],
            NativeUI.colors["volume_plot"].name(),
        )

        self.setLayout(layout)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(16)  # just faster than 60Hz
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

        self.__update_ranges()

    def plot(self, canvas, x, y, plotname, color):
        pen = pg.mkPen(color=color, width=3)
        return canvas.plot(x, y, name=plotname, pen=pen)

    def update_plot_data(self):
        # subtract latest timestamp and scale to seconds
        plots = self.NativeUI.get_plots_db()
        timestamp = np.true_divide(np.subtract(plots[:, 0], plots[-1, 0]), 1000)
        pressure = plots[:, 1]
        flow = plots[:, 2]
        volume = [v / (10 ** self.__PID_I_scale) for v in plots[:, 3]]

        # Check whether data exceeds limits
        update_ranges = False
        if max(pressure) > self.NativeUI.plots["plot_axis_range_pressure"][1]:
            self.NativeUI.plots["plot_axis_range_pressure"][1] = max(pressure)
            update_ranges = True
        if min(flow) < self.NativeUI.plots["plot_axis_range_flow"][0]:
            self.NativeUI.plots["plot_axis_range_flow"][0] = min(flow)
            update_ranges = True
        if max(flow) > self.NativeUI.plots["plot_axis_range_flow"][1]:
            self.NativeUI.plots["plot_axis_range_flow"][1] = max(flow)
            update_ranges = True
        if max(volume) > self.NativeUI.plots["plot_axis_range_volume"][1]:
            self.NativeUI.plots["plot_axis_range_volume"][1] = max(volume)
            update_ranges = True
        if update_ranges:
            self.__update_ranges()

        self.pressure_line.setData(timestamp, pressure)
        self.flow_line.setData(timestamp, flow)
        self.volume_line.setData(timestamp, volume)

    def __update_ranges(self):
        self.pressure_plot.setYRange(*self.NativeUI.plots["plot_axis_range_pressure"])
        self.flow_plot.setYRange(*self.NativeUI.plots["plot_axis_range_flow"])
        self.volume_plot.setYRange(*self.NativeUI.plots["plot_axis_range_volume"])
        return 0

    @QtCore.Slot()
    def update_plot_time_range(self, time_range: int):
        self.time_range = time_range
        for plot in self.plots:
            plot.setXRange(self.time_range * (-1), 0, padding=0)
            plot.enableAutoRange("y", True)
        return 0
