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

from handler_library.handler import PayloadHandler
import logging

class AlarmHandler(PayloadHandler):

    UpdateAlarm = QtCore.Signal(dict)
    NewAlarm = QtCore.Signal(QtWidgets.QWidget)
    RemoveAlarm = QtCore.Signal(QtWidgets.QWidget)

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(['DATA', 'ALARM'],*args, **kwargs)
        self.NativeUI = NativeUI

        self.alarmDict = {}
        self.alarm_list = []
        self.oldAlarms = []

    def acknowledge_pressed(self):
        self.popup.clearAlarms()
        self.list.acknowledge_all()

    def _set_alarm_list(self, alarm_list:list):
        self.alarm_list = alarm_list

    def active_payload(self, *args) -> int:
        #alarm_data = self.get_db()
        #outdict = {}

        full_payload = args[0]
        #print(full_payload['alarms'])
        currentAlarms = full_payload['alarms']#self.NativeUI.ongoingAlarms  # instead of getting database at a particular frequency, this should be triggered when a new alarm arrives
        self.alarm_list = currentAlarms
        #self._set__alarm_list(currentAlarms)
        if self.oldAlarms != currentAlarms:
            if len(self.oldAlarms) != len(currentAlarms):
                self.oldAlarms = currentAlarms

        self.UpdateAlarm.emit(currentAlarms)

    def handle_newAlarm(self, currentAlarms): # if this is combined with active_payload an error arises
        for alarm in currentAlarms:
            alarmCode = alarm["alarm_code"]
            if alarmCode in self.alarmDict:
                self.alarmDict[alarmCode].resetTimer()
                self.alarmDict[alarmCode].calculateDuration()
            else:
                newAbstractAlarm = AbstractAlarm(self.NativeUI, alarm)
                self.alarmDict[alarmCode] = newAbstractAlarm
                self.NewAlarm.emit(newAbstractAlarm)
                newAbstractAlarm.alarmExpired.connect(
                    lambda i=newAbstractAlarm: self.handleAlarmExpiry(i)
                )

    def handleAlarmExpiry(self, abstractAlarm):
        abstractAlarm.freezeTimer()
        abstractAlarm.recordFinishTime()
        self.RemoveAlarm.emit(abstractAlarm)
        self.alarmDict.pop(abstractAlarm.alarmPayload["alarm_code"])
        # abstractAlarm is deleted by itself


class AbstractAlarm(QtCore.QObject):

    alarmExpired = QtCore.Signal()

    def __init__(self, NativeUI, alarmPayload, *args, **kwargs):
        super(AbstractAlarm, self).__init__(*args, **kwargs)
        self.NativeUI = NativeUI
        self.alarmPayload = alarmPayload

        self.startTime = datetime.now()
        self.duration = datetime.now() - self.startTime
        self.finishTime = -1

        self.timer = QtCore.QTimer()
        self.timer.setInterval(2000)  # just faster than 60Hz
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

