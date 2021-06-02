#!/usr/bin/env python3

"""
tab_alarms.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

import sys

#from alarm_widgets.alarm_popup import alarmPopup, abstractAlarm
from alarm_widgets.alarm_table import alarmTable
from PySide2 import QtCore, QtGui, QtWidgets


class TabAlarmTable(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(TabAlarmTable, self).__init__(*args, **kwargs)
        self.NativeUI = NativeUI


        self.table = alarmTable(NativeUI)
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self.table)

        self.acknowledgeButton = QtWidgets.QPushButton('table button')
        #self.acknowledgeButton.pressed.connect(self.acknowledge_pressed)
        vlayout.addWidget(self.acknowledgeButton)

        self.setLayout(vlayout)