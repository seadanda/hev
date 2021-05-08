#!/usr/bin/env python3

"""
global_typeval_popup.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

from PySide2 import QtCore, QtGui, QtWidgets
import os

from widget_library.ok_cancel_buttons_widget import OkButtonWidget, CancelButtonWidget


class TypeValuePopup(QtWidgets.QDialog):
    """Popup takes user input to put in spin box. """

    def __init__(self, NativeUI):
        super().__init__()

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(1)

        self.setStyleSheet("border-radius:4px; background-color:black")

        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setText("4")
        self.lineEdit.setStyleSheet(
            "QLineEdit{"
            "   background-color: white;"
            "   border-radius: 4px;"
            "}"
            "QLineEdit[colour = '0']{"
            "   color: green;"
            "}"
            "QLineEdit[colour = '1']{"
            "   color: rgb(144, 231, 211);"
            "}"
            "QLineEdit[colour = '2']{"
            "   color: red;"
            "}"
        )
        self.lineEdit.setFont(NativeUI.text_font)
        self.lineEdit.setProperty("colour", "1")
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit.saveVal = self.lineEdit.text()
        self.lineEdit.setValidator(
            QtGui.QDoubleValidator(0.0, 100.0, 2)
        )  # ensures only doubles can be typed
        # self.lineEdit.textEdited.connect(self.setTextColour(1))
        grid.addWidget(self.lineEdit, 0, 0, 1, 2)

        self.okButton = OkButtonWidget(NativeUI)
        self.okButton.setEnabled(True)
        grid.addWidget(self.okButton, 1, 0)

        self.cancelButton = CancelButtonWidget(NativeUI)
        self.cancelButton.setEnabled(True)
        grid.addWidget(self.cancelButton, 1, 1)

        self.setLayout(grid)
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint
        )  # no window title

    def getValue(self):
        return self.lineEdit.text()
