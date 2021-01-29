from PySide2 import QtWidgets, QtGui, QtCore
import sys


def catch_exceptions(t, val, tb):
    # QtWidgets.QMessageBox.critical(None,
    #                                "An exception was raised",
    #                                "Exception type: {}".format(t))
    old_hook(t, val, tb)


old_hook = sys.excepthook
sys.excepthook = catch_exceptions


class alarmPopup(
    QtWidgets.QDialog
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, *args, **kwargs):
        super(alarmPopup, self).__init__(*args, **kwargs)

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(10)
        self.shadow.setYOffset(10)
        self.alarmDict = {}
        self.alarmDict["alarm_code"] = "stringy"
        self.alarmDict["alarm_type"] = "PRIORITY_HIGH"
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(0)
        # self.setStyleSheet('background-color:green; width:100px;')
        self.layout.setMargin(0)
        self.setLayout(self.layout)
        self.addAlarm(self.alarmDict)

        self.location_on_window()
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog
        )  # no window title

        self.timer = QtCore.QTimer()
        self.timer.setInterval(16)  # just faster than 60Hz
        self.timer.timeout.connect(
            self.updateAlarms
        )  # updates without checking if new data arrived?
        self.timer.start()
        self.existingAlarms = []

    def updateAlarms(self):
        newAlarm = self.parent().alarms
        if newAlarm == []:
            return
        if newAlarm["alarm_code"] in self.existingAlarms:
            a = 1  # do nothing
        else:
            self.addAlarm(newAlarm)
            self.existingAlarms.append(newAlarm["alarm_code"])
        self.show()

    def addAlarm(self, alarmPayload):
        alarmBox = QtWidgets.QWidget()
        alarmLayout = QtWidgets.QHBoxLayout()
        alarmLayout.setSpacing(0)

        alarmLayout.setMargin(0)
        iconLabel = QtWidgets.QLabel()
        iconLabel.setText("icon!")
        alarmLayout.addWidget(iconLabel)

        textLabel = QtWidgets.QLabel()
        textLabel.setText(alarmPayload["alarm_code"])

        textLabel.setFixedHeight(40)
        textLabel.setFixedWidth(150)
        textLabel.setAlignment(QtCore.Qt.AlignCenter)
        alarmLayout.addWidget(textLabel)

        alarmBox.setLayout(alarmLayout)
        if alarmPayload["alarm_type"] == "PRIORITY_HIGH":
            alarmBox.setStyleSheet("background-color:red;")
        elif alarmPayload["alarm_type"] == "PRIORITY_MEDIUM":
            alarmBox.setStyleSheet("background-color:orange;")

        self.layout.addWidget(alarmBox)

    def location_on_window(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = screen.width() - screen.width() / 2
        y = 0  # screen.height() - widget.height()
        self.move(x, y)
