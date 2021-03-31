from PySide2 import QtWidgets, QtGui, QtCore
from global_widgets.global_typeval_popup import TypeValuePopup


class SignallingLineEditWidget(QtWidgets.QLineEdit):
    manualChanged = QtCore.Signal()

    def __init__(self, NativeUI):
        super().__init__()
        self.installEventFilter(self)

        self.popUp = TypeValuePopup(NativeUI)
        self.popUp.lineEdit.setValidator(None)  # nsure it accepts text
        self.popUp.okButton.clicked.connect(self.okButtonPressed)
        self.popUp.cancelButton.clicked.connect(self.cancelButtonPressed)

    def okButtonPressed(self):
        val = self.popUp.lineEdit.text()
        self.setText(val)
        self.popUp.close()
        self.manualChanged.emit()

    def cancelButtonPressed(self):
        self.popUp.lineEdit.setText(self.popUp.lineEdit.saveVal)
        self.popUp.close()

    def eventFilter(self, source, event):
        if source is self and event.type() == QtCore.QEvent.MouseButtonDblClick:
            self.popUp.lineEdit.setText(str(self.text()))
            self.popUp.show()
            return True
        return False


class LabelledLineEditWidget(QtWidgets.QWidget):
    def __init__(self, NativeUI, infoArray, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # print(infoArray)
        self.NativeUI = NativeUI
        self.cmd_type, self.cmd_code = "", ""
        self.min, self.max, self.step = 0, 10000, 0.3
        self.decPlaces = 2
        if len(infoArray) == 9:
            self.label, self.units, self.tag, self.cmd_type, self.cmd_code, self.min, self.max, self.step, self.decPlaces = (
                infoArray
            )
        elif len(infoArray) == 5:
            self.label, self.units, self.tag, self.cmd_type, self.cmd_code = infoArray
        elif len(infoArray) == 3:
            self.label, self.units, self.tag = infoArray
        self.manuallyUpdated = False
        layout = QtWidgets.QHBoxLayout()
        widgetList = []
        textStyle = "color:white; font: 16pt"

        if self.label != "":
            self.nameLabel = QtWidgets.QLabel(self.label)
            self.nameLabel.setStyleSheet(textStyle)
            self.nameLabel.setAlignment(QtCore.Qt.AlignRight)
            widgetList.append(self.nameLabel)

        self.simpleSpin = SignallingLineEditWidget(NativeUI)
        self.simpleSpin.setText("")
        self.simpleSpin.setStyleSheet(
            """QDoubleSpinBox{ width:100px; font:16pt}
            QDoubleSpinBox[bgColour="0"]{background-color:white; }
            QDoubleSpinBox[bgColour="1"]{background-color:grey; }
                                        QDoubleSpinBox[textColour="0"]{color:black}
                                        QDoubleSpinBox[textColour="1"]{color:red}
                                        QDoubleSpinBox::up-button{width:20; border:solid white; color:black }
                                        QDoubleSpinBox::down-button{width:20; }
                                        """
        )
        self.simpleSpin.setProperty("textColour", "0")
        self.simpleSpin.setProperty("bgColour", "0")
        self.simpleSpin.setAlignment(QtCore.Qt.AlignCenter)
        if self.cmd_type == "":
            self.simpleSpin.setReadOnly(True)
            self.simpleSpin.setProperty("bgColour", "1")
        widgetList.append(self.simpleSpin)

        if self.units != "":
            self.unitLabel = QtWidgets.QLabel(self.units)
            self.unitLabel.setStyleSheet(textStyle)
            self.unitLabel.setAlignment(QtCore.Qt.AlignLeft)
            widgetList.append(self.unitLabel)

        for widget in widgetList:
            layout.addWidget(widget)

        self.setLayout(layout)

    def update_personal_value(self):
        newVal = self.NativeUI.get_db("personal")
        if newVal == {}:
            a = 1  # do nothing
        else:
            self.simpleSpin.setText(newVal[self.tag])
            self.simpleSpin.setProperty("textColour", "0")
            self.simpleSpin.style().polish(self.simpleSpin)
