#!/usr/bin/env python3

"""
spin_buttons_widget.py
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

# from global_widgets.global_ok_cancel_buttons import okButton, cancelButton
from widget_library.ok_cancel_buttons_widget import OkButtonWidget, CancelButtonWidget
from global_widgets.global_spinbox import signallingSpinBox
from global_widgets.global_send_popup import SetConfirmPopup


class SpinButton(QtWidgets.QFrame):
    """TO DO: Implement command sending"""

    def __init__(self, NativeUI, settings):
        super().__init__()

        self.manuallyUpdated = False
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
            if not self.manuallyUpdated:
                self.simpleSpin.setValue(newVal[self.val_code])
                self.setTextColour(1)
            else:

                if int(self.simpleSpin.value()) == int(newVal[self.val_code]):
                    self.manuallyUpdated = False
                    self.setTextColour(1)

    def manualChanged(self):
        """Called when user manually makes a change. Stops value from updating and changes colour"""
        self.manuallyUpdated = True
        self.setTextColour(2)
        return 0

    def setTextColour(self, option):
        """Set text colour and unpolish polish widget to show change"""
        self.simpleSpin.setProperty("colour", option)
        self.simpleSpin.style().unpolish(self.simpleSpin)
        self.simpleSpin.style().polish(self.simpleSpin)
        return 0


class SpinButtonsWidget(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

        self.okButton = OkButtonWidget(self.NativeUI)
        self.okButton.pressed.connect(self.ok_button_pressed)

        self.cancelButton = CancelButtonWidget(self.NativeUI)
        self.cancelButton.pressed.connect(self.cancel_button_pressed)

        self.spinDict = {}
        self.spinStack = QtWidgets.QStackedWidget()
        stackedNames = ["Inhale Time", "IE Ratio"]
        for settings in self.settingsList:
            self.spinDict[settings[0]] = SpinButton(NativeUI, settings)
            self.spinDict[settings[0]].simpleSpin.manualChanged.connect(lambda: self.refresh_button_colour())
            if settings[0] in stackedNames:
                self.spinStack.addWidget(self.spinDict[settings[0]])
            else:
                self.layout.addWidget(self.spinDict[settings[0]])
        self.layout.addWidget(self.spinStack)

        self.buttonLayout = QtWidgets.QVBoxLayout()
        self.buttonLayout.setSpacing(5)

        self.buttonLayout.addWidget(self.okButton)
        self.buttonLayout.addWidget(self.cancelButton)

        self.layout.addLayout(self.buttonLayout)

        self.setLayout(self.layout)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(160)
        self.timer.timeout.connect(self.update_targets)
        self.timer.start()

    def setStackWidget(self, label):
        self.spinStack.setCurrentWidget(self.spinDict[label])

    def colourButtons(self, option):
        self.okButton.setColour(str(option))
        self.cancelButton.setColour(str(option))

    def update_targets(self):
        for widget in self.spinDict:
            self.spinDict[widget].update_targets_value()  # pass database
        self.refresh_button_colour()

    def refresh_button_colour(self):
        self.manuallyUpdated = False
        for spin in self.spinDict:
            self.manuallyUpdated = self.manuallyUpdated or self.spinDict[spin].manuallyUpdated

        self.okButton.setColour(str(int(self.manuallyUpdated)))
        self.cancelButton.setColour((str(int(self.manuallyUpdated))))

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

    def ok_button_pressed(self):
        """Respond to ok button pressed by changing text colour and liveUpdating to True"""
        message, command = [], []
        for widget in self.spinDict:
            if self.spinDict[widget].manuallyUpdated:
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
            self.spinDict[spin].manuallyUpdated = False
            self.spinDict[spin].setTextColour("1")
        self.refresh_button_colour()
        #self.colourButtons(0)

    def cancel_button_pressed(self):
        """Respond to cancel button pressed by changing text colour and liveUpdating to True"""
        for spin in self.spinDict:
            self.spinDict[spin].manuallyUpdated = False
            self.spinDict[spin].setTextColour("1")
        self.refresh_button_colour()

        # targets = self.NativeUI.get_targets_db()
        # if targets == {}:
        #     return
        # for spin, label in zip(self.__spins, self.__labels):
        #     if spin.doubleSpin.value() != float(targets[label]):
        #         spin.setTextColour("0")
        #     else:
        #         spin.setTextColour("2")
