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
from datetime import datetime
from PySide2 import QtCore, QtGui, QtWidgets


class AlarmHandler(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(AlarmHandler, self).__init__(*args, **kwargs)
        self.NativeUI = NativeUI


        # self.setLayout(vlayout)
        self.alarmDict = {}
        self.oldAlarms = []


    def acknowledge_pressed(self):
        self.popup.clearAlarms()
        self.list.acknowledge_all()

    def update_alarms(self):
        currentAlarms = self.NativeUI.ongoingAlarms # instead of getting database at a particular frequency, this should be triggered when a new alarm arrives
        if self.oldAlarms != currentAlarms:
            if len(self.oldAlarms) != len(currentAlarms):
                self.oldAlarms = currentAlarms

        for alarm in currentAlarms:
            alarmCode = alarm["alarm_code"]
            if alarmCode in self.alarmDict:
                self.alarmDict[alarmCode].resetTimer()
                self.alarmDict[alarmCode].calculateDuration()
            else:
                newAbstractAlarm = AbstractAlarm(self.NativeUI, alarm)
                self.alarmDict[alarmCode] = newAbstractAlarm
                newAbstractAlarm.alarmExpired.connect(
                    lambda i=newAbstractAlarm: self.handleAlarmExpiry(i)
                )
                self.NativeUI.widgets.alarm_popup.addAlarm(newAbstractAlarm)
                self.NativeUI.widgets.alarm_list.addAlarm(newAbstractAlarm)
                self.NativeUI.widgets.alarm_table.addAlarmRow(newAbstractAlarm)

    def handleAlarmExpiry(self, abstractAlarm):
        abstractAlarm.freezeTimer()
        self.NativeUI.widgets.alarm_popup.removeAlarm(abstractAlarm)
        self.NativeUI.widgets.alarm_list.removeAlarm(abstractAlarm)
        self.alarmDict.pop(abstractAlarm.alarmPayload["alarm_code"])
        abstractAlarm.recordFinishTime()

class AbstractAlarm(QtWidgets.QWidget):

    alarmExpired = QtCore.Signal()

    def __init__(self, NativeUI, alarmPayload, *args, **kwargs):
        super(AbstractAlarm, self).__init__(*args, **kwargs)
        self.NativeUI = NativeUI
        self.alarmPayload = alarmPayload

        self.startTime = datetime.now()
        self.duration = datetime.now() - self.startTime
        self.finishTime = -1

        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)  # just faster than 60Hz
        self.timer.timeout.connect(self.timeoutDelete)
        self.timer.start()

    def timeoutDelete(self):
        # """Check alarm still exists in ongoingAlarms object. If present do nothing, otherwise delete."""
        self.alarmExpired.emit()
        self.setParent(None) # delete self
        return 0

    def resetTimer(self):
        self.timer.start()
        return 0

    def freezeTimer(self):
        self.timer.stop()
        return 0

    def recordFinishTime(self):
        self.finishTime = datetime.now()
        self.duration = self.finishTime - self.startTime

    def calculateDuration(self):
        self.duration = datetime.now() - self.startTime

