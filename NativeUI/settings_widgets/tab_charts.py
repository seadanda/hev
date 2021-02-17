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
