import sys
import os
from PySide2 import QtCore, QtGui, QtWidgets

path = "/home/pi/Documents/hev/hev-display/assets/svg/"


class alarmList(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(alarmList, self).__init__(*args, **kwargs)

        self.labelList = []
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.setStyleSheet("background-color:white; font:15pt white;")
        
        iconpath_bell = os.path.join(NativeUI.iconpath, "bell-solid.png") 
        iconpath_bellReg = os.path.join(NativeUI.iconpath, "bell-regular.png") 

        self.solidBell = QtGui.QIcon(iconpath_bell)
        self.regularBell = QtGui.QIcon(iconpath_bellReg)

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



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widg = alarmList()
    widg.show()
    sys.exit(app.exec_())
