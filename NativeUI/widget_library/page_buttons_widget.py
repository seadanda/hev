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

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.NativeUI = NativeUI

        layout = QtWidgets.QVBoxLayout()

        self.main_button = PageButton(
            NativeUI,
            "",
            signal_value="main_page",
            icon=NativeUI.icons["button_main_page"],
        )
        self.alarms_button = PageButton(
            "", signal_value="alarms_page", icon=NativeUI.icons["button_alarms_page"]
        )
        self.modes_button = PageButton(
            "", signal_value="modes_page", icon=NativeUI.icons["button_modes_page"]
        )
        self.settings_button = PageButton(
            "",
            signal_value="settings_page",
            icon=NativeUI.icons["button_settings_page"],
        )

        self.buttons = [
            self.main_button,
            self.alarms_button,
            self.modes_button,
            self.settings_button,
        ]

        stylesheet = (
            "QPushButton{"
            "    border:none"
            "}"
            "QPushButton:disabled{"
            "    background-color:"
            + NativeUI.colors["button_background_disabled"].name()
            + ";"
            "    border:none"
            "}"
            "QPushButton:enabled{"
            "    background-color:"
            + NativeUI.colors["button_background_enabled"].name()
            + ";"
            "    border:none"
            "}"
        )

        for button in self.buttons:
            # set button appearance
            button.setStyleSheet(stylesheet)
            button.setIconColor(NativeUI.colors["page_foreground"])

            layout.addWidget(button)

        self.setLayout(layout)

        # Connect the buttons so that pressing one enables all of the others
        for pressed_button in self.buttons:
            for unpressed_button in self.buttons:
                if pressed_button == unpressed_button:
                    continue
                pressed_button.pressed.connect(unpressed_button.enable)

    def set_pressed(self, pressed: str) -> int:
        """
        Set the specified buttons to enabled (unpressed) or disabled (pressed) states.
        By default, all buttons in self.buttons will be made enabled except those in the
        "pressed" list.

        pressed can be str or list of str.
        """
        if isinstance(pressed, str):
            pressed = [pressed]
        for button in self.buttons:
            button.setEnabled(True)
        for button_name in pressed:
            button = getattr(self, button_name)
            button.setEnabled(False)
        return 0

    def set_size(self, x: int, y: int, spacing: int = 10) -> int:
        """
        Set the size of the widget and its subwidgets.

        Spacing is computed on the assumption that the buttons should be square.

        If both x and y are set, buttons will be size (x - spacing) by MIN(x - spacing,
        y/n - spacing) where n is the number of buttons, and the PageButtonsWidget will
        have size x by y

        If x alone is set, buttons will be size (x-spacing) by (x-spacing), and the
        PageButtonsWidget will be size x by n*x where n is the number of buttons.

        If y alone is set, buttons will be size (y/n - spacing) by (y/n - spacing) where
        n is the number of buttons, and the PageButtonsWidget will have size y/n by y.


        """
        button_border = int(x / 3)
        n_buttons = len(self.buttons)

        x_set, y_set = False, False
        if x is not None:
            x_set = True
        if y is not None:
            y_set = True

        if x_set and y_set:
            self.setFixedSize(x, y)
            x_button = x - spacing
            y_button = min([x, int(y / n_buttons)]) - spacing
        elif x_set and not y_set:
            self.setFixedSize(x, n_buttons * x)
            x_button = x - spacing
            y_button = x - spacing
        elif y_set and not x_set:
            x_button = int(y / n_buttons)
            self.setFixedSize(x_button, y)
            y_button = x_button
        else:
            raise ValueError("set_size called with no size information")

        for button in self.buttons:
            button.setFixedSize(x_button, y_button)
            button.setIconSize(
                QSize(x_button - button_border, y_button - button_border)
            )

        return 0


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
