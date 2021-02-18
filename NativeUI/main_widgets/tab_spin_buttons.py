# from customPopup2 import customPopup2
import sys

from PySide2 import QtCore, QtGui, QtWidgets
from global_widgets.global_typeval_popup import TypeValuePopup


class SpinButton(QtWidgets.QFrame):
    def __init__(self, NativeUI):
        super().__init__()

        # self.setStyleSheet("background-color:blue;")
        self.currentVal = 0

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setMargin(0)

        # create and style label
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

        self.popUp = TypeValuePopup(NativeUI)
        self.popUp.okButton.clicked.connect(self.okButtonPressed)
        self.popUp.cancelButton.clicked.connect(self.cancelButtonPressed)

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


class TabSpinButtons(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(TabSpinButtons, self).__init__(*args, **kwargs)
        self.NativeUI = NativeUI
        # self.setStyleSheet("background-color:blue;")

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setSpacing(5)

        self.spinInsp = SpinButton(NativeUI)
        self.spinRR = SpinButton(NativeUI)
        self.spinFIo2 = SpinButton(NativeUI)
        self.spinInhaleT = SpinButton(NativeUI)

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

    def updateTargets(self):
        targets = self.NativeUI.get_targets_db()
        if targets == "empty":
            return
        for spin, label in zip(self.__spins, self.__labels):
            if spin.doubleSpin.value() != float(targets[label]):
                spin.setTextColour("0")
            else:
                spin.setTextColour("2")
