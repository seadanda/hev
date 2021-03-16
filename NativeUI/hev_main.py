#!/usr/bin/env python3

"""
hev_main.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Benjamin Mummery"
__email__ = "benjamin.mummery@stfc.ac.uk"
__status__ = "Development"

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2.QtCore import QSize, Slot
import numpy as np
from main_widgets.tab_measurements import TabMeasurements
from main_widgets.tab_plots import TabPlots
from main_widgets.tab_spin_buttons import TabSpinButtons
from main_widgets.tab_history_buttons import TabHistoryButtons
from main_widgets.tab_expert_plots import TabExpertPlots
from PySide2.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

# TODO move accessing plot data to this page so we only do it once.


class MainView(QWidget):
    """
    Docstring [TODO]
    """

    def __init__(self, NativeUI, *args, **kwargs):
        super(MainView, self).__init__(*args, **kwargs)

        hlayout = QHBoxLayout()

        center_vlayout = QVBoxLayout()
        bottom_layout = QHBoxLayout()

        # Set up the widget tabs
        self.stack = QStackedWidget(self)
        self.tab_expert_plots = TabExpertPlots(NativeUI)
        self.tab_spin = TabSpinButtons(NativeUI)
        self.tab_history_buttons = TabHistoryButtons(NativeUI)
        self.tab_normal_expert_buttons = TabNormalExpertButtons(NativeUI)
        self.tab_normal_plots_view = TabNormalPlotsView(NativeUI)

        # Get references to the widgets
        self.tab_plots = self.tab_normal_plots_view.tab_plots

        # Bottom bar -
        bottom_layout.addWidget(self.tab_history_buttons)
        bottom_layout.addWidget(self.tab_spin)

        # stack layout
        self.stack.addWidget(self.tab_normal_plots_view)
        self.stack.addWidget(self.tab_expert_plots)
        center_vlayout.addWidget(self.tab_normal_expert_buttons)
        center_vlayout.addWidget(self.stack)
        center_vlayout.addLayout(bottom_layout)
        hlayout.addLayout(center_vlayout)

        self.setLayout(hlayout)

        self.tab_normal_expert_buttons.normal_button.pressed.connect(
            self.switch_to_normal
        )
        self.tab_normal_expert_buttons.expert_button.pressed.connect(
            self.switch_to_expert
        )
        self.switch_to_normal()

        for button in self.tab_history_buttons.buttons:
            button.HistoryButtonPressed.connect(self.tab_plots.update_plot_time_range)
            button.HistoryButtonPressed.connect(
                self.tab_expert_plots.update_plot_time_range
            )

    @Slot()
    def get_plot_data(self):
        plots = self.NativeUI.get_plots_db()
        timestamp = np.true_divide(np.subtract(plots[:, 0], plots[-1, 0]), 1000)
        pressure = plots[:, 1]
        flow = plots[:, 2]
        volume = [v / (10 ** self.__PID_I_scale) for v in plots[:, 3]]

    @Slot()
    def switch_to_normal(self):
        """
        raise the normal plots view
        """
        self.stack.setCurrentWidget(self.tab_normal_plots_view)
        for button in self.tab_normal_expert_buttons.buttons:
            button.setEnabled(True)
        self.tab_normal_expert_buttons.normal_button.setEnabled(False)

    @Slot()
    def switch_to_expert(self):
        """
        raise the detailed plots view
        """
        self.stack.setCurrentWidget(self.tab_expert_plots)
        for button in self.tab_normal_expert_buttons.buttons:
            button.setEnabled(True)
        self.tab_normal_expert_buttons.expert_button.setEnabled(False)


class PlotDataManager:
    def __init__(self, NativeUI, *args, **kwargs):
        self.NativeUI = NativeUI

        self.properties = {"timestamp": [], "pressure": [], "flow": [], "volume": []}

        self.pressure_range = NativeUI.plots["plot_axis_range_pressure"]
        self.flow_range = NativeUI.plots["plot_axis_range_flow"]
        self.volume_range = NativeUI.plots["plot_axis_range_volume"]

        self.__plotlist = []

    def add_plot(self, plot, x_property, y_property):
        pass

    def update_data(self):
        plots = self.NativeUI.get_plots_db()

        self.properties["timestamp"] = np.true_divide(
            np.subtract(plots[:, 0], plots[-1, 0]), 1000
        )
        self.properties["pressure"] = plots[:, 1]
        self.properties["flow"] = plots[:, 2]
        self.properties["volume"] = [
            v / (10 ** self.NativeUI.PID_I_plot_scale) for v in plots[:, 3]
        ]

        self.check_ranges()
        return 0

    def check_ranges(self):
        """
        Check that the current values of p
        """
        update_ranges = False
        p_min = min(self.properties["pressure"])
        p_max = max(self.properties["pressure"])
        f_min = min(self.properties["flow"])
        f_max = max(self.properties["flow"])
        v_min = min(self.properties["volume"])
        v_max = max(self.properties["volume"])

        if p_min < self.pressure_range[0]:
            self.pressure_range[0] = p_min
            update_ranges = True
        if p_max > self.pressure_range[1]:
            self.pressure_range[1] = p_max
            update_ranges = True
        if f_min < self.flow_range[0]:
            self.flow_range[0] = f_min
            update_ranges = True
        if f_max > self.flow_range[1]:
            self.flow_range[1] = f_max
            update_ranges = True
        if v_min < self.volume_range[0]:
            self.volume_range[0] = v_min
            update_ranges = True
        if v_max > self.volume_range[1]:
            self.volume_range[1] = v_max
            update_ranges = True

        if update_ranges:
            self.update_ranges()

        return 0


class TabNormalExpertButtons(QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        button_size = QSize(150, 50)
        self.NativeUI = NativeUI
        layout = QHBoxLayout()
        self.normal_button = QPushButton("Normal")
        self.expert_button = QPushButton("Detailed")
        self.buttons = [self.normal_button, self.expert_button]
        layout.addWidget(self.normal_button)
        layout.addWidget(self.expert_button)
        # layout.setAlignment(self.normal_button, QtCore.Qt.AlignLeft)
        # layout.setAlignment(self.expert_button, QtCore.Qt.AlignLeft)
        self.setLayout(layout)

        for button in self.buttons:
            button.setStyleSheet(
                "QPushButton{"
                "   color: " + NativeUI.colors["foreground"].name() + ";"
                "   font-size: " + NativeUI.text_size + ";"
                "   background-color: "
                + NativeUI.colors["background-enabled"].name()
                + ";"
                "   border-color: " + NativeUI.colors["background"].name() + ";"
                "   border:none"
                "}"
                "QPushButton:disabled{"
                "   background-color: "
                + NativeUI.colors["background-disabled"].name()
                + ";"
                "   border:none"
                "}"
            )
            button.setFixedSize(button_size)


class TabNormalPlotsView(QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QHBoxLayout()

        self.tab_plots = TabPlots(NativeUI)
        self.tab_measurements = TabMeasurements(NativeUI)

        layout.addWidget(self.tab_plots)
        layout.addWidget(self.tab_measurements)

        self.setLayout(layout)
