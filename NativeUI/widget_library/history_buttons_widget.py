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

from PySide2 import QtWidgets
from PySide2.QtCore import QSize, Signal, Slot


class HistoryButtonsWidget(QtWidgets.QWidget):
    """
    Widget to hold the HistoryButtons.
    """

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        button_size = 60
        self.__button_size = QSize(button_size, button_size)

        self.buttons = [
            HistoryButton("60s", signal_value=61),
            HistoryButton("30s", signal_value=31),
            HistoryButton("15s", signal_value=15),
            HistoryButton("5s", signal_value=5),
        ]

        # Button Appearance
        for button in self.buttons:
            button.setStyleSheet(
                "QPushButton{"
                "   background-color: "
                + NativeUI.colors["page_background"].name()
                + ";"
                "   border-color: " + NativeUI.colors["page_background"].name() + ";"
                "   color: " + NativeUI.colors["page_foreground"].name() + ";"
                "   font-size: " + NativeUI.text_size + ";"
                "}"
                "QPushButton:disabled{"
                "   background-color: "
                + NativeUI.colors["background_disabled"].name()
                + ";"
                "}"
            )
            button.setFixedSize(self.__button_size)

        # Button Layout
        grid = QtWidgets.QGridLayout()
        grid_columns = 2
        i_col = 0
        i_row = 0
        for widget in self.buttons:
            grid.addWidget(widget, i_row, i_col)
            i_col += 1
            if i_col == grid_columns:
                i_col = 0
                i_row += 1

        self.setLayout(grid)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # Connect the buttons so that pressing one enables all of the others
        for pressed_button in self.buttons:
            for unpressed_button in self.buttons:
                if pressed_button == unpressed_button:
                    continue
                pressed_button.pressed.connect(unpressed_button.enable)

        # self.resize(110, 110)

        self.buttons[0].on_press()


class HistoryButton(QtWidgets.QPushButton):
    """
    Identical to QPushButton but accepts an aditional optional argument signal_value
    that is emitted as part of the signal 'HistoryButtonPressed'. When pressed, all
    linked buttons as defined by the buttons list of the parent widget are enabled,
    while the pushed button is disabled.
    """

    HistoryButtonPressed = Signal(int)

    def __init__(self, *args, signal_value=None, **kwargs):
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
