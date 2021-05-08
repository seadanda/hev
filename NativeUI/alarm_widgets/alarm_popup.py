#!/usr/bin/env python3

"""
alarm_popup.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

import os
from PySide2 import QtCore, QtGui, QtWidgets
from datetime import datetime


class AlarmWidget(QtWidgets.QWidget):
    """Object containing information particular to one alarm.
    Created when alarm received from microcontroller, timeout after alarm signal stops.
    Is contained within alarmPopup"""

    def __init__(self, NativeUI, abstractAlarm, alarmCarrier, *args, **kwargs):
        super(AlarmWidget, self).__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        self.alarmCarrier = alarmCarrier  # Needs to refer to its containing object

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setMargin(0)
        self.alarmPayload = abstractAlarm.alarmPayload

        iconLabel = QtWidgets.QLabel()
        iconpath_check = os.path.join(
            self.NativeUI.iconpath, "exclamation-triangle-solid.png"
        )
        pixmap = QtGui.QPixmap(iconpath_check).scaledToHeight(40)
        iconLabel.setPixmap(pixmap)
        self.layout.addWidget(iconLabel)

        self.textLabel = QtWidgets.QLabel()
        self.textLabel.setText(
            self.alarmPayload["alarm_type"] + " - " + self.alarmPayload["alarm_code"]
        ) #remove priority_
        self.textLabel.setFixedWidth(400)
        self.textLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.textLabel.setFont(NativeUI.text_font)
        #self.textLabel.setStyleSheet("font-size: " + NativeUI.text_size + ";")
        self.layout.addWidget(self.textLabel)

        self.setFixedHeight(40)
        self.setLayout(self.layout)
        if self.alarmPayload["alarm_type"] == "PRIORITY_HIGH":
            self.setStyleSheet("background-color:red;")
        elif self.alarmPayload["alarm_type"] == "PRIORITY_MEDIUM":
            self.setStyleSheet("background-color:orange;")

        # self.timer = QtCore.QTimer()
        # self.timer.setInterval(500)  # just faster than 60Hz
        # self.timer.timeout.connect(self.checkAlarm)
        # self.timer.start()
        # self.installEventFilter(self)

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseButtonPress):
            self.NativeUI.leftBar.tab_page_buttons.button_alarms.click()
            self.NativeUI.alarms_view.alarmButton.click()
        return False

    def get_priority(self):
        return self.alarmPayload["alarm_type"]


    def setFont(self, font) -> int:
        """
        Set the font for textLabel.
        """
        self.textLabel.setFont(font)
        return 0

    # def checkAlarm(self):
    #     """Check alarm still exists in ongoingAlarms object. If present do nothing, otherwise delete."""
    #     self.ongoingAlarms = self.NativeUI.ongoingAlarms
    #     for alarm in self.ongoingAlarms:
    #         if self.alarmPayload["alarm_code"] == alarm["alarm_code"]:
    #             return
    #     self.alarmCarrier.alarmDict.pop(self.alarmPayload["alarm_code"])
    #     self.setParent(None) # delete self
    #     return 0


class AlarmPopup(QtWidgets.QDialog):
    """Container class for alarm widgets. Handles ordering and positioning of alarms.
    Needs to adjust its size whenever a widget is deleted"""
    def __init__(self, NativeUI, *args, **kwargs):
        super(AlarmPopup, self).__init__(*args, **kwargs)
        self.setParent(NativeUI)  # ensures popup closes when main UI does
        self.alarmDict = {}
        self.NativeUI = NativeUI
        self.extraAlarms = AlarmExtrasWidget(NativeUI,self)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setMargin(0)
        self.setLayout(self.layout)

        self.location_on_window()
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.Dialog
            | QtCore.Qt.WindowStaysOnTopHint
        )  # no window title

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(10)
        self.shadow.setYOffset(10)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)  # just faster than 60Hz
        self.timer.timeout.connect(self.adjustSize)
        self.timer.start()

        self.show()

    def clearAlarms(self):
        """Wipe all alarms out and clear dictionary"""
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        self.adjustSize()
        self.setLayout(self.layout)
        self.alarmDict = {}
        return 0

    def addAlarm(self, abstractAlarm):
        """Creates a new alarmWidget and adds it to the container"""
        self.alarmDict[abstractAlarm.alarmPayload["alarm_code"]] = AlarmWidget(
            self.NativeUI, abstractAlarm, self
        )
        self.refresh_alarm_ordering()
        #self.layout.addWidget(self.alarmDict[abstractAlarm.alarmPayload["alarm_code"]])
        return 0

    def removeAlarm(self, abstractAlarm):
        """Creates a new alarmWidget and adds it to the container"""
        self.alarmDict[abstractAlarm.alarmPayload["alarm_code"]].setParent(None)
        self.alarmDict.pop(abstractAlarm.alarmPayload["alarm_code"])
        self.refresh_alarm_ordering()
        return 0

    def refresh_alarm_ordering(self):
        self.layout.removeWidget(self.extraAlarms)
        for key in self.alarmDict:
            self.layout.removeWidget(self.alarmDict[key])

        for key in self.alarmDict:
            if self.alarmDict[key].get_priority() == 'PRIORITY_HIGH':
                if self.layout.count() == 4:
                    self.extraAlarms.update_text(1 + len(self.alarmDict) - self.layout.count())
                    self.layout.addWidget(self.extraAlarms)
                    break
                self.layout.addWidget(self.alarmDict[key])


        if self.layout.count() < 5:
            for key in self.alarmDict:
                if self.layout.count() == 3:
                    self.extraAlarms.update_text(len(self.alarmDict) - self.layout.count())
                    self.layout.addWidget(self.extraAlarms)
                    break
                if self.alarmDict[key].get_priority() == 'PRIORITY_LOW':
                    self.layout.addWidget(self.alarmDict[key])



    # def resetTimer(self, alarmPayload):
    #     self.alarmDict[alarmPayload["alarm_code"]].timer.start()

    def location_on_window(self):
        """Position the popup as defined here"""
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        x = screen.width() - screen.width() / 2
        y = 0  # screen.height() - widget.height()
        self.move(x, y)
        return 0



class AlarmExtrasWidget(QtWidgets.QWidget):
    """Object containing information particular to one alarm.
    Created when alarm received from microcontroller, timeout after alarm signal stops.
    Is contained within alarmPopup"""
    def __init__(self, NativeUI, alarmCarrier, *args, **kwargs):
        super(AlarmExtrasWidget, self).__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        self.alarmCarrier = alarmCarrier # Needs to refer to its containing object

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setMargin(0)
        #self.alarmPayload = abstractAlarm.alarmPayload

        iconLabel = QtWidgets.QLabel()
        iconpath_check = os.path.join(
            self.NativeUI.iconpath, "exclamation-triangle-solid.png"
        )
        pixmap = QtGui.QPixmap(iconpath_check).scaledToHeight(40)
        iconLabel.setPixmap(pixmap)
        self.layout.addWidget(iconLabel)

        self.textLabel = QtWidgets.QLabel()
        self.textLabel.setText('1 More Alarms')
        self.textLabel.setFixedWidth(400)
        self.textLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.textLabel.setFont(NativeUI.text_font)
        #self.textLabel.setStyleSheet("font-size: " + NativeUI.text_size + ";")
        self.layout.addWidget(self.textLabel)

        self.setFixedHeight(40)
        self.setLayout(self.layout)
        self.setStyleSheet("background-color:red;")
            #self.priority = "PRIORITY_LOW"

    def update_text(self, num):
        self.textLabel.setText(str(num)+ ' More Alarms')
        #self.code =

        # self.timer = QtCore.QTimer()
        # self.timer.setInterval(500)  # just faster than 60Hz
        # self.timer.timeout.connect(self.checkAlarm)
        # self.timer.start()
        # self.installEventFilter(self)

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseButtonPress):
            self.NativeUI.leftBar.tab_page_buttons.button_alarms.click()
            self.NativeUI.alarms_view.alarmButton.click()
        return False

    def get_priority(self):
        return self.alarmPayload["alarm_type"]
