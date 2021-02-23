import sys

from alarm_widgets.alarm_popup import alarmPopup
from alarm_widgets.alarm_list import alarmList
from PySide2 import QtCore, QtGui, QtWidgets

path = "/home/pi/Documents/hev/hev-display/assets/svg/"


class TabAlarm(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(TabAlarm, self).__init__(*args, **kwargs)
        self.NativeUI = NativeUI

        self.popup = alarmPopup(NativeUI,self)
        self.popup.show()

        self.list = alarmList(NativeUI)
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self.list)

        self.acknowledgeButton = QtWidgets.QPushButton()
        self.acknowledgeButton.pressed.connect(self.acknowledge_pressed)
        vlayout.addWidget(self.acknowledgeButton)

        self.setLayout(vlayout)
        # fdd
        self.timer = QtCore.QTimer()
        self.timer.setInterval(160)  # just faster than 60Hz
        self.timer.timeout.connect(self.updateAlarms)
        self.timer.start()

    def acknowledge_pressed(self):
        self.popup.clearAlarms()
        self.list.acknowledge_all()

    def updateAlarms(self):
        newAlarm = self.NativeUI.get_alarms_db()
        if newAlarm == []:
            return
        if newAlarm["alarm_code"] in self.popup.alarmDict:
            self.popup.resetTimer(newAlarm)
        else:
            self.popup.addAlarm(newAlarm)
            self.list.addAlarm(newAlarm)
