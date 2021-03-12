#!/usr/bin/env python3

"""
tab_expert_plots.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Benjamin Mummery"
__email__ = "benjamin.mummery@stfc.ac.uk"
__status__ = "Development"

from main_widgets.tab_measurements import TabExpertMeasurements
from PySide2 import QtWidgets
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np


class TabExpertPlots(QtWidgets.QWidget):
    def __init__(self, NativeUI, port=54322, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        self.history_length = 500
        self.time_range = 30
        self.port = port

        self.timestamp = list(el * (-1) for el in range(self.history_length))[::-1]
        self.PID_P = list(0 for _ in range(self.history_length))
        self.PID_I = list(0 for _ in range(self.history_length))
        self.PID_D = list(0 for _ in range(self.history_length))

        # Scaling for plot axes (helpful for keeping left axis lined up)
        self.__PID_I_scale = NativeUI.PID_I_plot_scale

        #
        layout = QtWidgets.QHBoxLayout()
        self.left_graph_widget = pg.GraphicsLayoutWidget()
        self.tab_expert_measurements = TabExpertMeasurements(NativeUI)
        self.right_graph_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.left_graph_widget)
        layout.addWidget(self.tab_expert_measurements)
        layout.addWidget(self.right_graph_widget)

        # Left column - value-time plots
        self.pressure_plot = self.left_graph_widget.addPlot(
            labels={"left": NativeUI.text["plot_axis_label_pressure"]}
        )
        self.pressure_plot.getAxis("bottom").setStyle(showValues=False)
        self.left_graph_widget.nextRow()

        self.flow_plot = self.left_graph_widget.addPlot(
            labels={"left": NativeUI.text["plot_axis_label_flow"]}
        )
        self.flow_plot.setXLink(self.pressure_plot)
        self.flow_plot.getAxis("bottom").setStyle(showValues=False)
        self.left_graph_widget.nextRow()

        self.volume_plot = self.left_graph_widget.addPlot(
            labels={
                "left": NativeUI.text["plot_axis_label_volume"],
                "bottom": NativeUI.text["plot_axis_label_time"],
            }
        )
        self.volume_plot.setXLink(self.pressure_plot)
        self.left_graph_widget.nextRow()

        self.plots = [self.pressure_plot, self.flow_plot, self.volume_plot]
        self.left_graph_widget.setContentsMargins(0.0, 0.0, 0.0, 0.0)

        # Right column - circle plots
        self.pressure_flow_plot = self.right_graph_widget.addPlot(
            labels={
                "bottom": NativeUI.text["plot_axis_label_flow"],
                "left": NativeUI.text["plot_axis_label_pressure"],
            }
        )
        self.right_graph_widget.nextRow()

        self.flow_volume_plot = self.right_graph_widget.addPlot(
            labels={
                "bottom": NativeUI.text["plot_axis_label_volume"],
                "left": NativeUI.text["plot_axis_label_flow"],
            }
        )
        self.right_graph_widget.nextRow()

        self.volume_pressure_plot = self.right_graph_widget.addPlot(
            labels={
                "bottom": NativeUI.text["plot_axis_label_pressure"],
                "left": NativeUI.text["plot_axis_label_volume"],
            }
        )
        self.right_graph_widget.nextRow()

        self.circleplots = [
            self.pressure_flow_plot,
            self.flow_volume_plot,
            self.volume_pressure_plot,
        ]
        self.right_graph_widget.setContentsMargins(0.0, 0.0, 0.0, 0.0)

        # Set background to match global background
        self.left_graph_widget.setBackground(self.NativeUI.colors["background"])
        self.right_graph_widget.setBackground(self.NativeUI.colors["background"])

        # Add Grid, hide the autoscale button, and add the legend
        for plot in self.plots + self.circleplots:
            plot.showGrid(x=True, y=True)
            plot.hideButtons()
            l = plot.addLegend(offset=(-1, 1))
            l.setLabelTextSize(self.NativeUI.text_size)

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
        self.pressure_flow_line = self.plot(
            self.pressure_flow_plot,
            self.PID_P,
            self.PID_I,
            NativeUI.text["plot_line_label_pressure_flow"],
            NativeUI.colors["pressure_flow_plot"].name(),
        )
        self.flow_volume_line = self.plot(
            self.flow_volume_plot,
            self.PID_D,
            self.PID_I,
            NativeUI.text["plot_line_label_flow_volume"],
            NativeUI.colors["flow_volume_plot"].name(),
        )
        self.volume_pressure_line = self.plot(
            self.volume_pressure_plot,
            self.PID_P,
            self.PID_D,
            NativeUI.text["plot_line_label_volume_pressure"],
            NativeUI.colors["volume_pressure_plot"].name(),
        )

        self.setLayout(layout)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(16)  # just faster than 60Hz
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

        # Set Ranges
        self.update_plot_time_range(60)
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
        self.pressure_flow_line.setData(flow, pressure)
        self.flow_volume_line.setData(volume, flow)
        self.volume_pressure_line.setData(pressure, volume)

    def __update_ranges(self):
        self.pressure_plot.setYRange(*self.NativeUI.plots["plot_axis_range_pressure"])

        self.flow_plot.setYRange(*self.NativeUI.plots["plot_axis_range_flow"])

        self.volume_plot.setYRange(*self.NativeUI.plots["plot_axis_range_volume"])

        self.pressure_flow_plot.setXRange(*self.NativeUI.plots["plot_axis_range_flow"])
        self.pressure_flow_plot.setYRange(
            *self.NativeUI.plots["plot_axis_range_pressure"]
        )

        self.flow_volume_plot.setXRange(*self.NativeUI.plots["plot_axis_range_volume"])
        self.flow_volume_plot.setYRange(*self.NativeUI.plots["plot_axis_range_flow"])

        self.volume_pressure_plot.setXRange(
            *self.NativeUI.plots["plot_axis_range_pressure"]
        )
        self.volume_pressure_plot.setYRange(
            *self.NativeUI.plots["plot_axis_range_volume"]
        )
        return 0

    @QtCore.Slot()
    def update_plot_time_range(self, time_range: int):
        self.time_range = time_range
        for plot in self.plots:
            plot.setXRange(self.time_range * (-1), 0, padding=0)
        self.update_plot_data()
        return 0
