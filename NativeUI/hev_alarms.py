#!/usr/bin/env python3

"""
hev_alarms.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

from alarm_widgets.tab_alarms import TabAlarm
from alarm_widgets.tab_alarm_table import TabAlarmTable
from alarm_widgets.tab_clinical import TabClinical
from global_widgets.global_select_button import selectorButton
from global_widgets.template_main_pages import TemplateMainPages
from alarm_widgets.alarm_popup import abstractAlarm
from PySide2 import QtCore


class AlarmView(TemplateMainPages):
    """Subclasses TemplateMainPages to display alarms."""

    def __init__(self, NativeUI, *args, **kwargs):
        super(AlarmView, self).__init__(*args, **kwargs)

        self.NativeUI = NativeUI

        self.alarmButton = selectorButton(NativeUI, "List of Alarms")
        self.alarmTableButton = selectorButton(NativeUI, "Alarm Table")
        self.clinicalButton = selectorButton(NativeUI, "Clinical Limits")
        # self.techButton = selectorButton(NativeUI, "Technical Limits")

        self.buttonWidgets = [
            self.alarmButton,
            self.alarmTableButton,
            self.clinicalButton,
        ]  # , self.techButton]

        self.alarmTab = TabAlarm(NativeUI)
        self.alarmTableTab = TabAlarmTable(NativeUI)
        self.clinicalTab = TabClinical(NativeUI)
        # self.technicalTab = TabClinical(NativeUI)
        self.tabsList = [
            self.alarmTab,
            self.alarmTableTab,
            self.clinicalTab,
        ]  # , self.technicalTab]
        self.buildPage(self.buttonWidgets, self.tabsList)

        self.alarmDict = {}
        self.timer = QtCore.QTimer()
        self.timer.setInterval(300)
        self.timer.timeout.connect(self.updateAlarms)
        self.timer.start()

    def updateAlarms(self):
        print("attempting new alarms")
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
            self.alarmTab.popup.addAlarm(newAbstractAlarm)
            self.alarmTab.list.addAlarm(newAbstractAlarm)
            self.alarmTableTab.table.addAlarmRow(newAbstractAlarm)

    def handleAlarmExpiry(self, abstractAlarm):
        abstractAlarm.freezeTimer()
        self.alarmTab.popup.removeAlarm(abstractAlarm)
        self.alarmTab.list.removeAlarm(abstractAlarm)
        self.alarmDict.pop(abstractAlarm.alarmPayload["alarm_code"])
        abstractAlarm.recordFinishTime()
