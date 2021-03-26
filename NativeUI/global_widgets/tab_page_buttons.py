#!/usr/bin/env python3

"""
tab_page_buttons.py
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
from PySide2.QtCore import QSize
import logging


class TabPageButtons(QtWidgets.QWidget):
    """
    Widget to contain the buttons that allow movement between pages. Buttons
    are oriented vertically.

    Button colors may be dictated by setting the colors dict, wherein
    foreground and background colors are provided in QColor types. If button
    colors are not set they default to red.

    TODO: move connections to NativeUI
    """

    def __init__(self, NativeUI, *args, size: QSize = None, **kwargs):
        super(TabPageButtons, self).__init__(*args, **kwargs)

        self.NativeUI = NativeUI

        if size is not None:
            self.__button_size = size
        else:
            self.__button_size = QSize(100, 100)
        self.__iconsize = self.__button_size * 0.8

        layout = QtWidgets.QVBoxLayout()

        self.button_mainview = QtWidgets.QPushButton("")
        self.button_alarms = QtWidgets.QPushButton("")
        self.button_fancon = QtWidgets.QPushButton("")
        self.button_settings = QtWidgets.QPushButton("")

        self.__buttons = [
            self.button_mainview,
            self.button_alarms,
            self.button_fancon,
            self.button_settings,
        ]
        self.__icons = [
            "user-md-solid",
            "exclamation-triangle-solid",
            "fan-solid",
            "sliders-h-solid",
        ]
        self.__icons = [ic + ".png" for ic in self.__icons]

        for button, icon in zip(self.__buttons, self.__icons):
            pixmap = QtGui.QPixmap(os.path.join(self.NativeUI.iconpath, icon))

            # set icon color
            mask = pixmap.mask()  # mask from alpha
            pixmap.fill(NativeUI.colors["page_foreground"])  # fill with color
            pixmap.setMask(mask)  # reapply mask

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
            button.setFixedSize(self.__button_size)

            button.setIcon(QtGui.QIcon(pixmap))
            button.setIconSize(self.__iconsize)
            layout.addWidget(button)

        self.setLayout(layout)

        self.button_mainview.pressed.connect(self.mainview_pressed)
        self.button_alarms.pressed.connect(self.alarms_pressed)
        self.button_fancon.pressed.connect(self.fancon_pressed)
        self.button_settings.pressed.connect(self.settings_pressed)

    def mainview_pressed(self):
        self.NativeUI.widgets.page_stack.setCurrentWidget(
            self.NativeUI.widgets.main_page
        )
        for button in self.__buttons:
            button.setEnabled(True)
        self.button_mainview.setEnabled(False)

    def settings_pressed(self):
        self.NativeUI.widgets.page_stack.setCurrentWidget(
            self.NativeUI.widgets.settings_page
        )
        for button in self.__buttons:
            button.setEnabled(True)
        self.button_settings.setEnabled(False)

    def alarms_pressed(self):
        self.NativeUI.widgets.page_stack.setCurrentWidget(
            self.NativeUI.widgets.alarms_page
        )
        for button in self.__buttons:
            button.setEnabled(True)
        self.button_alarms.setEnabled(False)

    def fancon_pressed(self):
        self.NativeUI.widgets.page_stack.setCurrentWidget(
            self.NativeUI.widgets.modes_page
        )
        for button in self.__buttons:
            button.setEnabled(True)
        self.button_fancon.setEnabled(False)
