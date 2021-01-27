#!/usr/bin/env python3
import logging
import os
import pyqtgraph as pg
import numpy as np
from PySide2 import QtWidgets, QtCore, QtGui
from pyqtgraph import PlotWidget, plot, mkColor
from hevclient import HEVClient
import sys


class customSpinBox(QtWidgets.QSpinBox):
    def __init__(self, iconPath: str):
        super().__init__()
        # self.setStyleSheet("border:none; background-image:url('" + iconPath + "');height:100px;width:100px")


class TabSpin(QtWidgets.QWidget):
    def __init__(self, port=54322, *args, **kwargs):
        super(TabSpin, self).__init__(*args, **kwargs)

        layout = QtWidgets.QHBoxLayout()
        self.Spin1 = customSpinBox(
            ""
        )  # QtWidgets.QPushSpin(QtGui.QIcon('SpinIcons/settings1.jpeg'),'')
        # self.Spin1.setIcon(QtGui.QIcon('settings1.jpeg'))
        # self.Spin1.setStyleSheet("border: none; background-image: url('SpinIcons/settings1.jpeg');height:50px")
        layout.addWidget(self.Spin1)
        self.Spin2 = customSpinBox(
            "SpinIcons/settings2.jpeg"
        )  # QtWidgets.QPushSpin('test Spin number 2?')
        # self.Spin2.setStyleSheet('border: none')
        layout.addWidget(self.Spin2)
        self.Spin3 = (
            QtWidgets.QSpinBox()
        )  # customSpinBox('SpinIcons/settings3.jpeg')#QtWidgets.QPushSpin('test Spin number three?')
        layout.addWidget(self.Spin3)
        self.Spin4 = customSpinBox(
            "SpinIcons/settings4.jpeg"
        )  # QtWidgets.QPushSpin('test Spin will it show up?')
        layout.addWidget(self.Spin4)
        self.setLayout(layout)


if __name__ == "__main__":
    # parse args and setup logging
    # setup pyqtplot widget
    app = QtWidgets.QApplication(sys.argv)
    dep = TabSpin()
    dep.show()
    app.exec_()
