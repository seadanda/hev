import argparse
import logging
import sys

# from PySide2.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout
from hevclient import HEVClient

# from PySide2.QtCore import Slot
from PySide2 import QtCore, QtGui, QtWidgets
from settings_widgets.tab_charts import TabChart
from settings_widgets.tab_expert import TabExpert
from global_widgets.global_select_button import selectorButton


class SettingsView(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(SettingsView, self).__init__(*args, **kwargs)

        hTabLayout = QtWidgets.QHBoxLayout()
        self.expertButton = selectorButton("Expert")
        self.expertButton.setProperty("selected", "1")
        self.expertButton.style().polish(self.expertButton)
        self.expertButton.pressed.connect(self.expertPressed)

        self.chartButton = selectorButton("Charts")
        self.chartButton.pressed.connect(self.chartPressed)

        self.buttonWidgets = [self.expertButton, self.chartButton]
        for button in self.buttonWidgets:
            hTabLayout.addWidget(button)
            button.pressed.connect(lambda i=button: self.setColour(i))

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addLayout(hTabLayout)

        self.stack = QtWidgets.QStackedWidget()
        self.expertTab = TabExpert()
        self.stack.addWidget(self.expertTab)
        self.chartTab = TabChart()
        self.stack.addWidget(self.chartTab)

        vlayout.addWidget(self.stack)
        self.setLayout(vlayout)

    def expertPressed(self):
        self.stack.setCurrentWidget(self.expertTab)

    def chartPressed(self):
        self.stack.setCurrentWidget(self.chartTab)

    def change(self):
        print("pressed")
        self.parent().setCentralWidget(self.parent().main_view)

    def setColour(self, buttonWidg):
        for button in self.buttonWidgets:
            if button == buttonWidg:
                button.setProperty("selected", "1")
            else:
                button.setProperty("selected", "0")
            button.style().unpolish(button)
            button.style().polish(button)
