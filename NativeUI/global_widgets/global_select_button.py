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
    """A button styled with two colour options, to use for tab selection"""

    def __init__(self, NativeUI, *args, **kwargs):
        super(selectorButton, self).__init__(*args, **kwargs)
        self.setFont(NativeUI.text_font)
        style = (
            "QPushButton[selected='0']{"
            "   color: " + NativeUI.colors["page_foreground"].name() + ";"
            "   background-color: "
            + NativeUI.colors["button_background_enabled"].name()
            + ";"
            "   border:none"
            "}"
            "QPushButton[selected='1']{"
            "   color: " + NativeUI.colors["page_background"].name() + ";"
            "   background-color:"
            + NativeUI.colors["button_foreground_disabled"].name()
            + ";"
            "   border:none"
            "}"
        )

        self.setStyleSheet(style)
        self.setProperty("selected", "0")
