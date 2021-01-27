import logging
import argparse
import sys
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout
from hevclient import HEVClient
from main_widgets.tab_plots import TabPlots
from main_widgets.tab_buttons import TabButtons
from main_widgets.tab_spin import TabSpin
from main_widgets.tab_valueLabels import TabLabels
from main_widgets.customButton import customButton, spinRow
from main_widgets.alarmPopup import alarmPopup


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
