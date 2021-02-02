# from customPopup2 import customPopup2
import sys

from PySide2 import QtCore, QtGui, QtWidgets

# from main_widgets.customPopup import customPopup


class SpinPopup(
    QtWidgets.QDialog
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self):
        super().__init__()

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(1)

        self.setStyleSheet("border-radius:4px; background-color:black")

        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setText("4")
        self.lineEdit.setStyleSheet(
            """QLineEdit{font: 16pt;
                                            background-color:white;
                                            border-radius:4px }
                                        QLineEdit[colour = "0"]{
                                            color:green
                                        }
                                        QLineEdit[colour = "1"]{
                                            color:rgb(144,231,211);
                                        }
                                        QLineEdit[colour = "2"]{
                                            color:red
                                        }"""
        )
        self.lineEdit.setProperty("colour", "1")
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit.saveVal = self.lineEdit.text()
        self.lineEdit.setValidator(
            QtGui.QDoubleValidator(0.0, 100.0, 2)
        )  # ensures only doubles can be typed
        # self.lineEdit.installEventFilter(
        #    self
        # )  # override to respond to key press(enter and esc) defined in eventFilter
        grid.addWidget(self.lineEdit, 0, 0, 1, 2)

        self.okButton = QtWidgets.QPushButton()
        self.okButton.setIcon(QtGui.QIcon("hev-display/svg/check-solid.svg"))
        self.okButton.setStyleSheet("background-color:white; border-radius:4px ")
        grid.addWidget(self.okButton, 1, 0)

        self.cancelButton = QtWidgets.QPushButton()
        self.cancelButton.setIcon(QtGui.QIcon("figures/pic2.jpg"))
        self.cancelButton.setStyleSheet("background-color:white; border-radius:4px ")
        grid.addWidget(self.cancelButton, 1, 1)

        self.setLayout(grid)
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint
        )  # no window title

    def getValue(self):
        return self.lineEdit.text()

    def setTextColour(self, option):
        self.lineEdit.style().unpolish(self.lineEdit)
        self.lineEdit.style().polish(self.lineEdit)
        self.lineEdit.setProperty("colour", option)

    def setTextWhite(self):
        self.lineEdit.style().unpolish(self.lineEdit)
        self.lineEdit.style().polish(self.lineEdit)
        self.lineEdit.setProperty("colour", "2")

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.KeyPress and source is self.lineEdit:
            if event.text() == "\r":  # enter
                self.okButton.click()
                return True
            elif event.text() == "\x1b":  # Escape button
                self.cancelButton.click()
                return True
            else:
                return False  # think False means process normally


