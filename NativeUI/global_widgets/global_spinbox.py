from PySide2 import QtWidgets, QtGui, QtCore
from global_widgets.global_typeval_popup import TypeValuePopup


class signallingSpinBox(QtWidgets.QSpinBox):
    manualChanged = QtCore.Signal()

    def __init__(self, NativeUI):
        super().__init__()
        self.lineEdit().installEventFilter(self)

        self.popUp = TypeValuePopup(NativeUI)
        self.popUp.okButton.clicked.connect(self.okButtonPressed)
        self.popUp.cancelButton.clicked.connect(self.cancelButtonPressed)

    def okButtonPressed(self):
        val = float(self.popUp.lineEdit.text())
        self.setValue(val)
        self.popUp.close()
        self.manualChanged.emit()

    def cancelButtonPressed(self):
        self.popUp.lineEdit.setText(self.popUp.lineEdit.saveVal)
        self.popUp.close()

    def stepBy(self, step):
        value = self.value()
        super(signallingSpinBox, self).stepBy(step)
        if self.value() != value:
            self.manualChanged.emit()

    def eventFilter(self, source, event):
        if (
            source is self.lineEdit()
            and event.type() == QtCore.QEvent.MouseButtonDblClick
        ):
            self.popUp.lineEdit.setText(str(self.value()))
            self.popUp.show()
            return True
        return False


class simpleSpin(QtWidgets.QWidget):
    def __init__(self, NativeUI, infoArray, *args, **kwargs):
        super(simpleSpin, self).__init__(*args, **kwargs)
        print(infoArray)
        self.NativeUI = NativeUI

        self.cmd_type, self.cmd_code = '',''
        if len(infoArray) == 5:
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

        self.simpleSpin = signallingSpinBox(NativeUI)
        self.simpleSpin.setStyleSheet(
            """QSpinBox{ width:100px; font:16pt}
            QSpinBox[bgColour="0"]{background-color:white; }
            QSpinBox[bgColour="1"]{background-color:grey; }
                                        QSpinBox[textColour="0"]{color:black}
                                        QSpinBox[textColour="1"]{color:red}
                                        QSpinBox::up-button{width:20; border:solid white; color:black }
                                        QSpinBox::down-button{width:20; }
                                        """
        )
        self.simpleSpin.setProperty("textColour", "0")
        self.simpleSpin.setProperty("bgColour", "0")
        self.simpleSpin.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus
        )
        self.simpleSpin.setAlignment(QtCore.Qt.AlignCenter)
        if self.cmd_type == '':
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
        self.simpleSpin.manualChanged.connect(self.manualStep)
        # self.simpleSpin.valueChanged.connect(self.valChange)

    def manualStep(self):
        self.parent().liveUpdating = False
        self.manuallyUpdated = True
        self.simpleSpin.setProperty("textColour", "1")
        # self.expertButton.style().unpolish(self.expertButton)
        self.simpleSpin.style().polish(self.simpleSpin)

    def update_readback_value(self):
        newVal = self.NativeUI.readback[self.tag]
        self.simpleSpin.setValue(newVal)
        self.simpleSpin.setProperty("textColour", "0")
        self.simpleSpin.style().polish(self.simpleSpin)

    def update_targets_value(self):
        #print('new target')
        
        newVal = self.NativeUI.get_targets_db()
        #print(newVal)
        #self.simpleSpin.setValue(newVal)
        self.simpleSpin.setProperty("textColour", "0")
        self.simpleSpin.style().polish(self.simpleSpin)
