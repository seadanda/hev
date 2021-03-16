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
        self.pressure_flow_line = self.plot(
            self.pressure_flow_plot,
            [0, 0],
            [0, 0],
            NativeUI.text["plot_line_label_pressure_flow"],
            NativeUI.colors["pressure_flow_plot"].name(),
        )
        self.flow_volume_line = self.plot(
            self.flow_volume_plot,
            [0, 0],
            [0, 0],
            NativeUI.text["plot_line_label_flow_volume"],
            NativeUI.colors["flow_volume_plot"].name(),
        )
        self.volume_pressure_line = self.plot(
            self.volume_pressure_plot,
            [0, 0],
            [0, 0],
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
        self.pressure_flow_plot.setXRange(*plots["flow_axis_range"])
        self.pressure_flow_plot.setYRange(*plots["pressure_axis_range"])
        self.flow_volume_plot.setXRange(*plots["volume_axis_range"])
        self.flow_volume_plot.setYRange(*plots["flow_axis_range"])
        self.volume_pressure_plot.setXRange(*plots["pressure_axis_range"])
        self.volume_pressure_plot.setYRange(*plots["volume_axis_range"])

        # Replot lines with new data
        self.pressure_line.setData(plots["timestamp"], plots["pressure"])
        self.flow_line.setData(plots["timestamp"], plots["flow"])
        self.volume_line.setData(plots["timestamp"], plots["volume"])
        self.pressure_flow_line.setData(plots["flow"], plots["pressure"])
        self.flow_volume_line.setData(plots["volume"], plots["flow"])
        self.volume_pressure_line.setData(plots["pressure"], plots["volume"])

        return 0

    @QtCore.Slot()
    def update_plot_time_range(self, time_range: int):
        self.time_range = time_range
        for plot in self.plots:
            plot.setXRange(self.time_range * (-1), 0, padding=0)
        self.update_plot_data()
        return 0
