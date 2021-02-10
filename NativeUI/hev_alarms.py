import logging
import argparse
import sys

# from PySide2.QtCore import Slot
from PySide2 import QtWidgets, QtGui, QtCore

# from PySide2.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout
from hevclient import HEVClient
from alarm_widgets.tab_alarms import TabAlarm
from alarm_widgets.tab_clinical import TabClinical
from global_widgets.global_select_button import selectorButton


class AlarmView(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(AlarmView, self).__init__(*args, **kwargs)

        hTabLayout = QtWidgets.QHBoxLayout()
        self.alarmButton = selectorButton("List of Alarms")
        self.alarmButton.setProperty("selected", "1")
        self.alarmButton.style().polish(self.alarmButton)
        self.alarmButton.pressed.connect(self.alarmPressed)

        self.clinicalButton = selectorButton("Clinical Limits")
        # self.clinicalButton.setStyleSheet("")
        self.clinicalButton.pressed.connect(self.clinicalPressed)

        self.techButton = selectorButton("Technical Limits")
        # self.techButton.setStyleSheet("")

        self.buttonWidgets = [self.alarmButton, self.clinicalButton, self.techButton]
        for button in self.buttonWidgets:
            hTabLayout.addWidget(button)
            button.pressed.connect(lambda i=button: self.setColour(i))

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addLayout(hTabLayout)

        self.stack = QtWidgets.QStackedWidget()
        self.alarmTab = TabAlarm(NativeUI)
        self.stack.addWidget(self.alarmTab)
        self.clinicalTab = TabClinical()
        self.stack.addWidget(self.clinicalTab)
        # self.chartTab = TabChart()
        # self.stack.addWidget(self.chartTab)

        vlayout.addWidget(self.stack)
        self.setLayout(vlayout)

    def alarmPressed(self):
        self.stack.setCurrentWidget(self.alarmTab)

    def clinicalPressed(self):
        self.stack.setCurrentWidget(self.clinicalTab)

    def setColour(self, buttonWidg):
        for button in self.buttonWidgets:
            if button == buttonWidg:
                button.setProperty("selected", "1")
            else:
                button.setProperty("selected", "0")
            button.style().unpolish(button)
            button.style().polish(button)
