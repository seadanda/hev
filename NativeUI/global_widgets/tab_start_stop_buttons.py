#!/usr/bin/env python3

"""
tab_start_stop_buttons.py
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


class TabStartStopStandbyButtons(QtWidgets.QWidget):
    """
    Combine holdButtons into Start, Stop, and Standby buttons in the left bar.
    """

    def __init__(self, NativeUI, *args, size: QSize = None, **kwargs):
        super(TabStartStopStandbyButtons, self).__init__(*args, **kwargs)

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
                "background-color: "
                + NativeUI.colors["background-enabled"].name()
                + ";"
                "border-color: " + NativeUI.colors["foreground"].name() + ";"
                "font-size: " + NativeUI.text_size + ";"
                "color: " + NativeUI.colors["foreground"].name() + ";"
                "border:none"
            )
            button.setFixedSize(self.__button_size)

        self.setLayout(layout)

