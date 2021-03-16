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
        self.time_range = 30
        self.port = port

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

        self.graph_widget.setBackground(self.NativeUI.colors["background"])

        # Add grid, hide the autoscale button, and add the legend
        for plot in self.plots:
            plot.showGrid(x=True, y=True)
            plot.hideButtons()
            l = plot.addLegend(offset=(-1, 1))
            l.setLabelTextSize(self.NativeUI.text_size)

        # Set Range
        self.update_plot_time_range(61)

        # Plot styles
        self.pressure_line = self.plot(
            self.pressure_plot,
            [0, 0],
            [0, 0],
            NativeUI.text["plot_line_label_pressure"],
            NativeUI.colors["pressure_plot"].name(),
        )
        self.flow_line = self.plot(
            self.flow_plot,
            [0, 0],
            [0, 0],
            NativeUI.text["plot_line_label_flow"],
            NativeUI.colors["flow_plot"].name(),
        )
        self.volume_line = self.plot(
            self.volume_plot,
            [0, 0],
            [0, 0],
            NativeUI.text["plot_line_label_volume"],
            NativeUI.colors["volume_plot"].name(),
        )

        self.setLayout(layout)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(16)  # just faster than 60Hz
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

        self.update_plot_data()

    def plot(self, canvas, x, y, plotname, color):
        pen = pg.mkPen(color=color, width=3)
        return canvas.plot(x, y, name=plotname, pen=pen)

    def update_plot_data(self):
        """
        Get the current plots database and update the plots to match
        """
        plots = self.NativeUI.get_plots_db()

        # Extend the non-time scales if we need to
        self.pressure_plot.setYRange(*plots["pressure_axis_range"])
        self.flow_plot.setYRange(*plots["flow_axis_range"])
        self.volume_plot.setYRange(*plots["volume_axis_range"])

        # Replot lines with new data
        self.pressure_line.setData(plots["timestamp"], plots["pressure"])
        self.flow_line.setData(plots["timestamp"], plots["flow"])
        self.volume_line.setData(plots["timestamp"], plots["volume"])

        return 0

    @QtCore.Slot()
    def update_plot_time_range(self, time_range: int):
        self.time_range = time_range
        for plot in self.plots:
            plot.setXRange(self.time_range * (-1), 0, padding=0)
            plot.enableAutoRange("y", True)
        return 0
