#!/usr/bin/env python3

"""
chart_buttons_widget.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Benjamin Mummery"
__email__ = "benjamin.mummery@stfc.ac.uk"
__status__ = "Development"

from PySide2 import QtGui, QtWidgets
from PySide2.QtCore import QSize, Signal, Slot


class ChartButtonsWidget(QtWidgets.QWidget):
    def __init__(self, *args, colors: dict = {}, **kwargs):
        super().__init__(*args, **kwargs)
        self.pressureButton = ToggleButtonWidget("Pressure", signal_value="pressure")
        self.flow_button = ToggleButtonWidget("Flow", signal_value="flow")
        self.buttons = [
            self.pressureButton,
            self.flow_button,
        ]

        stylesheet = (
            "QPushButton{"
            "   background-color:" + colors["button_background_enabled"].name() + ";"
            "   color:" + colors["button_foreground_enabled"].name() + ";"
            "   border: none"
            "}"
            "QPushButton:checked{"
            "   background-color:" + colors["button_background_disabled"].name() + ";"
            "   color:" + colors["button_foreground_enabled"].name() + ";"
            "   border: none"
            "}"
        )
        for button in self.buttons:
            button.setStyleSheet(stylesheet)

        # Layout buttons block
        grid = QtWidgets.QGridLayout()
        i_row = 0
        i_col = 0
        for widget in self.buttons:
            grid.addWidget(widget, i_row, i_col)
            i_row += 1
        self.setLayout(grid)

    def set_size(self, x: int, y: int, spacing: int = 10) -> int:
        """
        Set the size of the widget and its subwidgets.
        """
        pass

    def setFont(self, font: QtGui.QFont) -> int:
        """
        Overrides the existing setFont method in order to propogate the change to
        subwidgets.
        """
        for button in self.buttons:
            button.setFont(font)
        return 0


class ToggleButtonWidget(QtWidgets.QPushButton):
    """
    Variant of the QPushButton that emits a signal containing a string (signal_value)
    """

    ToggleButtonPressed = Signal(str)
    ToggleButtonReleased = Signal(str)

    def __init__(self, *args, signal_value: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.__signal_value = signal_value
        self.setCheckable(True)
        self.pressed.connect(self.on_press)

    def on_press(self) -> int:
        """
        When the button is pressed, emit the either the ToggleButtonPressed or
        ToggleButtonReleased signal depending on whether the button was in the checked
        or unchacked state.
        """
        if self.isChecked():  # active -> inactive
            self.ToggleButtonReleased.emit(self.__signal_value)
        else:  # inactive -> active
            self.ToggleButtonPressed.emit(self.__signal_value)
        return 0
