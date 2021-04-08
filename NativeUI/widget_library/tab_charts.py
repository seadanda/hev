#!/usr/bin/env python3

"""
tab_charts.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Development"

from PySide2 import QtWidgets, QtGui, QtCore
import sys


class TabChart(
    QtWidgets.QWidget
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, *args, **kwargs):
        super(TabChart, self).__init__(*args, **kwargs)

        label = QtWidgets.QLabel("charting")
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(label)
        self.setLayout(vlayout)
