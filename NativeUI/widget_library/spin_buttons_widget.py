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
            "color:white;"
            "background-color:" + labelBgColour + ";"
            "border-radius:4px;"
            "border: 2px solid white"
        )
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.label)
        self.setFont(NativeUI.text_font)

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
        self.setStyleSheet("border:2px solid white; border-radius:4px;")

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

    def set_label_font(self, font) -> int:
        """
        Set the font for the spinbox label.
        """
        self.label.setFont(font)
        return 0

    def set_value_font(self, font) -> int:
        """
        Set the font for the spinbox value display.
        """
        self.simpleSpin.setFont(font)
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
        self.okButton.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed
        )

        self.cancelButton = CancelButtonWidget(self.NativeUI)
        self.cancelButton.pressed.connect(self.cancel_button_pressed)
        self.cancelButton.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed
        )

        self.spinDict = {}
        self.spinStack = QtWidgets.QStackedWidget()
        stackedNames = ["Inhale Time", "IE Ratio"]
        for settings in self.settingsList:
            self.spinDict[settings[0]] = SpinButton(NativeUI, settings)
            self.spinDict[settings[0]].simpleSpin.manualChanged.connect(
                lambda: self.refresh_button_colour()
            )
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
            self.manuallyUpdated = (
                self.manuallyUpdated or self.spinDict[spin].manuallyUpdated
            )

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
        # self.colourButtons(0)

    def cancel_button_pressed(self):
        """Respond to cancel button pressed by changing text colour and liveUpdating to True"""
        for spin in self.spinDict:
            self.spinDict[spin].manuallyUpdated = False
            self.spinDict[spin].setTextColour("1")
        self.refresh_button_colour()

    def set_size(self, x: int, y: int, spacing: int = 10) -> int:
        """
        Set the size of the spinwidgets block and all widgets contained within.

        The SpinButtonsWidget is set to x by y pixels. Each spinbox within is set to
        x_spin by y pixels (minus spacing) where x_spin is the x value divided by 1 plus
        the number of shown spinboxes (at present this is one less than the total number
        of spinboxes since two of them are combined in a stack). The additional 1 is
        used to provide space for the ok and cancel buttons, which are set to x_spin by
        y_spin/2 pixels such that the two buttonstogether take up the space of a single
        spinbox.
        """
        self.setFixedSize(x, y)
        x_spin = int(x / len(self.spinDict)) - spacing
        y_spin = y - spacing

        for key in self.spinDict:
            self.spinDict[key].setFixedSize(x_spin, y_spin)
        self.spinStack.setFixedSize(x_spin, y_spin)
        self.cancelButton.setFixedSize(x_spin, int(y_spin / 2) - spacing)
        self.okButton.setFixedSize(x_spin, int(y_spin / 2) - spacing)
        return 0

    def set_label_font(self, font) -> int:
        """
        Set the font for all labels in spinboxes.
        """
        for key in self.spinDict:
            self.spinDict[key].set_label_font(font)
        return 0

    def set_value_font(self, font) -> int:
        """
        set the font for all value displays in spinboxes.
        """
        for key in self.spinDict:
            self.spinDict[key].set_value_font(font)
        return 0
