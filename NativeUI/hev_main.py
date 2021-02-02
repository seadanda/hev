import argparse
import logging
import sys

from hevclient import HEVClient
from main_widgets.tab_buttons import TabButtons
from main_widgets.tab_measurements import TabMeasurements
from main_widgets.tab_page_buttons import TabPageButtons
from main_widgets.tab_plots import TabPlots
from main_widgets.tab_spin import TabSpin
# from main_widgets.alarmPopup import alarmPopup
from main_widgets.tab_spin_buttons import TabSpinButtons
from main_widgets.tab_start_stop_buttons import TabStartStopStandbyButtons
from main_widgets.tab_valueLabels import TabLabels
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget


class MainView(QWidget):
    def __init__(self, *args, **kwargs):
        super(MainView, self).__init__(*args, **kwargs)

        hlayout = QHBoxLayout()

        # self.setStyleSheet('background-color: black')
        left_vlayout = QVBoxLayout()
        center_vlayout = QVBoxLayout()
        right_vlayout = QVBoxLayout()

        # Set up the widget tabs
        self.tab_plots = TabPlots()
        # self.page_buttons = TabPageButtons()
        self.start_stop_standby_buttons = TabStartStopStandbyButtons()
        self.measurements = TabMeasurements()

        # left column - page buttons and start/stop/standby
        # left_vlayout.addWidget(self.page_buttons)
        left_vlayout.addWidget(self.start_stop_standby_buttons)
        hlayout.addLayout(left_vlayout)

        # center column - plots
        center_vlayout.addWidget(self.tab_plots)
        self.tab_spin = TabSpinButtons(self)
        center_vlayout.addWidget(self.tab_spin)
        hlayout.addLayout(center_vlayout)

        # right column - measurements
        right_vlayout.addWidget(self.measurements)
        hlayout.addLayout(right_vlayout)

        self.setLayout(hlayout)
