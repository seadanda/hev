#!/usr/bin/env python3

"""
tab_personal.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

from PySide2 import QtGui, QtWidgets, QtCore


class TabPersonal(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(TabPersonal, self).__init__(*args, **kwargs)

        self.infoLabel = QtWidgets.QLabel("Person person, 55kg")
        self.infoLabel.setStyleSheet("font:15pt;color:white")
        self.infoLabel.setAlignment(QtCore.Qt.AlignCenter)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.infoLabel)
        self.setLayout(hlayout)
