#!/usr/bin/env python3
import logging
import os
import pyqtgraph as pg
import numpy as np
from PySide2 import QtWidgets, QtCore, QtGui
from pyqtgraph import PlotWidget, plot, mkColor
from hevclient import HEVClient
import sys

logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s"
)


class customButton(QtWidgets.QPushButton):
    def __init__(self, iconPath: str):
        super().__init__()
        # self.setIcon(icon)
        self.setStyleSheet(
            "border:none; background-image:url('"
            + iconPath
            + "');height:100px;width:100px"
        )


class TabButtons(QtWidgets.QWidget):
    def __init__(self, port=54322, *args, **kwargs):
        super(TabButtons, self).__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout()
        self.button1 = customButton("buttonIcons/settings1.jpeg")
        layout.addWidget(self.button1)
        self.button2 = customButton("buttonIcons/settings2.jpeg")
        layout.addWidget(self.button2)
        self.button3 = customButton("buttonIcons/settings3.jpeg")
        layout.addWidget(self.button3)
        self.button4 = customButton("buttonIcons/settings4.jpeg")
        layout.addWidget(self.button4)
        self.setLayout(layout)


if __name__ == "__main__":
    # parse args and setup logging
    # setup pyqtplot widget
    app = QtWidgets.QApplication(sys.argv)
    dep = TabButtons()
    dep.show()
    app.exec_()
