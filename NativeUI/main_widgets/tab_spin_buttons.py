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
    """TO DO: Implement command sending"""
    def __init__(self, NativeUI, settings):
        super().__init__()

        self.liveUpdating = True
        # self.setStyleSheet("background-color:blue;")
        self.currentVal = 0
        self.cmd_type = settings[3]
        self.val_code = settings[2]
        self.NativeUI = NativeUI

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setMargin(0)

        # create and style label
        self.label = QtWidgets.QLabel()
        self.label.setText(settings[0])

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

        # upButtonPressedStyleString = (
        #    "QDoubleSpinBox::up-button:pressed{ border:orange;}"
        # )
        downButtonStyleString = upButtonStyleString.replace(
            "up", "down"
        )  # "QDoubleSpinBox::down-button{image: url('" + downImage + "');}"
        # downButtonPressedStyleString = ""  # "QDoubleSpinBox::down-button:pressed{background-color:white;image: url('" + upImage + "');}"
        self.simpleSpin.setStyleSheet(
            boxStyleString + upButtonStyleString + downButtonStyleString
        )
        #     + upButtonPressedStyleString
        #     + downButtonPressedStyleString
        # )
        self.simpleSpin.setProperty("colour", "1")
        self.simpleSpin.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus
        )
        # self.doubleSpin.setStyleSheet("QDoubleSpinBox::up-button{ height:30; width:100;")
        self.simpleSpin.setAlignment(QtCore.Qt.AlignCenter)
        self.simpleSpin.manualChanged.connect(self.manualChanged)
        self.layout.addWidget(self.simpleSpin)
        self.setLayout(self.layout)
        self.setStyleSheet("border:2px solid white; border-radius:4px; padding:0px; ")

    def update_targets_value(self):
        newVal = self.NativeUI.get_db("targets")
        if (newVal == {}) or (self.val_code == ""):
            a = 1  # do nothing
        else:
            if self.liveUpdating:
                self.simpleSpin.setValue(newVal[self.val_code])
                self.setTextColour(1)
            else:
                if self.simpleSpin.value() == newVal[self.val_code]:
                    self.liveUpdating = True
                    self.setTextColour(1)

    def manualChanged(self):
        """Called when user manually makes a change. Stops value from updating and changes colour"""
        self.liveUpdating = False
        self.setTextColour(2)
        return 0

    def setTextColour(self, option):
        """Set text colour and unpolish polish widget to show change"""
        self.simpleSpin.setProperty("colour", option)
        self.simpleSpin.style().unpolish(self.simpleSpin)
        self.simpleSpin.style().polish(self.simpleSpin)
        return 0


class TabSpinButtons(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(TabSpinButtons, self).__init__(*args, **kwargs)
        self.NativeUI = NativeUI
        # self.setStyleSheet("background-color:blue;")

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setSpacing(5)

        self.settingsList = [
            [
                "Inhale Pressure",
                "",
                "inspiratory_pressure",
                "SET_TARGET_CURRENT",
                "INSPIRATORY_PRESSURE",
            ],
            [
                "Respiratory Rate",
                "/min",
                "respiratory_rate",
                "SET_TARGET_CURRENT",
                "RESPIRATORY_RATE",
            ],
            ["Inhale Time", "s", "inhale_time", "SET_TARGET_CURRENT", "INHALE_TIME"],
            ["IE Ratio", "", "ie_ratio", "SET_TARGET_CURRENT", "IE_RATIO"],
            ["Percentage O2", "", "fiO2_percent", "SET_TARGET_CURRENT", "FIO2_PERCENT"],
        ]
        self.spinDict = {}
        for settings in self.settingsList:
            self.spinDict[settings[0]] = SpinButton(NativeUI, settings)
            self.layout.addWidget(self.spinDict[settings[0]])

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
        """Update values on all spinboxes"""
        for spin in self.spinDict:
            self.spinDict[spin].update_targets_value()
        return 0

    def ok_button_pressed(self):
        """Respond to ok button pressed by changing text colour and liveUpdating to True"""
        message, command = [], []
        for widget in self.spinDict:
            if not self.spinDict[widget].liveUpdating:
                setVal = self.spinDict[widget].simpleSpin.value()
                message.append("set" + widget + " to " + str(setVal))
                command.append(
                    [
                        self.spinDict[widget].cmd_type,
                        self.spinDict[widget].val_code,
                        setVal,
                    ]
                )
        self.popup = SetConfirmPopup(self, self.NativeUI, message, command)
        self.popup.okButton.pressed.connect(self.commandSent)
        self.popup.show()

        return 0

    def commandSent(self):
        for spin in self.spinDict:
            self.spinDict[spin].liveUpdating = True
            self.spinDict[spin].setTextColour("1")

    def cancel_button_pressed(self):
        """Respond to cancel button pressed by changing text colour and liveUpdating to True"""
        for spin in self.spinDict:
            self.spinDict[spin].liveUpdating = True
            self.spinDict[spin].setTextColour("1")

        # targets = self.NativeUI.get_targets_db()
        # if targets == {}:
        #     return
        # for spin, label in zip(self.__spins, self.__labels):
        #     if spin.doubleSpin.value() != float(targets[label]):
        #         spin.setTextColour("0")
        #     else:
        #         spin.setTextColour("2")
