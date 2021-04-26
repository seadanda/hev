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
from datetime import datetime
import os


class calibrationWidget(
    QtWidgets.QWidget
):
    def __init__(self, NativeUI, key, infoDict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.NativeUI = NativeUI
        self.key = key
        self.infoDict = infoDict
        hlayout = QtWidgets.QHBoxLayout()

        self.button = QtWidgets.QPushButton(infoDict["label"])
        hlayout.addWidget(self.button)

        self.progBar = QtWidgets.QProgressBar()
        hlayout.addWidget(self.progBar)

        self.lastTime = datetime.fromtimestamp(infoDict['last_performed'])
        self.lastTime.strftime('%d-%m-%y %H:%M')
        self.lineEdit = QtWidgets.QLineEdit(str(self.lastTime))
        hlayout.addWidget(self.lineEdit)

        self.setLayout(hlayout)