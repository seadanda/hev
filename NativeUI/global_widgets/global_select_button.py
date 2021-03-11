#!/usr/bin/env python3

"""
global_select_button.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

from PySide2 import QtWidgets, QtGui, QtCore


class selectorButton(QtWidgets.QPushButton):
    def __init__(self, NativeUI, *args, **kwargs):
        super(selectorButton, self).__init__(*args, **kwargs)
        fontsize = 20

        style = (
            "QPushButton{"
            "font: " + str(fontsize) + "pt;"
            "}"
            "QPushButton[selected='0']{"
            "font: " + str(fontsize) + "pt;"
            "color: " + NativeUI.colors["foreground"].name() + ";"
            "background-color: " + NativeUI.colors["background-enabled"].name() + ";"
            "border:none"
            "}"
            "QPushButton[selected='1']{"
            "font: " + str(fontsize) + "pt;"
            "color: " + NativeUI.colors["background"].name() + ";"
            "background-color: " + NativeUI.colors["foreground-disabled"].name() + ";"
            "border:none"
            "}"
        )

        self.setStyleSheet(style)
        self.setProperty("selected", "0")