class SpinButton(QtWidgets.QFrame):
    def __init__(self,):
        super().__init__()

        # self.setStyleSheet("background-color:blue;")
        self.currentVal = 0

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setMargin(0)
        self.label = QtWidgets.QLabel()
        self.label.setText("test label")

        labelBgColour = "rgb(60,58,60)"
        self.label.setStyleSheet(
            "font: 16pt; color:white; background-color:"
            + labelBgColour
            + "; border-radius:4px; border: 2px solid white "
        )
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.doubleSpin = QtWidgets.QDoubleSpinBox()
        self.doubleSpin.lineEdit().installEventFilter(
            self
        )  # override is defined in 'eventFilter'. ensures lineEdit responds to double mouse click
        self.doubleSpin.lineEdit().setStyleSheet("border:blue;")

        boxStyleString = """QDoubleSpinBox{
                        border:none;
                        background-color: black;
                        font: 16pt large 'Times New Roman';
                        height:60px;
                        }
                        QDoubleSpinBox[colour="0"] {
                            color:green;
                        }
                        QDoubleSpinBox[colour="1"] {
                            color:rgb(144,231,211);
                        }
                        QDoubleSpinBox[colour="2"] {
                            color:red;
                        }
                        """

        upButtonStyleString = """QDoubleSpinBox::up-button{
             height:30;
             width:40;
             }    """

        # upButtonPressedStyleString = (
        #    "QDoubleSpinBox::up-button:pressed{ border:orange;}"
        # )
        downButtonStyleString = upButtonStyleString.replace(
            "up", "down"
        )  # "QDoubleSpinBox::down-button{image: url('" + downImage + "');}"
        # downButtonPressedStyleString = ""  # "QDoubleSpinBox::down-button:pressed{background-color:white;image: url('" + upImage + "');}"
        self.doubleSpin.setStyleSheet(
            boxStyleString + upButtonStyleString + downButtonStyleString
        )
        #     + upButtonPressedStyleString
        #     + downButtonPressedStyleString
        # )
        self.doubleSpin.setProperty("colour", "1")
        self.doubleSpin.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus
        )
        # self.doubleSpin.setStyleSheet("QDoubleSpinBox::up-button{ height:30; width:100;")
        self.doubleSpin.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.doubleSpin)
        self.setLayout(self.layout)
        self.setStyleSheet("border:2px solid white; border-radius:4px; padding:0px; ")

        self.popUp = SpinPopup()
        self.popUp.okButton.clicked.connect(self.okButtonPressed)
        self.popUp.cancelButton.clicked.connect(self.cancelButtonPressed)
        # self.lineEdit.installEventFilter(self)

        # self.test()

    def eventFilter(self, source, event):
        if (
            source is self.doubleSpin.lineEdit()
            and event.type() == QtCore.QEvent.MouseButtonDblClick
        ):
            self.popUp.lineEdit.setText(str(self.doubleSpin.value()))
            self.popUp.show()
            return True
        return False

    def okButtonPressed(self):
        val = float(self.popUp.lineEdit.text())
        self.doubleSpin.setValue(val)
        self.popUp.close()

    def cancelButtonPressed(self):
        self.popUp.lineEdit.setText(self.popUp.lineEdit.saveVal)
        self.popUp.close()

    def setTextColour(self, option):
        self.doubleSpin.style().unpolish(self.doubleSpin)
        self.doubleSpin.style().polish(self.doubleSpin)
        self.doubleSpin.setProperty("colour", option)


#    def valuechange(self):
#        print("changed to " + str(self.value()))


class TabSpinButtons(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(TabSpinButtons, self).__init__(*args, **kwargs)

        # self.setStyleSheet("background-color:blue;")

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setSpacing(5)

        self.spinInsp = SpinButton()
        self.spinRR = SpinButton()
        self.spinFIo2 = SpinButton()
        self.spinInhaleT = SpinButton()

        self.__spins = [self.spinInsp, self.spinRR, self.spinFIo2, self.spinInhaleT]
        self.__labels = [
            "inspiratory_pressure",
            "respiratory_rate",
            "fiO2_percent",
            "inhale_time",
        ]
        for spin in self.__spins:
            self.layout.addWidget(spin)

        self.buttonLayout = QtWidgets.QVBoxLayout()
        self.buttonLayout.setSpacing(5)
        self.okButton = QtWidgets.QPushButton()
        self.okButton.setStyleSheet(
            "height:50; width:40;background-image:url('buttonIcons/settings1.jpeg')"
        )
        self.buttonLayout.addWidget(self.okButton)

        self.cancelButton = QtWidgets.QPushButton()
        self.cancelButton.setStyleSheet(
            "height:50; width:40;background-image:url('buttonIcons/settings1.jpeg')"
        )
        self.buttonLayout.addWidget(self.cancelButton)

        self.layout.addLayout(self.buttonLayout)

        self.setLayout(self.layout)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(160)
        self.timer.timeout.connect(self.updateTargets)
        self.timer.start()
        self.existingAlarms = []

    def updateTargets(self):
        targets = self.parent().parent().parent().parent().targets
        if targets == "empty":
            return
        for spin, label in zip(self.__spins, self.__labels):
            if spin.doubleSpin.value() != float(targets[label]):
                spin.setTextColour("0")
            else:
                spin.setTextColour("2")
