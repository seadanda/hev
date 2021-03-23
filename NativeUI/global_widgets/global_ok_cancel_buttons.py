#!/usr/bin/env python3

"""
global_ok_cancel_buttons.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

from PySide2 import QtWidgets, QtGui, QtCore
import os


class okButton(
    QtWidgets.QPushButton
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        iconpath_check = os.path.join(NativeUI.iconpath, "check-solid.png")

        # set icon color
        pixmap = QtGui.QPixmap(iconpath_check)
        mask = pixmap.mask()
        pixmap.fill(NativeUI.colors["page_background"])
        pixmap.setMask(mask)
        self.setIcon(QtGui.QIcon(pixmap))

        self.setStyleSheet(
            "background-color: " + NativeUI.colors["page_foreground"].name() + ";"
            "color: " + NativeUI.colors["page_background"].name() + ";"
            "border-color: " + NativeUI.colors["page_foreground"].name() + ";"
            "font-size: " + NativeUI.text_size + ";"
            "border:none"
        )

        self.setFixedHeight(50)
        # self.setFixedSize(QtCore.QSize(150, 50))


class cancelButton(
    QtWidgets.QPushButton
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        iconpath_cross = os.path.join(NativeUI.iconpath, "times-solid.png")

        # set icon color
        pixmap = QtGui.QPixmap(iconpath_cross)
        mask = pixmap.mask()
        pixmap.fill(NativeUI.colors["page_background"])
        pixmap.setMask(mask)
        self.setIcon(QtGui.QIcon(pixmap))

        self.setStyleSheet(
            "background-color: " + NativeUI.colors["page_foreground"].name() + ";"
            "color: " + NativeUI.colors["page_background"].name() + ";"
            "border-color: " + NativeUI.colors["page_foreground"].name() + ";"
            "font-size: " + NativeUI.text_size + ";"
            "border-radius: 8px;"
            "border:none"
        )

        self.setFixedHeight(50)
        # self.setFixedSize(QtCore.QSize(150, 50))
