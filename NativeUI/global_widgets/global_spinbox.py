from PySide2 import QtWidgets, QtGui, QtCore


class signallingSpinBox(QtWidgets.QSpinBox):
    stepChanged = QtCore.Signal()

    def stepBy(self, step):
        value = self.value()
        super(signallingSpinBox, self).stepBy(step)
        if self.value() != value:
            self.stepChanged.emit()


class simpleSpin(QtWidgets.QWidget):
    def __init__(self, infoArray, *args, **kwargs):
        super(simpleSpin, self).__init__(*args, **kwargs)

        self.label, self.units, self.tag = infoArray
        self.manuallyUpdated = False
        layout = QtWidgets.QHBoxLayout()

        textStyle = "color:white; font: 16pt"

        self.nameLabel = QtWidgets.QLabel(self.label)
        self.nameLabel.setStyleSheet(textStyle)
        self.nameLabel.setAlignment(QtCore.Qt.AlignRight)

        self.simpleSpin = signallingSpinBox()
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

        self.unitLabel = QtWidgets.QLabel(self.units)
        self.unitLabel.setStyleSheet(textStyle)
        self.unitLabel.setAlignment(QtCore.Qt.AlignLeft)

        widgets = [self.nameLabel, self.simpleSpin, self.unitLabel]
        for widget in widgets:
            layout.addWidget(widget)

        self.setLayout(layout)
        self.simpleSpin.stepChanged.connect(self.manualStep)
        # self.simpleSpin.valueChanged.connect(self.valChange)

    def manualStep(self):
        self.parent().liveUpdating = False
        self.manuallyUpdated = True
        self.simpleSpin.setProperty("textColour", "1")
        # self.expertButton.style().unpolish(self.expertButton)
        self.simpleSpin.style().polish(self.simpleSpin)

    def update_readback_value(self):
        newVal = (
            self.parent()
            .parent()
            .parent()
            .parent()
            .parent()
            .parent()
            .readback[self.tag]
        )
        self.simpleSpin.setValue(newVal)
        self.simpleSpin.setProperty("textColour", "0")
        self.simpleSpin.style().polish(self.simpleSpin)

    def update_targets_value(self):
        if (
            type(
                self.parent()
                .parent()
                .parent()
                .parent()
                .parent()
                .parent()
                .parent()
                .parent()
                .targets
            )
            == str
        ):
            return
        newVal = (
            self.parent().parent().parent().parent().parent().parent().targets[self.tag]
        )
        self.simpleSpin.setValue(newVal)
        self.simpleSpin.setProperty("textColour", "0")
        self.simpleSpin.style().polish(self.simpleSpin)
