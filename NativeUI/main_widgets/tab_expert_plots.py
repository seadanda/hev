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

from PySide2 import QtCore, QtWidgets
import pyqtgraph as pg
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

        layout = QtWidgets.QHBoxLayout()
        self.left_graph_widget = pg.GraphicsLayoutWidget()
        self.right_graph_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.left_graph_widget)
        layout.addWidget(self.right_graph_widget)

        # Left column - value-time plots
        self.pressure_plot = self.left_graph_widget.addPlot(title="Pressure")
        self.left_graph_widget.nextRow()
        self.flow_plot = self.left_graph_widget.addPlot(title="Flow")
        self.left_graph_widget.nextRow()
        self.volume_plot = self.left_graph_widget.addPlot(title="Volume")
        self.left_graph_widget.nextRow()
        self.plots = [self.pressure_plot, self.flow_plot, self.volume_plot]

        # Right column - circle plots
        self.pressure_volume_plot = self.right_graph_widget.addPlot(
            title="Pressure vs Volume"
        )
        self.right_graph_widget.nextRow()
        self.pressure_flow_plot = self.right_graph_widget.addPlot(
            title="Pressure vs Flow"
        )
        self.right_graph_widget.nextRow()
        self.flow_volume_plot = self.right_graph_widget.addPlot(title="Flow vs Volume")
        self.right_graph_widget.nextRow()
        self.circleplots = [
            self.pressure_volume_plot,
            self.pressure_flow_plot,
            self.flow_volume_plot,
        ]

        # Set background to match global background
        self.left_graph_widget.setBackground(self.NativeUI.colors["background"])
        self.right_graph_widget.setBackground(self.NativeUI.colors["background"])

        # Add Grid
        for plot in self.plots + self.circleplots:
            plot.showGrid(x=True, y=True)

        # Plot styles
        self.line1 = self.plot(
            self.pressure_plot, self.timestamp, self.PID_P, "Airway Pressure", "077"
        )
        self.line2 = self.plot(
            self.flow_plot, self.timestamp, self.PID_D, "Flow", "00F"
        )
        self.line3 = self.plot(
            self.volume_plot, self.timestamp, self.PID_I, "Volume", "707"
        )
        self.line4 = self.plot(
            self.pressure_volume_plot,
            self.PID_P,
            self.PID_I,
            "Pressure vs Volume",
            "077",
        )
        self.line5 = self.plot(
            self.flow_volume_plot, self.PID_D, self.PID_I, "Flow vs Volume", "077"
        )
        self.line6 = self.plot(
            self.pressure_flow_plot, self.PID_P, self.PID_D, "Pressure vs Flow", "077"
        )

        self.setLayout(layout)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(16)  # just faster than 60Hz
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

        # Set Time Range
        self.update_plot_time_range(60)

    def plot(self, canvas, x, y, plotname, color):
        pen = pg.mkPen(color=color, width=3)
        return canvas.plot(x, y, name=plotname, pen=pen)

    def update_plot_data(self):
        # subtract latest timestamp and scale to seconds
        plots = self.NativeUI.get_plots_db()
        timestamp = np.true_divide(np.subtract(plots[:, 0], plots[-1, 0]), 1000)
        pressure = plots[:, 1]
        flow = plots[:, 2]
        volume = plots[:, 3]
        self.line1.setData(timestamp, pressure)
        self.line2.setData(timestamp, flow)
        self.line3.setData(timestamp, volume)
        self.line4.setData(pressure, volume)
        self.line5.setData(flow, volume)
        self.line6.setData(pressure, flow)

    @QtCore.Slot()
    def update_plot_time_range(self, time_range: int):
        self.time_range = time_range
        for plot in self.plots:
            plot.setXRange(self.time_range * (-1), 0, padding=0)
            plot.enableAutoRange("y", True)
        self.update_plot_data()
        return 0
