from PySide2 import QtWidgets, QtGui, QtCore

class alarmPopup(
    QtWidgets.QDialog
):
    def __init__(self, *args, **kwargs):
        super(alarmPopup, self).__init__(*args, **kwargs)

        self.alarmDict = {}

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


    def clearAlarms(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        self.adjustSize()
        self.setLayout(self.layout)

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
