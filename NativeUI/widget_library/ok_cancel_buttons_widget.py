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


class styledButton(QtWidgets.QPushButton):
    def __init__(self, NativeUI, colour, iconpath_play, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # set icon color
        pixmap = QtGui.QPixmap(iconpath_play)
        mask = pixmap.mask()
        pixmap.fill(NativeUI.colors["button_background_enabled"])
        pixmap.setMask(mask)
        self.setIcon(QtGui.QIcon(pixmap))

        self.setStyleSheet(
            "QPushButton[bgColour='0']{background-color: "
            + NativeUI.colors["page_foreground"].name()
            + ";}"
            "QPushButton[bgColour='1']{background-color: "
            + NativeUI.colors[colour].name()
            + ";}"
            "QPushButton{color: " + NativeUI.colors["page_background"].name() + ";"
            "border-color: " + NativeUI.colors["page_foreground"].name() + ";"
            "border-radius: 8px;"
            "border:none}"
        )
        self.setFont(NativeUI.text_font)
        self.setProperty("bgColour", "0")
        self.setEnabled(False)

        self.setFixedHeight(50)
        # self.setFixedSize(QtCore.QSize(150, 50))

    def setColour(self, option):
        # print('setting colour again again')
        self.setEnabled(bool(float(option)))
        self.setProperty("bgColour", str(option))
        self.style().polish(self)


class OkButtonWidget(styledButton):
    def __init__(self, NativeUI, *args, **kwargs):
        iconpath_check = os.path.join(NativeUI.iconpath, "check-solid.png")
        super().__init__(NativeUI, "green", iconpath_check, *args, **kwargs)


class CancelButtonWidget(styledButton):
    def __init__(self, NativeUI, *args, **kwargs):
        iconpath_cross = os.path.join(NativeUI.iconpath, "times-solid.png")
        super().__init__(NativeUI, "red", iconpath_cross, *args, **kwargs)


class OkSendButtonWidget(
    styledButton
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, NativeUI, *args, **kwargs):
        iconpath_play = os.path.join(NativeUI.iconpath, "play-solid.png")
        super().__init__(NativeUI, "green", iconpath_play, *args, **kwargs)
