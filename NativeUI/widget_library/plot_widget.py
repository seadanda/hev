#!/usr/bin/env python3

"""
plot_widget.py

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
from PySide2 import QtCore, QtGui, QtWidgets


class TimePlotsWidget(QtWidgets.QWidget):
    def __init__(self, NativeUI, port=54322, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        self.time_range = 30
        self.port = port

        layout = QtWidgets.QVBoxLayout()
        self.graph_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.graph_widget)

        labelStyle = {"color": NativeUI.colors["page_foreground"], "font-size": "15pt"}

        # Set up pressure - time plot
        self.pressure_plot = self.graph_widget.addPlot()
        self.pressure_plot.setLabel(
            "left", NativeUI.text["plot_axis_label_pressure"], **labelStyle
        )
        self.graph_widget.nextRow()

        # Set up flow - time plot
        self.flow_plot = self.graph_widget.addPlot()
        self.flow_plot.setLabel(
            "left", NativeUI.text["plot_axis_label_flow"], **labelStyle
        )
        self.flow_plot.setXLink(self.pressure_plot)
        self.graph_widget.nextRow()

        # Set up volume -time plot
        self.volume_plot = self.graph_widget.addPlot()
        self.volume_plot.setLabel(
            "left", NativeUI.text["plot_axis_label_volume"], **labelStyle
        )
        self.volume_plot.setLabel(
            "bottom", NativeUI.text["plot_axis_label_time"], **labelStyle
        )
        self.volume_plot.setXLink(self.pressure_plot)
        self.graph_widget.nextRow()

        self.plots = [self.pressure_plot, self.flow_plot, self.volume_plot]
        self.graph_widget.setContentsMargins(0.0, 0.0, 0.0, 0.0)

        self.graph_widget.setBackground(self.NativeUI.colors["page_background"])

        # Add grid, hide the autoscale button, and add the legend
        for plot in self.plots:
            plot.showGrid(x=True, y=True)
            plot.hideButtons()
            l = plot.addLegend(offset=(-1, 1))
            l.setFont(NativeUI.text_font)
            plot.setMouseEnabled(x=False, y=False)
            plot.getAxis("bottom").setStyle(tickFont=NativeUI.text_font)
            plot.getAxis("left").setStyle(tickFont=NativeUI.text_font)
            plot.getAxis("left").setTextPen(NativeUI.colors["page_foreground"])
            plot.getAxis("bottom").setTextPen(NativeUI.colors["page_foreground"])

        # Set Range
        self.update_plot_time_range(61)

        # Plot styles
        self.pressure_line = self.plot(
            self.pressure_plot,
            [0, 0],
            [0, 0],
            NativeUI.text["plot_line_label_pressure"],
            NativeUI.colors["plot_pressure"].name(),
        )
        self.flow_line = self.plot(
            self.flow_plot,
            [0, 0],
            [0, 0],
            NativeUI.text["plot_line_label_flow"],
            NativeUI.colors["plot_flow"].name(),
        )
        self.volume_line = self.plot(
            self.volume_plot,
            [0, 0],
            [0, 0],
            NativeUI.text["plot_line_label_volume"],
            NativeUI.colors["plot_volume"].name(),
        )

        self.setLayout(layout)

    def plot(self, canvas, x, y, plotname, color):
        pen = pg.mkPen(color=color, width=3)
        return canvas.plot(x, y, name=plotname, pen=pen)

    @QtCore.Slot(dict)
    def update_plot_data(self, plots: dict):
        """
        Get the current plots database and update the plots to match
        """

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

    @QtCore.Slot(dict)
    def localise_text(self, text: dict) -> int:
        """
        Update the text displayed on the axis' and legend of time plots.
        """
        self.pressure_plot.setLabel("left", text["plot_axis_label_pressure"])
        self.pressure_plot.legend.clear()
        self.pressure_plot.legend.addItem(
            self.pressure_line, text["plot_line_label_pressure"]
        )

        self.flow_plot.setLabel("left", text["plot_axis_label_flow"])
        self.flow_plot.legend.clear()
        self.flow_plot.legend.addItem(self.flow_line, text["plot_line_label_flow"])

        self.volume_plot.setLabel("left", text["plot_axis_label_volume"])
        self.volume_plot.setLabel("bottom", text["plot_axis_label_time"])
        self.volume_plot.legend.clear()
        self.volume_plot.legend.addItem(
            self.volume_line, text["plot_line_label_volume"]
        )

        return 0


class CirclePlotsWidget(QtWidgets.QWidget):
    def __init__(self, NativeUI, port=54322, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        self.time_range = 30
        self.port = port

        layout = QtWidgets.QVBoxLayout()
        self.graph_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.graph_widget)

        labelStyle = {"color": NativeUI.colors["page_foreground"], "font-size": "15pt"}

        self.pressure_flow_plot = self.graph_widget.addPlot()
        self.pressure_flow_plot.setLabel(
            "left", NativeUI.text["plot_axis_label_pressure"], **labelStyle
        )
        self.pressure_flow_plot.setLabel(
            "bottom", NativeUI.text["plot_axis_label_flow"], **labelStyle
        )
        self.graph_widget.nextRow()

        self.flow_volume_plot = self.graph_widget.addPlot()
        self.flow_volume_plot.setLabel(
            "left", NativeUI.text["plot_axis_label_volume"], **labelStyle
        )
        self.flow_volume_plot.setLabel(
            "bottom", NativeUI.text["plot_axis_label_flow"], **labelStyle
        )
        self.graph_widget.nextRow()

        self.volume_pressure_plot = self.graph_widget.addPlot()
        self.volume_pressure_plot.setLabel(
            "left", NativeUI.text["plot_axis_label_pressure"], **labelStyle
        )
        self.volume_pressure_plot.setLabel(
            "bottom", NativeUI.text["plot_axis_label_volume"], **labelStyle
        )
        self.graph_widget.nextRow()

        self.graph_widget.nextRow()

        self.plots = [
            self.pressure_flow_plot,
            self.flow_volume_plot,
            self.volume_pressure_plot,
        ]
        self.graph_widget.setContentsMargins(0.0, 0.0, 0.0, 0.0)

        # Set background to match global background
        self.graph_widget.setBackground(self.NativeUI.colors["page_background"])

        # Add grid, hide the autoscale button, and add the legend
        for plot in self.plots:
            plot.showGrid(x=True, y=True)
            plot.hideButtons()
            l = plot.addLegend(offset=(-1, 1))
            l.setFont(NativeUI.text_font)
            plot.setMouseEnabled(x=False, y=False)
            plot.getAxis("bottom").setStyle(tickFont=NativeUI.text_font)
            plot.getAxis("left").setStyle(tickFont=NativeUI.text_font)
            plot.getAxis("left").setTextPen(NativeUI.colors["page_foreground"])
            plot.getAxis("bottom").setTextPen(NativeUI.colors["page_foreground"])

        # Plot styles
        self.pressure_flow_line = self.plot(
            self.pressure_flow_plot,
            [0, 0],
            [0, 0],
            NativeUI.text["plot_line_label_pressure_flow"],
            NativeUI.colors["plot_pressure_flow"].name(),
        )
        self.flow_volume_line = self.plot(
            self.flow_volume_plot,
            [0, 0],
            [0, 0],
            NativeUI.text["plot_line_label_flow_volume"],
            NativeUI.colors["plot_flow_volume"].name(),
        )
        self.volume_pressure_line = self.plot(
            self.volume_pressure_plot,
            [0, 0],
            [0, 0],
            NativeUI.text["plot_line_label_volume_pressure"],
            NativeUI.colors["plot_volume_pressure"].name(),
        )

        self.setLayout(layout)

    def plot(self, canvas, x, y, plotname, color):
        pen = pg.mkPen(color=color, width=3)
        return canvas.plot(x, y, name=plotname, pen=pen)

    @QtCore.Slot(dict)
    def update_plot_data(self, plots: dict):
        """
        Update the plots to match the new data.
        """
        self.pressure_flow_line.setData(plots["cycle_flow"], plots["cycle_pressure"])
        self.flow_volume_line.setData(plots["cycle_volume"], plots["cycle_flow"])
        self.volume_pressure_line.setData(
            plots["cycle_pressure"], plots["cycle_volume"]
        )
        return 0

    @QtCore.Slot(dict)
    def localise_text(self, text: dict) -> int:
        """
        Update the text displayed on the axis' and legend of circle plots.
        """
        self.pressure_flow_plot.setLabel("left", text["plot_axis_label_pressure"])
        self.pressure_flow_plot.setLabel("bottom", text["plot_axis_label_flow"])
        self.pressure_flow_plot.legend.clear()
        self.pressure_flow_plot.legend.addItem(
            self.pressure_flow_line, text["plot_line_label_pressure_flow"]
        )

        self.flow_volume_plot.setLabel("left", text["plot_axis_label_flow"])
        self.flow_volume_plot.setLabel("bottom", text["plot_axis_label_volume"])
        self.flow_volume_plot.legend.clear()
        self.flow_volume_plot.legend.addItem(
            self.flow_volume_line, text["plot_line_label_flow_volume"]
        )

        self.volume_pressure_plot.setLabel("left", text["plot_axis_label_volume"])
        self.volume_pressure_plot.setLabel("bottom", text["plot_axis_label_pressure"])
        self.volume_pressure_plot.legend.clear()
        self.volume_pressure_plot.legend.addItem(
            self.volume_pressure_line, text["plot_line_label_volume_pressure"]
        )

        return 0


class ChartsPlotWidget(QtWidgets.QWidget):
    def __init__(self, port=54322, *args, colors: dict = {}, **kwargs):
        super().__init__(*args, **kwargs)

        self.port = port

        layout = QtWidgets.QHBoxLayout()

        # Set up the graph widget
        self.graph_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.graph_widget)

        labelStyle = {"color": "#FFF", "font-size": "15pt"}

        # Add the plot axes to the graph widget
        self.display_plot = self.graph_widget.addPlot()
        self.display_plot.setLabel("left", "????", **labelStyle)
        self.display_plot.setLabel("bottom", "????", **labelStyle)
        self.display_plot.getAxis("left").setTextPen("w")
        self.display_plot.getAxis("bottom").setTextPen("w")

        self.graph_widget.nextRow()

        # Store plots in a list in case we need to add additional axes in the future.
        plots = [self.display_plot]

        # Create lines
        self.lines = {
            "pressure": self.plot(
                self.display_plot, [0, 10], [5, -5], "pressure", (0, 0, 0, 0)
            ),
            "flow": self.plot(
                self.display_plot,
                [0, 2, 4, 6, 8, 10],
                [3, 1, 4, 1, 5, 9],
                "flow",
                (0, 0, 0, 0),
            ),
        }

        # Store the colors of the lines
        self.colors = {"pressure": colors["plot_pressure"], "flow": colors["plot_flow"]}

        self.graph_widget.setContentsMargins(0.0, 0.0, 0.0, 0.0)
        self.graph_widget.setBackground(colors["page_background"])
        self.legends = []

        font = QtGui.QFont()  # TODO: change to an imported font from NativeuI
        font.setPixelSize(25)

        for plot in plots:
            plot.showGrid(x=True, y=True)
            plot.hideButtons()
            plot.setMouseEnabled(x=False, y=False)
            self.legends.append(plot.addLegend(offset=(-1, 1)))
            plot.getAxis("bottom").setStyle(tickFont=font)
            plot.getAxis("left").setStyle(tickFont=font)

        self.setLayout(layout)

        self.hide_line("pressure")
        self.show_line("pressure")

    def setFont(self, font: QtGui.QFont) -> int:
        for l in self.legends:
            l.setFont(font)
        return 0

    def update_plot_data(self):
        pass

    def plot(self, canvas, x, y, plotname, color):
        pen = pg.mkPen(color=color, width=3)
        return canvas.plot(x, y, name=plotname, pen=pen)

    @QtCore.Slot(str)
    def show_line(self, key: str) -> int:
        """
        Show the specified line
        """
        self.lines[key].setPen(pg.mkPen(color=self.colors[key], width=3))
        return 0

    @QtCore.Slot(str)
    def hide_line(self, key: str) -> int:
        """
        Hide the specified line
        """
        self.lines[key].setPen(pg.mkPen(color=(0, 0, 0, 0), width=0))
        return 0

    @QtCore.Slot(dict)
    def localise_text(self, text: dict) -> int:
        """
        Update the text displayed on the axis' and legend of time plots.

        Currently a placeholder.
        """
        self.display_plot.setLabel("left", text["plot_axis_label_pressure"])
        # self.display_plot.legend.clear()
        # self.display_plot.legend.addItem(
        #     self.pressure_line, text["plot_line_label_pressure"]
        # )

        return 0
