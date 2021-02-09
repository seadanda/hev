import argparse
import logging
import sys

# from PySide2.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout
from hevclient import HEVClient

# from PySide2.QtCore import Slot
from PySide2 import QtCore, QtGui, QtWidgets
from mode_widgets.tab_modes import TabModes
from mode_widgets.tab_personal import TabPersonal
from global_widgets.global_select_button import selectorButton


class ModeView(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(ModeView, self).__init__(*args, **kwargs)

        hTabLayout = QtWidgets.QHBoxLayout()
        self.modeButton = selectorButton("Mode Settings")
        self.modeButton.setProperty("selected", "1")
        self.modeButton.style().polish(self.modeButton)
        self.modeButton.pressed.connect(self.modePressed)

        self.personalButton = selectorButton("Personal Settings")
        self.personalButton.pressed.connect(self.personalPressed)

        self.buttonWidgets = [self.modeButton, self.personalButton]
        for button in self.buttonWidgets:
            hTabLayout.addWidget(button)
            button.pressed.connect(lambda i=button: self.setColour(i))

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addLayout(hTabLayout)

        self.stack = QtWidgets.QStackedWidget()
        self.modeTab = TabModes()
        self.stack.addWidget(self.modeTab)
        self.personalTab = TabPersonal()
        self.stack.addWidget(self.personalTab)

        vlayout.addWidget(self.stack)
        self.setLayout(vlayout)

    def modePressed(self):
        self.stack.setCurrentWidget(self.modeTab)

    def personalPressed(self):
        self.stack.setCurrentWidget(self.personalTab)

    def setColour(self, buttonWidg):
        for button in self.buttonWidgets:
            if button == buttonWidg:
                button.setProperty("selected", "1")
            else:
                button.setProperty("selected", "0")
            button.style().unpolish(button)
            button.style().polish(button)
