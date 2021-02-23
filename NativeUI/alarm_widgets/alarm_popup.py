import os
from PySide2 import QtCore, QtGui, QtWidgets


class alarmWidget(QtWidgets.QWidget):
    def __init__(self, NativeUI, alarmPayload, *args, **kwargs):
        super(alarmWidget, self).__init__(*args, **kwargs)

        self.NativeUI = NativeUI

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setMargin(0)
        self.alarmPayload = alarmPayload

        iconLabel = QtWidgets.QLabel()
        iconpath_check = os.path.join(self.NativeUI.iconpath, "exclamation-triangle-solid.png") 
        pixmap = QtGui.QPixmap(iconpath_check)
        iconLabel.setPixmap(pixmap)
        self.layout.addWidget(iconLabel)

        textLabel = QtWidgets.QLabel()
        textLabel.setText(self.alarmPayload["alarm_code"])
        textLabel.setFixedWidth(150)
        textLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(textLabel)

        self.setFixedHeight(40)
        self.setLayout(self.layout)
        if alarmPayload["alarm_type"] == "PRIORITY_HIGH":
            self.setStyleSheet("background-color:red;")
        elif alarmPayload["alarm_type"] == "PRIORITY_MEDIUM":
            self.setStyleSheet("background-color:orange;")

        self.timer = QtCore.QTimer()
        self.timer.setInterval(20000)  # just faster than 60Hz
        self.timer.timeout.connect(self.checkAlarm)
        self.timer.start()

    def checkAlarm(self):
        self.parent().alarmDict.pop(self.alarmPayload["alarm_code"])
        self.setParent(None)


class alarmPopup(QtWidgets.QDialog):
    def __init__(self, NativeUI, *args, **kwargs):
        super(alarmPopup, self).__init__(*args, **kwargs)

        self.alarmDict = {}
        self.NativeUI = NativeUI

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(0)
        # self.setStyleSheet('background-color:green; width:100px;')
        self.layout.setMargin(0)
        self.setLayout(self.layout)

        self.location_on_window()
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog
        )  # no window title

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(10)
        self.shadow.setYOffset(10)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)  # just faster than 60Hz
        self.timer.timeout.connect(self.adjustSize)
        self.timer.start()

    def clearAlarms(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        self.adjustSize()
        self.setLayout(self.layout)
        self.alarmDict = {}

    def addAlarm(self, alarmPayload):
        self.alarmDict[alarmPayload["alarm_code"]] = alarmWidget(self.NativeUI, alarmPayload)
        self.layout.addWidget(self.alarmDict[alarmPayload["alarm_code"]])

    def resetTimer(self, alarmPayload):
        self.alarmDict[alarmPayload["alarm_code"]].timer.start()

    def location_on_window(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry()

        x = screen.width() - screen.width() / 2
        y = 0  # screen.height() - widget.height()
        self.move(x, y)
