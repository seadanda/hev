#!/usr/bin/env python3

"""
tab_spin_buttons.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Development"

# from customPopup2 import customPopup2
import sys

from PySide2 import QtCore, QtGui, QtWidgets
from global_widgets.global_typeval_popup import TypeValuePopup
from global_widgets.global_ok_cancel_buttons import okButton, cancelButton
from global_widgets.global_spinbox import signallingSpinBox
from global_widgets.global_send_popup import SetConfirmPopup


class SpinButton(QtWidgets.QFrame):
    def __init__(self, NativeUI, label, code):
        super().__init__()
        self.NativeUI = NativeUI
        self.manuallyUpdated = False
        # self.setStyleSheet("background-color:blue;")
        self.code = code
        self.currentVal = 0

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setMargin(0)

        # create and style label
        self.label = QtWidgets.QLabel(label)
        # self.label.setText("test label")

        labelBgColour = "rgb(60,58,60)"
        self.label.setStyleSheet(
            "font-size: " + NativeUI.text_size + ";"
            "color:white;"
            "background-color:" + labelBgColour + ";"
            "border-radius:4px;"
            "border: 2px solid white"
        )
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.simpleSpin = signallingSpinBox(NativeUI)
        # self.doubleSpin = QtWidgets.QDoubleSpinBox()
        # self.doubleSpin.lineEdit().installEventFilter(
        #     self
        # )  # override is defined in 'eventFilter'. ensures lineEdit responds to double mouse click
        self.simpleSpin.lineEdit().setStyleSheet("border:blue;")

        boxStyleString = (
            "QDoubleSpinBox{"
            "   border:none;"
            "   background-color: black;"
            "   font: " + NativeUI.text_size + " large 'Times New Roman';"
            "   height: 60px;"
            "}"
            "QDoubleSpinBox[colour='0'] {"
            "   color:green;"
            "}"
            "QDoubleSpinBox[colour='1'] {"
            "   color:rgb(144,231,211);"
            "}"
            "QDoubleSpinBox[colour='2'] {"
            "    color:red;"
            "}"
        )

        upButtonStyleString = "QDoubleSpinBox::up-button{" "height:30;" "width:40;" "}"

        downButtonStyleString = upButtonStyleString.replace("up", "down")
        self.simpleSpin.setStyleSheet(
            boxStyleString + upButtonStyleString + downButtonStyleString
        )
        self.simpleSpin.setProperty("colour", "1")
        self.simpleSpin.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus
        )
        self.simpleSpin.setAlignment(QtCore.Qt.AlignCenter)
        self.simpleSpin.manualChanged.connect(self.manualChanged)
        self.layout.addWidget(self.simpleSpin)
        self.setLayout(self.layout)
        self.setStyleSheet("border:2px solid white; border-radius:4px; padding:0px; ")

    def manualChanged(self):
        self.manuallyUpdated = True
        self.setTextColour("2")

    def setTextColour(self, option):
        self.simpleSpin.setProperty("colour", option)
        self.simpleSpin.style().unpolish(self.simpleSpin)
        self.simpleSpin.style().polish(self.simpleSpin)

    def update_targets_value(self):
        newVal = self.NativeUI.get_db("targets")
        if (newVal == {}) or (self.code == ""):
            a = 1  # do nothing
        else:
            if not self.manuallyUpdated:
                self.simpleSpin.setValue(newVal[self.code])
                self.simpleSpin.setProperty("textColour", "0")
                self.simpleSpin.style().polish(self.simpleSpin)


class TabSpinButtons(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(TabSpinButtons, self).__init__(*args, **kwargs)
        self.NativeUI = NativeUI
        # self.setStyleSheet("background-color:blue;")
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setSpacing(5)

<<<<<<< HEAD
=======
        #        self.spinInsp = SpinButton(NativeUI)
        #       self.spinRR = SpinButton(NativeUI)
        #      self.spinFIo2 = SpinButton(NativeUI)
        #     self.spinInhaleT = SpinButton(NativeUI)

        # self.__spins = [self.spinInsp, self.spinRR, self.spinFIo2, self.spinInhaleT]
>>>>>>> 0c27f0b0cc2468eee3298a8eb46342b7f507a4c4
        self.__labels = ["P_insp [cm H2O]", "RR", "FIO2 [%]", "Inhale Time [s]"]
        self.__codes = [
            "inspiratory_pressure",
            "respiratory_rate",
            "fiO2_percent",
            "inhale_time",
        ]
<<<<<<< HEAD

=======
        # self.cmd_code = [code.upper() for code in self.__codes]
>>>>>>> 0c27f0b0cc2468eee3298a8eb46342b7f507a4c4
        self.spinDict = {}
        for label, code in zip(self.__labels, self.__codes):
            self.spinDict[code] = SpinButton(NativeUI, label, code)
            self.spinDict[code].simpleSpin.manualChanged.connect(self.colourButtons)
            self.layout.addWidget(self.spinDict[code])

        self.buttonLayout = QtWidgets.QVBoxLayout()
        self.buttonLayout.setSpacing(5)

        self.okButton = okButton(self.NativeUI)
        self.okButton.pressed.connect(self.ok_button_pressed)
        self.buttonLayout.addWidget(self.okButton)

        self.cancelButton = cancelButton(self.NativeUI)
        self.cancelButton.pressed.connect(self.cancel_button_pressed)
        self.buttonLayout.addWidget(self.cancelButton)

        self.layout.addLayout(self.buttonLayout)

        self.setLayout(self.layout)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(160)
        self.timer.timeout.connect(self.update_targets)
        self.timer.start()

    def colourButtons(self):
        self.okButton.setColour(1)
        self.cancelButton.setColour(1)

    def update_targets(self):
        for widget in self.spinDict:
            self.spinDict[widget].update_targets_value()  # pass database
<<<<<<< HEAD
=======
        # targets = self.NativeUI.get_db("targets")
        # if targets == {}:
        #     return
        # if targets["mode"] == "CURRENT":
        #     for spin, code in zip(self.__spins, self.__codes):
        #         if spin.simpleSpin.value() != float(targets[code]):
        #             if spin.liveUpdating:
        #                 spin.simpleSpin.setValue(float(targets[code]))
        #                 spin.setTextColour("2")
        #             else:
        #                 spin.setTextColour("0")
        #         else:
        #             spin.setTextColour("2")
>>>>>>> 0c27f0b0cc2468eee3298a8eb46342b7f507a4c4

    def ok_button_pressed(self):
        message, command = [], []
        for widget in self.spinDict:
            if self.spinDict[widget].manuallyUpdated:
                setVal = self.spinDict[widget].simpleSpin.value()
                message.append(
                    "set" + self.spinDict[widget].label.text() + " to " + str(setVal)
                )
                command.append(
                    ["SET_TARGET_PC_AC", self.spinDict[widget].code.upper(), setVal]
                )
        self.popup = SetConfirmPopup(self, self.NativeUI, message, command)
        self.popup.okButton.pressed.connect(self.commandSent)
        self.popup.show()

    def commandSent(self):
        self.okButton.setColour(0)
        self.cancelButton.setColour(0)
        for widget in self.spinDict:
            if self.spinDict[widget].manuallyUpdated:
                self.spinDict[widget].manuallyUpdated = False
            self.spinDict[widget].setTextColour("1")

    def cancel_button_pressed(self):
        self.okButton.setColour(0)
        self.cancelButton.setColour(0)
        for spin in self.spinDict:
            self.spinDict[spin].manuallyUpdated = False
            self.spinDict[spin].setTextColour("1")
