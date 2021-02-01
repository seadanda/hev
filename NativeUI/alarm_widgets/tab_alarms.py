from PySide2 import QtWidgets, QtGui, QtCore
import sys
from alarm_widgets.alarmPopup import alarmPopup

path = "/home/pi/Documents/hev/hev-display/assets/svg/"
class alarmList(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(alarmList, self).__init__(*args, **kwargs)

        self.labelList = []
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.setStyleSheet("background-color:white; font:15pt white;")
        self.solidBell = QtGui.QIcon(path + 'bell-solid.svg')
        self.regularBell = QtGui.QIcon(path + 'bell-regular.svg')
        #self.activeItems = []
        self.vlayout = QtWidgets.QVBoxLayout()
        #self.test = QtWidgets.QLabel('etst labe')
        self.test = QtWidgets.QListWidget()
        self.test.addItem("ring the alarm")
        self.test.addItem("and the sound is dying")
        self.vlayout.addWidget(self.test)
        self.setLayout(self.vlayout)
        self.test.itemClicked.connect(self.selected)

    def selected(self):
        items = self.test.selectedItems()
        for item in items:
            item.setText('newtestText')
            item.setIcon(self.regularBell)


    def acknowledge_all(self):
        for x in range(self.test.count()-1):
            self.test.item(x).setText('newtestTextinnit')
            self.test.item(x).setIcon(self.regularBell)


    def addAlarm(self, alarmPayload):
        print('adding alrm')
        #label = QtWidgets.QLabel('alarmPayload["alarm_code"]')
        newItem = QtWidgets.QListWidgetItem(self.solidBell,alarmPayload["alarm_code"])
        #newItem.setIcon(self.solidBell)
        #newItem.set()
        self.test.insertItem(0,newItem)
        #self.labelList.append(label)
        #self.vlayout.addWidget(label)
        #self.setLayout(self.vlayout)
        #labelList = labelList + [alarmPayload["alarm_code"]]


class TabAlarm(
    QtWidgets.QWidget
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, *args, **kwargs):
        super(TabAlarm, self).__init__(*args, **kwargs)

        self.alarmHandler = alarmPopup(self)
        self.alarmHandler.show()

        self.list = alarmList()
        #elf.list.setSizeHint(self.sizeHint())
        #self.scroll = QtWidgets.QScrollArea()
        #self.scroll.setWidget(self.list)
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self.list)
        self.acknowledgeButton = QtWidgets.QPushButton()
        self.acknowledgeButton.pressed.connect(self.acknowledge_pressed)
        vlayout.addWidget(self.acknowledgeButton)
        #vlayout.addWidget(self.scroll)
        self.setLayout(vlayout)
        self.existingAlarms = []

        self.timer = QtCore.QTimer()
        self.timer.setInterval(160)  # just faster than 60Hz
        self.timer.timeout.connect(self.updateAlarms)
        self.timer.start()

    # def addAlarm(self,alarmPayload):
    #     self.scroll.setWid

    def acknowledge_pressed(self):
        self.list.acknowledge_all()

    def updateAlarms(self):
        newAlarm = self.parent().parent().parent().alarms
        if newAlarm == []:
            return
        if newAlarm["alarm_code"] in self.existingAlarms:
            a = 1  # do nothing
        else:
            self.alarmHandler.addAlarm(newAlarm)
            self.existingAlarms.append(newAlarm["alarm_code"])
        self.list.addAlarm(newAlarm)
        #self.show()

# def update_alarm_list(self):
#    self.
