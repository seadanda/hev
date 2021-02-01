import logging
import argparse
import sys

# from PySide2.QtCore import Slot
from PySide2 import QtWidgets, QtGui, QtCore

# from PySide2.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout
from hevclient import HEVClient
from settings_widgets.tab_expert import TabExpert
from settings_widgets.tab_charts import TabChart


class SettingsView(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(SettingsView, self).__init__(*args, **kwargs)

        hTabLayout = QtWidgets.QHBoxLayout()
        self.alarmButton = QtWidgets.QPushButton("List of Alarms")
        self.alarmButton.setStyleSheet("")
        self.alarmButton.pressed.connect(self.alarmPressed)
        hTabLayout.addWidget(self.alarmButton)
        self.clinicalButton = QtWidgets.QPushButton("Clinical Limits")
        self.clinicalButton.setStyleSheet("")
        self.clinicalButton.pressed.connect(self.clinicalPressed)
        hTabLayout.addWidget(self.clinicalButton)
        self.techButton = QtWidgets.QPushButton("Technical Limits")
        self.techButton.setStyleSheet("")
        hTabLayout.addWidget(self.techButton)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addLayout(hTabLayout)

        self.stack = QtWidgets.QStackedWidget()
        self.alarmTab = TabAlarm()
        self.stack.addWidget(self.expertTab)
        # self.chartTab = TabChart()
        # self.stack.addWidget(self.chartTab)

        vlayout.addWidget(self.stack)
        self.setLayout(vlayout)
