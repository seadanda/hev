from PySide2 import QtWidgets, QtGui, QtCore
from main_widgets.customPopup import customPopup

# from customPopup2 import customPopup2
import sys


class customButton(QtWidgets.QFrame):
    def __init__(
        self,
    ):
        super().__init__()

        # self.setStyleSheet("background-color:blue;")
        self.currentVal = 0

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setMargin(0)
        self.label = QtWidgets.QLabel()
        self.label.setText("test label")
        labelTextColour = "rbg(60,58,60)"
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

        textColour = "blue"
        bgColour = "black"
        boxHeight, boxWidth = "100", "70"
        buttonHeight = "100"
        buttonWidth = "20"
        upImage = "buttonIcons/settings1.jpeg"  # if these are
        downImage = "buttonIcons/settings2.svg"
        textColour = "rbg(136,235,220)"
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
        # background-image: url('buttonIcons/settings1.jpeg');}"""
        # upButtonStyleString = ""
        upButtonPressedStyleString = (
            "QDoubleSpinBox::up-button:pressed{ border:orange;}"
        )
        downButtonStyleString = upButtonStyleString.replace(
            "up", "down"
        )  # "QDoubleSpinBox::down-button{image: url('" + downImage + "');}"
        downButtonPressedStyleString = ""  # "QDoubleSpinBox::down-button:pressed{background-color:white;image: url('" + upImage + "');}"
        self.doubleSpin.setStyleSheet(
            boxStyleString
            + upButtonStyleString
            + downButtonStyleString
            + upButtonPressedStyleString
            + downButtonPressedStyleString
        )
        self.doubleSpin.setProperty("colour", "1")
        self.doubleSpin.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus
        )
        # self.doubleSpin.setStyleSheet("QDoubleSpinBox::up-button{ height:30; width:100;")
        self.doubleSpin.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.doubleSpin)
        self.setLayout(self.layout)
        self.setStyleSheet("border:2px solid white; border-radius:4px; padding:0px; ")

        self.popUp = customPopup()
        self.popUp.okButton.clicked.connect(self.updateValue)
        self.popUp.cancelButton.clicked.connect(self.cancelUpdate)
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

    def updateValue(self):
        val = float(self.popUp.lineEdit.text())
        self.doubleSpin.setValue(val)
        self.popUp.close()

    def cancelUpdate(self):
        self.popUp.lineEdit.setText(self.popUp.lineEdit.saveVal)
        self.popUp.close()

    def setTextColour(self, option):
        # self.doubleSpin.setStyleSheet(self.boxStyleString + self.upArrowStyleString + self.downArrowStyleString + self.upArrowPressedStyleString + self.downArrowPressedStyleString)
        self.doubleSpin.style().unpolish(self.doubleSpin)
        self.doubleSpin.style().polish(self.doubleSpin)
        self.doubleSpin.setProperty("colour", option)

    def setTextWhite(self):
        # self.doubleSpin.setStyleSheet(boxStyleString + upArrowStyleString + downArrowStyleString + upArrowPressedStyleString + downArrowPressedStyleString)
        self.doubleSpin.style().unpolish(self.doubleSpin)
        self.doubleSpin.style().polish(self.doubleSpin)
        self.doubleSpin.setProperty("colour", "2")

    def valuechange(self):
        print("changed to " + str(self.value()))


class spinRow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(spinRow, self).__init__(*args, **kwargs)

        # self.setStyleSheet("background-color:blue;")

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setSpacing(5)

        self.spinInsp = customButton()
        self.spinRR = customButton()
        self.spinFIo2 = customButton()
        self.spinInhaleT = customButton()

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
        self.timer.setInterval(160)  # just faster than 60Hz
        self.timer.timeout.connect(
            self.updateTargets
        )  # updates without checking if new data arrived?
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
