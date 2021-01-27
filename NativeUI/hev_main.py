import argparse
import logging
import sys

from hevclient import HEVClient
<<<<<<< HEAD
from main_widgets.tab_plots import TabPlots
from main_widgets.tab_buttons import TabButtons
from main_widgets.tab_spin import TabSpin
from main_widgets.tab_valueLabels import TabLabels
from main_widgets.customButton import customButton, spinRow
from main_widgets.alarmPopup import alarmPopup
=======
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget
from tab_measurements import TabMeasurements
from tab_page_buttons import TabPageButtons
from tab_plots import TabPlots
from tab_start_stop_standby_buttons import TabStartStopStandbyButtons
>>>>>>> origin/feature/UI_Measurements


class MainView(QWidget):
    def __init__(self, *args, **kwargs):
        super(MainView, self).__init__(*args, **kwargs)
        hlayout = QHBoxLayout()
        self.buttons = TabButtons()
        hlayout.addWidget(self.buttons)
        vlayout = QVBoxLayout()
        self.tab_plots = TabPlots()
        vlayout.addWidget(self.tab_plots)
        self.tab_spin = spinRow(self)
        vlayout.addWidget(self.tab_spin)
        hlayout.addLayout(vlayout)
        self.tab_label = TabLabels()
        hlayout.addWidget(self.tab_label)
        self.setLayout(hlayout)

        self.alarmHandler = alarmPopup(self)
        self.alarmHandler.show()
        # self.setStyleSheet('background-color: black')
        left_vlayout = QVBoxLayout()
        center_vlayout = QVBoxLayout()
        right_vlayout = QVBoxLayout()

        # Set up the widget tabs
        self.tab_plots = TabPlots()
        self.page_buttons = TabPageButtons()
        self.start_stop_standby_buttons = TabStartStopStandbyButtons()
        self.measurements = TabMeasurements()

        # left column - page buttons and start/stop/standby
        left_vlayout.addWidget(self.page_buttons)
        left_vlayout.addWidget(self.start_stop_standby_buttons)
        hlayout.addLayout(left_vlayout)

        # center column - plots
        center_vlayout.addWidget(self.tab_plots)
        hlayout.addLayout(center_vlayout)

        # right column - measurements
        right_vlayout.addWidget(self.measurements)
        hlayout.addLayout(right_vlayout)

        self.setLayout(hlayout)
