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

from alarm_widgets.alarm_popup import alarmPopup, abstractAlarm
from alarm_widgets.alarm_list import alarmList
from PySide2 import QtCore, QtGui, QtWidgets


class TabAlarm(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(TabAlarm, self).__init__(*args, **kwargs)
        self.NativeUI = NativeUI

        # self.alarmDict = {}

        self.popup = alarmPopup(NativeUI, self)
        self.popup.show()

        self.list = alarmList(NativeUI)
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self.list)

        self.acknowledgeButton = QtWidgets.QPushButton()
        self.acknowledgeButton.pressed.connect(self.acknowledge_pressed)
        vlayout.addWidget(self.acknowledgeButton)

        self.setLayout(vlayout)
        self.alarmDict = {}
        # fdd
        # self.timer = QtCore.QTimer()
        # self.timer.setInterval(160)
        # self.timer.timeout.connect(self.updateAlarms)
        # self.timer.start()

    def acknowledge_pressed(self):
        self.popup.clearAlarms()
        self.list.acknowledge_all()

    def update_alarms(self):
        print('here')
        newAlarmPayload = self.NativeUI.get_db("alarms")
        if newAlarmPayload == []:
            return
        if newAlarmPayload["alarm_code"] in self.alarmDict:
            a = 1
            self.alarmDict[newAlarmPayload["alarm_code"]].resetTimer()
            self.alarmDict[newAlarmPayload["alarm_code"]].calculateDuration()
        else:
            newAbstractAlarm = abstractAlarm(self.NativeUI, newAlarmPayload)
            self.alarmDict[newAlarmPayload["alarm_code"]] = newAbstractAlarm
            newAbstractAlarm.alarmExpired.connect(
                lambda i=newAbstractAlarm: self.handleAlarmExpiry(i)
            )
            self.popup.addAlarm(newAbstractAlarm)
            self.list.addAlarm(newAbstractAlarm)
            self.NativeUI.widgets.alarm_table_tab.table.addAlarmRow(newAbstractAlarm)

    def handleAlarmExpiry(self, abstractAlarm):
        abstractAlarm.freezeTimer()
        self.popup.removeAlarm(abstractAlarm)
        self.list.removeAlarm(abstractAlarm)
        self.alarmDict.pop(abstractAlarm.alarmPayload["alarm_code"])
        abstractAlarm.recordFinishTime()
