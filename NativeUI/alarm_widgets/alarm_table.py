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


class AlarmTable(QtWidgets.QTableWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(AlarmTable, self).__init__(*args, **kwargs)

        self.alarmDict = {}
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.setStyleSheet("background-color:white;")
        self.setFont(NativeUI.text_font)
        self.nrows = 0
        self.setColumnCount(4)
        self.setSortingEnabled(True)

        if self.nrows == 0:
            self.setHorizontalHeaderLabels(
                ["Timestamp", "Priority Level", "Alarm Code", "Duration"]
            )

        self.payloadKeys = ["alarm_type", "alarm_code"]
        self.resizeColumnsToContents()

        self.alarmDict = {}
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        # self.timer.timeout.connect(self.updateDuration)
        self.timer.start()

    def addAlarm(self, abstractAlarm):
        timestamp = str(datetime.now())[:-3]
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

        # widg = self.cellWidget(rowNumber, 4)
        # cellItem.setText(str(abstractAlarm.duration))
        #     abstractAlarm.alarmExpired.connect(lambda i =newItem, j = abstractAlarm: self.update_duration(i,j))
        #     self.setItem(self.nrows, colnum, newItem)
        # tableItem.setText(str(abstractAlarm.duration))

    def removeAlarm(self, abstractAlarm):
        for x in range(self.count() - 1):
            if abstractAlarm.alarmPayload["alarm_code"] in self.item(x).text():
                self.takeItem(x)

    def addAlarmRow(self, abstractAlarm):
        self.setSortingEnabled(False)
        self.setRowCount(self.nrows + 1)
        colnum = 0

        newItem = QtWidgets.QTableWidgetItem(str(abstractAlarm.startTime)[:-3])
        self.setItem(self.nrows, 0, newItem)

        newItem = QtWidgets.QTableWidgetItem(abstractAlarm.alarmPayload["alarm_type"])
        self.setItem(self.nrows, 1, newItem)

        newItem = QtWidgets.QTableWidgetItem(abstractAlarm.alarmPayload["alarm_code"])
        self.setItem(self.nrows, 2, newItem)

        newItem = QtWidgets.QTableWidgetItem(" ")
        self.alarmDict[self.nrows] = newItem
        self.setItem(self.nrows, 3, self.alarmDict[self.nrows])
        # abstractAlarm.alarmExpired.connect(lambda i = self.alarmDict[self.nrows], j = abstractAlarm: self.update_duration(i,j))
        self.timer.timeout.connect(
            lambda i=self.alarmDict[self.nrows], j=abstractAlarm: self.update_duration(
                i, j
            )
        )

        if self.nrows == 1:
            self.resizeColumnsToContents()
        self.nrows = self.nrows + 1
        self.setSortingEnabled(True)

    def update_duration(self, cellItem, abstractAlarm):
        cellItem.setText(str(abstractAlarm.duration))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widg = alarmList()
    widg.show()
    sys.exit(app.exec_())
