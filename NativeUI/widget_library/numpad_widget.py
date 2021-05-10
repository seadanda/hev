#!/usr/bin/env python3

"""
numpad_wdget.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

from PySide2 import QtWidgets, QtGui, QtCore

class NumberpadButton(QtWidgets.QPushButton):
    """Individual numberpad buttons are styled here. Consider moving this to NumberpadWidget."""

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("background-color: " + NativeUI.colors["button_background_enabled"].name() + ";"
                           "color: " + NativeUI.colors["label_foreground"].name())
        self.setFont(NativeUI.text_font)


class NumberpadWidget(QtWidgets.QWidget):
    """A widget with digits 0-9, a decimal point '.', and a backspace '<'.
    Has one signal for any button pressed, the corresponding character is emitted with the signal.
    """
    numberPressed = QtCore.Signal(str)
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        symbol_list = ['0', '.', '<', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        button_dict = {}
        grid = QtWidgets.QGridLayout()
        ncolumns = 3
        i = 0
        for symbol in symbol_list:
            button_dict[symbol] = NumberpadButton(NativeUI, symbol)
            button_dict[symbol].pressed.connect(lambda j=symbol: self.buttonPressed(j))
            grid.addWidget(button_dict[symbol], int(i/ncolumns), i%ncolumns)
            i = i+1

        self.setLayout(grid)

    def buttonPressed(self,symbol: str):
        """Emit a signal with the button's character"""
        self.numberPressed.emit(symbol)