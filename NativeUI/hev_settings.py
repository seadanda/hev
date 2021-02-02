import argparse
import logging
import sys

# from PySide2.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout
from hevclient import HEVClient
# from PySide2.QtCore import Slot
from PySide2 import QtCore, QtGui, QtWidgets
from settings_widgets.tab_charts import TabChart
from settings_widgets.tab_expert import TabExpert


class SettingsView(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(SettingsView, self).__init__(*args, **kwargs)

        hTabLayout = QtWidgets.QHBoxLayout()
        self.expertButton = QtWidgets.QPushButton("Expert")
        self.expertButton.setStyleSheet("")
        self.expertButton.pressed.connect(self.expertPressed)
        hTabLayout.addWidget(self.expertButton)
        self.chartButton = QtWidgets.QPushButton("Charts")
        self.chartButton.setStyleSheet("")
        self.chartButton.pressed.connect(self.chartPressed)
        hTabLayout.addWidget(self.chartButton)
        self.expertButton3 = QtWidgets.QPushButton("Expert3")
        self.expertButton3.setStyleSheet("")
        hTabLayout.addWidget(self.expertButton3)

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
