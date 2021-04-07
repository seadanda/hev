#!/usr/bin/env python3

"""
ok_cancel_buttons_widget.py
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


class OkButtonWidget(
    QtWidgets.QPushButton
):
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
            "QPushButton[bgColour='0']{background-color: "
            + NativeUI.colors["page_foreground"].name()
            + ";}"
            "QPushButton[bgColour='1']{background-color: "
            + NativeUI.colors["green"].name()
            + ";}"
            "QPushButton{color: " + NativeUI.colors["page_background"].name() + ";"
            "border-color: " + NativeUI.colors["page_foreground"].name() + ";"
            "font-size: " + NativeUI.text_size + ";"
            "border-radius: 8px;"
            "border:none}"
        )
        self.setProperty("bgColour", "0")
        self.setEnabled(False)

        self.setFixedHeight(50)
        # self.setFixedSize(QtCore.QSize(150, 50))

    def setColour(self, option):
        self.setEnabled(bool(float(option)))
        self.setProperty("bgColour", str(option))
        self.style().polish(self)


class CancelButtonWidget(
    QtWidgets.QPushButton
):  
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
            "QPushButton[bgColour='0']{"
            "   background-color:"
            + NativeUI.colors["button_foreground_enabled"].name()
            + ";"
            "}"
            "QPushButton[bgColour='1']{"
            "background-color:" + NativeUI.colors["red"].name() + ";"
            "}"
            "QPushButton{"
            "   color: " + NativeUI.colors["button_background_enabled"].name() + ";"
            "   font-size: " + NativeUI.text_size + ";"
            "   border:none;"
            "}"
        )
        self.setProperty("bgColour", "0")
        self.setEnabled(False)

        self.setFixedHeight(50)
        # self.setFixedSize(QtCore.QSize(150, 50))

    def setColour(self, option):
        self.setEnabled(bool(float(option)))
        self.setProperty("bgColour", str(option))
        self.style().polish(self)


class OkSendButtonWidget(
    QtWidgets.QPushButton
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        iconpath_play = os.path.join(NativeUI.iconpath, "play-solid.png")

        # set icon color
        pixmap = QtGui.QPixmap(iconpath_play)
        mask = pixmap.mask()
        pixmap.fill(NativeUI.colors["button_background_enabled"])
        pixmap.setMask(mask)
        self.setIcon(QtGui.QIcon(pixmap))

        self.setStyleSheet(
            "QPushButton[bgColour='0']{"
            "   background-color: "
            + NativeUI.colors["button_foreground_enabled"].name()
            + ";"
            "}"
            "QPushButton[bgColour='1']{"
            "   background-color:" + NativeUI.colors["green"].name() + ";"
            "}"
            "QPushButton{"
            "   color: " + NativeUI.colors["button_background_enabled"].name() + ";"
            "   font-size: " + NativeUI.text_size + ";"
            "   border:none"
            "}"
            "font-size: " + NativeUI.text_size + ";"
            "border:none;"
        )
        self.setProperty("bgColour", "0")
        self.setEnabled(False)

        self.setFixedHeight(50)
        # self.setFixedSize(QtCore.QSize(150, 50))

    def setColour(self, option):
        self.setEnabled(bool(float(option)))
        self.setProperty("bgColour", str(option))
        self.style().polish(self)
