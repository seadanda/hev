import logging
import argparse
import sys

# from PySide2.QtCore import Slot
from PySide2 import QtWidgets, QtGui, QtCore

# from PySide2.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout
from hevclient import HEVClient
from settings_widgets.customLabelTab import labelTab


class SettingsView(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(SettingsView, self).__init__(*args, **kwargs)

        hlayout = QtWidgets.QHBoxLayout()
        # self.buttons = QtWidgets.QPushButton()
        self.test = labelTab()
        # self.buttons = TabButtons()
        hlayout.addWidget(self.test)
        # vlayout = QVBoxLayout()
        # self.tab_plots = TabPlots()
        # vlayout.addWidget(self.tab_plots)
        # self.tab_spin = spinRow(self)
        # vlayout.addWidget(self.tab_spin)
        # hlayout.addLayout(vlayout)
        # self.tab_label = TabLabels()
        # hlayout.addWidget(self.tab_label)
        self.setLayout(hlayout)

    #        self.buttons.pressed.connect(self.change)
    # self.alarmHandler = alarmPopup(self)
    # self.alarmHandler.show()
    # self.setStyleSheet('background-color: black')

    def change(self):
        print("pressed")
        self.parent().setCentralWidget(self.parent().main_view)

        # self.setCentralWidget(self.settings_view)
