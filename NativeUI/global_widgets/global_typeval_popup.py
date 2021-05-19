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
os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

from widget_library.ok_cancel_buttons_widget import OkButtonWidget, CancelButtonWidget
from widget_library.numpad_widget import NumberpadWidget

class TypeValuePopup(QtWidgets.QDialog):
    """Popup takes user input to put in spin box. """
    okPressed = QtCore.Signal(str)
    cancelPressed = QtCore.Signal()

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #self.label_text = label_text
        #self.min, self.max, self.initVal, self.step, self.decPlaces = min, max, initVal, step, decPlaces
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(1)

        self.setStyleSheet("border-radius:4px; background-color:black")

        self.label = QtWidgets.QLabel()#self.label_text)
        self.label.setFont(NativeUI.text_font)
        self.label.setStyleSheet('color: ' + NativeUI.colors["page_foreground"].name())

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
        self.lineEdit.saveVal = ''#self.lineEdit.text()
        self.lineEdit.setValidator(
            QtGui.QDoubleValidator(0.0, 100.0, 5)
        )  # ensures only doubles can be typed, do
        # self.lineEdit.textEdited.connect(self.setTextColour(1))

        self.numberpad = NumberpadWidget(NativeUI)
        self.numberpad.numberPressed.connect(self.handle_numberpress)
        
        self.increaseButton = OkButtonWidget(NativeUI)
        self.increaseButton.clicked.connect(self.increase_button_clicked)
        self.increaseButton.setEnabled(True)
        
        self.decreaseButton = CancelButtonWidget(NativeUI)
        self.decreaseButton.clicked.connect(self.decrease_button_clicked)
        self.decreaseButton.setEnabled(True)

        #grid.addWidget(self.lineEdit, 0, 0, 1, 2)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.decreaseButton)
        hlayout.addWidget(self.lineEdit)
        hlayout.addWidget(self.increaseButton)

        hlayout2 = QtWidgets.QHBoxLayout()

        self.okButton = OkButtonWidget(NativeUI)
        self.okButton.setEnabled(True)
        self.okButton.pressed.connect(self.handle_ok_press)
        hlayout2.addWidget(self.okButton)
        #grid.addWidget(self.okButton, 1, 0)

        self.cancelButton = CancelButtonWidget(NativeUI)
        self.cancelButton.setEnabled(True)

        hlayout2.addWidget(self.cancelButton)
        #grid.addWidget(self.cancelButton, 1, 1)
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self.label)
        vlayout.addLayout(hlayout)
        vlayout.addWidget(self.numberpad)
        vlayout.addLayout((hlayout2))

        self.setLayout(vlayout)
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint
        )  # no window title

    def handle_ok_press(self):
        val = self.lineEdit.text()
        self.currentWidg.setValue(float(val))
        self.close()
        self.currentWidg.manualChanged.emit()

    def populatePopup(self, currentWidg):
        self.currentWidg = currentWidg
        self.label_text, self.min, self.max, self.initVal, self.step, self.decPlaces = currentWidg.label_text, currentWidg.min, currentWidg.max, currentWidg.initVal, currentWidg.step, currentWidg.decPlaces

        self.label.setText(self.label_text)

        self.lineEdit.setText(str(currentWidg.value()))

    def handle_numberpress(self, symbol):
        """Handle number pad button press. Put button value in line edit text, and handle inputs 
        outside accepted range or number of decimal places. Handle backspace"""

        oldText = self.lineEdit.text()
        if symbol.isnumeric() or (symbol == '.'):
            newText = oldText + symbol
            if float(newText) > self.max:
                newText = str(self.max)
            elif float(newText) < self.min:
                newText = str(self.min)
            elif '.' in newText:
                if len(newText.split('.')[1]) > self.decPlaces:
                    newText = oldText
            self.lineEdit.setText(newText)
        elif symbol == '<':
            self.lineEdit.setText(oldText[0:-1])

    def increase_button_clicked(self):
        """Handle increase step button click"""
        currentVal = self.get_value()
        newVal = round(float(currentVal) + self.step, self.decPlaces)
        if newVal >= self.max:
            newVal = self.max
        self.lineEdit.setText(str(newVal))
        return 0

    def decrease_button_clicked(self):
        """Handle decrease step button click"""
        currentVal = self.get_value()
        newVal = round(float(currentVal) - self.step, self.decPlaces)
        if newVal <= self.min:
            newVal = self.min
        self.lineEdit.setText(str(newVal))
        return 0

    def get_value(self):
        return self.lineEdit.text()
