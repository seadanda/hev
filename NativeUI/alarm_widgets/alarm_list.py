#!/usr/bin/env python3

"""
alarm_list.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

import sys
import os
from PySide2 import QtCore, QtGui, QtWidgets
from datetime import datetime


class AlarmList(QtWidgets.QListWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(AlarmList, self).__init__(*args, **kwargs)

        self.labelList = []
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.setStyleSheet("background-color:white;")
        self.setFont(NativeUI.text_font)

        iconpath_bell = os.path.join(NativeUI.iconpath, "bell-solid.png")
        iconpath_bellReg = os.path.join(NativeUI.iconpath, "bell-regular.png")

        self.solidBell = QtGui.QIcon(iconpath_bell)
        self.regularBell = QtGui.QIcon(iconpath_bellReg)

        newItem = QtWidgets.QListWidgetItem(" ")
        self.addItem(newItem)

    def acknowledge_all(self):
        for x in range(self.count() - 1):
            self.item(x).setText("acknowledgedAlarm")
            self.item(x).setIcon(self.regularBell)

    def addAlarm(self, abstractAlarm):
        timestamp = str(abstractAlarm.startTime)[:-3]
        newItem = QtWidgets.QListWidgetItem(
            self.solidBell,
            timestamp
            + ": "
            + abstractAlarm.alarmPayload["alarm_type"]
            + " - "
            + abstractAlarm.alarmPayload["alarm_code"],
        )
        self.insertItem(0, newItem)  # add to the top
        # self.labelList

    def removeAlarm(self, abstractAlarm):
        for x in range(self.count() - 1):
            if abstractAlarm.alarmPayload["alarm_code"] in self.item(x).text():
                self.takeItem(x)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widg = alarmList()
    widg.show()
    sys.exit(app.exec_())
