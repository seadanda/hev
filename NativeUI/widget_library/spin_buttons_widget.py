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

# from global_widgets.global_send_popup import SetConfirmPopup


class SpinButton(QtWidgets.QFrame):
    """TO DO: Implement command sending"""

    def __init__(self, NativeUI, infoArray):
        super().__init__()

        self.manuallyUpdated = False
        # self.setStyleSheet("background-color:blue;")
        self.currentVal = 0
        if len(infoArray) == 10:
            self.label_text, self.units, self.tag, self.cmd_type, self.cmd_code, self.min, self.max, self.initVal, self.step, self.decPlaces = (
                infoArray
            )
        # self.cmd_type = settings[3]
        # self.cmd_code = settings[4]
        # self.tag = settings[2]
        self.NativeUI = NativeUI

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setMargin(0)

        # create and style label
        self.label = QtWidgets.QLabel()
        self.label.setText(self.label_text)

        labelBgColour = "rgb(60,58,60)"
        self.label.setStyleSheet(
            "color:white;"
            "background-color:" + labelBgColour + ";"
            ""  # border-radius:4px;"
            ""  # border: 2px solid white"
        )
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        #  self.label.setFixedHeight(45)
        #  self.label.setFont(NativeUI.text_font)
        self.layout.addWidget(self.label)
        # self.setFont(NativeUI.text_font)

        self.simpleSpin = signallingSpinBox(
            NativeUI,
            self.label_text,
            self.min,
            self.max,
            self.initVal,
            self.step,
            self.decPlaces,
        )
        self.simpleSpin.lineEdit().setStyleSheet("border:blue;")
        #  self.simpleSpin.setFixedHeight(100)
        #  self.simpleSpin.setFont(NativeUI.text_font)

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
        # self.setFont(NativeUI.text_font)
        upButtonStyleString = "QDoubleSpinBox::up-button{" "height:50;" "width:50;" "}"

        # upButtonPressedStyleString = (
        #    "QDoubleSpinBox::up-button:pressed{ border:orange;}"
        # )
        downButtonStyleString = upButtonStyleString.replace(
            "up", "down"
        )  # "QDoubleSpinBox::down-button{image: url('" + downImage + "');}"
        # downButtonPressedStyleString = ""  # "QDoubleSpinBox::down-button:pressed{background-color:white;image: url('" + upImage + "');}"
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
        self.simpleSpin.programmaticallyChanged.connect(self.manualChanged)
        self.simpleSpin.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed
        )
        self.layout.addWidget(self.simpleSpin)
        self.setLayout(self.layout)
        self.setFixedWidth(300)
        # self.setStyleSheet("border:2px solid white; border-radius:4px; padding:0px;")

    def update_value(self, db):
        newVal = db
        if (newVal == {}) or (self.cmd_code == ""):
            a = 1  # do nothing
        else:
            if not self.manuallyUpdated:
                self.simpleSpin.setValue(newVal[self.tag])
                self.setTextColour(1)
            else:
                if int(self.simpleSpin.value()) == int(newVal[self.tag]):
                    self.manuallyUpdated = False
                    self.setTextColour(1)

    def get_value(self):
        return self.simpleSpin.value()

    def set_value(self, value):
        self.simpleSpin.setValue(value)
        self.manuallyUpdated = True
        self.simpleSpin.programmaticallyChanged.emit()

    def manualChanged(self):
        print("manually changed" + self.label.text())
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

        # targets = self.NativeUI.get_targets_db()
        # if targets == {}:
        #     return
        # for spin, label in zip(self.__spins, self.__labels):
        #     if spin.doubleSpin.value() != float(targets[label]):
        #         spin.setTextColour("0")
        #     else:
        #         spin.setTextColour("2")

    @QtCore.Slot(dict)
    def localise_text(self, text: dict) -> int:
        self.spinDict["Inhale Pressure"].label.setText(
            text["spin_box_label_Inhale_Pressure"]
        )
        self.spinDict["Respiratory Rate"].label.setText(
            text["spin_box_label_Respiratory_Rate"]
        )
        self.spinDict["Inhale Time"].label.setText(text["spin_box_label_Inhale_Time"])
        self.spinDict["IE Ratio"].label.setText(text["spin_box_label_IE_Ratio"])
        self.spinDict["Percentage O2"].label.setText(
            text["spin_box_label_Percentage_O2"]
        )
        return 0
