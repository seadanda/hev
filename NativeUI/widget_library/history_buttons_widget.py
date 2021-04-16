#!/usr/bin/env python3

"""
history_buttons_widget.py

Part of NativeUI. Defines the HistoryButton class to control the lookback time
of plots, and constructs the HistoryButtonsWidget to contain the requisite
historybuttons.
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


class HistoryButtonsWidget(QtWidgets.QWidget):
    """
    Widget to hold the HistoryButtons.
    """

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.NativeUI = NativeUI

        self.buttons = [
            HistoryButton("60s", signal_value=61),
            HistoryButton("30s", signal_value=31),
            HistoryButton("15s", signal_value=15),
            HistoryButton("5s", signal_value=5),
        ]
        self.__grid_columns = 2

        # Button Appearance
        stylesheet = (
            "QPushButton{"
            "   background-color:"
            + NativeUI.colors["button_background_enabled"].name()
            + ";"
            "   color: " + NativeUI.colors["button_foreground_enabled"].name() + ";"
            "   border: none;"
            "}"
            "QPushButton:disabled{"
            "   background-color:"
            + NativeUI.colors["button_background_disabled"].name()
            + ";"
            "   color: " + NativeUI.colors["button_foreground_enabled"].name() + ";"
            "   border: none;"
            "}"
        )
        for button in self.buttons:
            button.setStyleSheet(stylesheet)

        # Button Layout
        grid = QtWidgets.QGridLayout()
        i_col = 0
        self.__grid_rows = 0
        for widget in self.buttons:
            grid.addWidget(widget, self.__grid_rows, i_col)
            i_col += 1
            if i_col == self.__grid_columns:
                i_col = 0
                self.__grid_rows += 1

        self.setLayout(grid)

        # Connect the buttons so that pressing one enables all of the others
        for pressed_button in self.buttons:
            for unpressed_button in self.buttons:
                if pressed_button == unpressed_button:
                    continue
                pressed_button.pressed.connect(unpressed_button.enable)

        self.buttons[0].on_press()

    def set_size(self, x: int, y: int, spacing: int = 10) -> int:
        """
        Set the size of the widget and its subwidgets.

        Sizes are computed on the assumption that all buttons should be square.

        If both x and y are set, HistoryButtonsWidget will have size x by y, and buttons
        will be size MIN(x/n_cols, y/n_rows)-spacing where n_cols and n_rows are number
        of columns and rows in the button grid respectively.

        If x alone is set, the buttons will have size x/n_cols-spacing, and
        HistoryButtonsWidget will have size x by n_rows*(x/n_cols) (i.e. the height to
        fit all of the buttons).

        If y alone is set, the buttons will have size y/n_rows-spacing, and
        HistoryButtonsWidget will have size  n_cols*(y/n_rows) by y (i.e. the width
        expands to fit all of the buttons).
        """

        x_set, y_set = False, False
        if x is not None:
            x_set = True
        if y is not None:
            y_set = True

        if x_set and y_set:
            self.setFixedSize(x, y)
            button_size_temp_x = int(x / self.__grid_columns)
            button_size_temp_y = int(y / self.__grid_rows)
            button_size = int(min(x / self.__grid_columns, y / self.__grid_rows))
        elif x_set and not y_set:
            button_size = int(x / self.__grid_columns)
            self.setFixedSize(x, self.__grid_rows * button_size)
        elif y_set and not x_set:
            button_size = int(y / self.__grid_rows)
            self.setFixedSize(self.__grid_columns * button_size, y)
        else:
            raise ValueError("set_size called with no size information")

        for button in self.buttons:
            button.setFixedSize(button_size - spacing, button_size - spacing)

        return 0

    def setFont(self, font: QtGui.QFont) -> int:
        """
        Overrides the existing setFont method in order to propogate the change to
        subwidgets.
        """
        for button in self.buttons:
            button.setFont(font)
        return 0


class HistoryButton(QtWidgets.QPushButton):
    """
    Identical to QPushButton but accepts an aditional optional argument signal_value
    that is emitted as part of the signal 'HistoryButtonPressed'. When pressed, all
    linked buttons as defined by the buttons list of the parent widget are enabled,
    while the pushed button is disabled.
    """

    HistoryButtonPressed = Signal(int)

    def __init__(self, *args, signal_value: int = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.__signal_value = signal_value
        self.pressed.connect(self.on_press)

    @Slot()
    def enable(self):
        self.setEnabled(True)
        return 0

    def on_press(self):
        """
        When the button is pressed, disable it and emit the HistoryButtonPressed signal.
        """

        self.setEnabled(False)
        self.HistoryButtonPressed.emit(self.__signal_value)
        return 0
