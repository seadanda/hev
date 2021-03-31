#!/usr/bin/env python3

"""
ventialtor_start_stop_buttons_widget.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

import logging
from PySide2 import QtGui, QtWidgets
from PySide2.QtCore import QSize
from global_widgets.tab_hold_buttons import holdButton


class VentilatorStartStopButtonsWidget(QtWidgets.QWidget):
    """
    TODO
    """

    def __init__(self, NativeUI, *args, size: QSize = None, **kwargs):
        super().__init__(*args, **kwargs)

        self.NativeUI = NativeUI

        if size is not None:
            self.__button_size = size
        else:
            self.__button_size = QSize(100, 20)

        layout = QtWidgets.QVBoxLayout()

        self.button_start = holdButton(NativeUI)  # QtWidgets.QPushButton()
        self.button_stop = holdButton(NativeUI)  # QtWidgets.QPushButton()
        self.button_standby = holdButton(NativeUI)  # QtWidgets.QPushButton()

        self.__buttons = [self.button_start, self.button_stop, self.button_standby]
        self.__buttontext = ["START", "STOP", "STANDBY"]
        self.__buttoncommand = [""]

        for button, text in zip(self.__buttons, self.__buttontext):
            button.setText(text)
            button.popUp.completeLabel.setText("Ventilation " + text)
            layout.addWidget(button)
            button.setStyleSheet(
                "background-color:"
                + NativeUI.colors["button_background_enabled"].name()
                + ";"
                "color:" + NativeUI.colors["button_foreground_enabled"].name() + ";"
                "border:none"
            )

        self.setLayout(layout)

    def set_size(self, x: int, y: int, spacing: int = 10) -> int:
        """
        Set the size of the widget and its subwidgets.

        Sizing is computed on the assumption that the buttons should be as large as
        possible.

        If both x and y are set, VentilatorStartStopButtonsWidget will have size x by y,
        and buttons will be size (x - spacing) by MIN(x - spacing, y/n - spacing) where
        n is the number of buttons.

        If x alone is set, VentilatorStartStopButtonsWidget will have width x, and
        buttons will have width x-spacing. Both will expand to fill the available
        vertical space.

        If y alone is set, VentilatorStartStopButtonsWidget will have height y, and
        buttons will have height (y/n - spacing). Both will expand to fill the available
        horizontal space.
        """
        n_buttons = len(self.__buttons)

        x_set, y_set = False, False
        if x is not None:
            x_set = True
        if y is not None:
            y_set = True

        if x_set and y_set:
            self.setFixedSize(x, y)
            x_button = x - spacing
            y_button = min([x, int(y / n_buttons)]) - spacing
            for button in self.__buttons:
                button.setFixedSize(x_button, y_button)
                button.setSizePolicy(
                    QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
                )
        elif x_set and not y_set:
            self.setFixedWidth(x)
            for button in self.__buttons:
                button.setFixedWidth(x - spacing)
                button.setSizePolicy(
                    QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding
                )
        elif y_set and not x_set:
            self.setFixedHeight(y)
            y_button = int(y / n_buttons)
            for button in self.__buttons:
                button.setFixedHeight(y_button)
                button.setSizePolicy(
                    QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
                )
        else:
            raise ValueError("set_size called with no size information")

        return 0

    def setFont(self, font: QtGui.QFont) -> int:
        """
        Overrides the existing setFont method in order to propogate the change to
        subwidgets.
        """
        for button in self.__buttons:
            button.setFont(font)
        return 0
