#!/usr/bin/env python3
import logging
import os
import pyqtgraph as pg
import numpy as np
from PySide2 import QtWidgets, QtCore, QtGui
from pyqtgraph import PlotWidget, plot, mkColor
from hevclient import HEVClient
import sys


class customLabel(QtWidgets.QLabel):
    def __init__(self, text):
        super().__init__(text)
        # self.setText('test text')
        # self.setIcon(icon)
        self.setStyleSheet(
            "color: white;background-color: black;height:100px;width:100px"
        )


class TabLabels(QtWidgets.QWidget):
    def __init__(self, port=54322, *args, **kwargs):
        super(TabLabels, self).__init__(*args, **kwargs)

        self.history_length = 500
        self.time_range = 30
        self.port = port

        layout = QtWidgets.QVBoxLayout()

        self.label1 = customLabel("label1")
        layout.addWidget(self.label1)
        self.label2 = customLabel("label2")
        layout.addWidget(self.label2)
        self.label3 = customLabel("label3")
        layout.addWidget(self.label3)
        self.label4 = customLabel("label4")
        layout.addWidget(self.label4)
        self.setLayout(layout)

    # self.timer = QtCore.QTimer()
    # self.timer.setInterval(16) # just faster than 60Hz
    # self.timer.timeout.connect(self.updateLabels) #updates without checking if new data arrived?
    # self.timer.start()

    def updateLabels(self):
        self.label1.setText(str(self.parent().parent().plots[-1, 1]))


if __name__ == "__main__":
    # parse args and setup logging
    # setup pyqtplot widget
    app = QtWidgets.QApplication(sys.argv)
    dep = TabLabels()
    dep.show()
    app.exec_()
