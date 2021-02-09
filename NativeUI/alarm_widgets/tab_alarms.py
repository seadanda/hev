import sys

from alarm_widgets.alarmPopup import alarmPopup
from PySide2 import QtCore, QtGui, QtWidgets

path = "/home/pi/Documents/hev/hev-display/assets/svg/"


class alarmList(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(alarmList, self).__init__(*args, **kwargs)

        self.labelList = []
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.setStyleSheet("background-color:white; font:15pt white;")
        self.solidBell = QtGui.QIcon(path + "bell-solid.svg")
        self.regularBell = QtGui.QIcon(path + "bell-regular.svg")

        self.vlayout = QtWidgets.QVBoxLayout()
        self.alarmList = QtWidgets.QListWidget()
        self.alarmList.addItem("ring the alarm")
        self.alarmList.addItem("alarm the ring")
        self.vlayout.addWidget(self.alarmList)
        self.setLayout(self.vlayout)
        self.alarmList.itemClicked.connect(self.selected)

    def selected(self):
        items = self.test.selectedItems()
        for item in items:
            item.setText("newtestText")
            item.setIcon(self.regularBell)

    def acknowledge_all(self):
        for x in range(self.alarmList.count() - 1):
            self.alarmList.item(x).setText("acknowledgedAlarm")
            self.alarmList.item(x).setIcon(self.regularBell)

    def addAlarm(self, alarmPayload):
        newItem = QtWidgets.QListWidgetItem(self.solidBell, alarmPayload["alarm_code"])
        self.alarmList.insertItem(0, newItem)  # add to the top


class TabAlarm(
    QtWidgets.QWidget
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, *args, **kwargs):
        super(TabAlarm, self).__init__(*args, **kwargs)

        self.alarmHandler = alarmPopup(self)
        self.alarmHandler.show()

        self.list = alarmList()
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self.list)

        self.acknowledgeButton = QtWidgets.QPushButton()
        self.acknowledgeButton.pressed.connect(self.acknowledge_pressed)
        vlayout.addWidget(self.acknowledgeButton)

        self.setLayout(vlayout)
        self.existingAlarms = []

        self.timer = QtCore.QTimer()
        self.timer.setInterval(160)  # just faster than 60Hz
        self.timer.timeout.connect(self.updateAlarms)
        self.timer.start()

    def acknowledge_pressed(self):
        self.existingAlarms = []
        self.alarmHandler.clearAlarms()
        self.list.acknowledge_all()

    def updateAlarms(self):
        newAlarm = self.parent().parent().parent().parent().parent().alarms
        if newAlarm == []:
            return
        if newAlarm["alarm_code"] in self.alarmHandler.alarmDict:
            self.alarmHandler.resetTimer(newAlarm)
            a = 1  # do nothing
        else:
            self.alarmHandler.addAlarm(newAlarm)
            # self.existingAlarms.append(newAlarm["alarm_code"])
            self.list.addAlarm(newAlarm)
