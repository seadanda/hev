#!/usr/bin/env python3

"""
page_buttons_widget.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "benjamin.mummery@stfc.ac.uk"
__status__ = "Prototype"

import os
from PySide2 import QtGui, QtWidgets
from PySide2.QtCore import QSize, Signal, Slot
import logging


class PageButtonsWidget(QtWidgets.QWidget):
    """
    Widget to contain the buttons that allow movement between pages. Buttons
    are oriented vertically.

    Button colors may be dictated by setting the colors dict, wherein
    foreground and background colors are provided in QColor types. If button
    colors are not set they default to red.
    """

    def __init__(self, NativeUI, *args, size: QSize = None, **kwargs):
        super().__init__(*args, **kwargs)

        self.NativeUI = NativeUI

        if size is not None:
            self.__button_size = size
        else:
            self.__button_size = QSize(100, 100)
        self.__iconsize = self.__button_size * 0.8

        layout = QtWidgets.QVBoxLayout()

        self.buttons = [
            PageButton(
                NativeUI,
                "",
                signal_value="main_page",
                icon=NativeUI.icons["button_main_page"],
            ),
            PageButton(
                "",
                signal_value="alarms_page",
                icon=NativeUI.icons["button_alarms_page"],
            ),
            PageButton(
                "", signal_value="modes_page", icon=NativeUI.icons["button_modes_page"]
            ),
            PageButton(
                "",
                signal_value="settings_page",
                icon=NativeUI.icons["button_settings_page"],
            ),
        ]

        for button in self.buttons:
            # set button appearance
            button.setStyleSheet(
                "QPushButton{"
                "    background-color:"
                + NativeUI.colors["background_enabled"].name()
                + ";"
                "    border-color: " + NativeUI.colors["page_background"].name() + ";"
                "    border:3px;"
                "}"
                "QPushButton:disabled{"
                "    background-color: "
                + NativeUI.colors["background_disabled"].name()
                + ";"
                "    border:none"
                "}"
            )
            button.setIconColor(NativeUI.colors["page_foreground"])
            button.setFixedSize(self.__button_size)
            button.setIconSize(self.__iconsize)

            layout.addWidget(button)

        self.setLayout(layout)

        # Connect the buttons so that pressing one enables all of the others
        for pressed_button in self.buttons:
            for unpressed_button in self.buttons:
                if pressed_button == unpressed_button:
                    continue
                pressed_button.pressed.connect(unpressed_button.enable)


class PageButton(QtWidgets.QPushButton):
    PageButtonPressed = Signal(str)

    def __init__(
        self, NativeUI, *args, signal_value: str = None, icon: str = None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.__signal_value = signal_value
        self.__icon_path = icon
        self.setIconColor("white")

        self.pressed.connect(self.on_press)

    def setIconColor(self, color):
        """
        Change the color of the icon to the specified color.
        """
        pixmap = QtGui.QPixmap(self.__icon_path)
        mask = pixmap.mask()  # mask from alpha
        pixmap.fill(color)  # fill with color
        pixmap.setMask(mask)  # reapply mask
        self.setIcon(QtGui.QIcon(pixmap))
        return 0

    @Slot()
    def enable(self):
        self.setEnabled(True)
        return 0

    def on_press(self):
        """
        When the button is pressed, disable it and emit the PageButtonPressed signal.
        """
        self.setEnabled(False)
        self.PageButtonPressed.emit(self.__signal_value)
        return 0
