import logging
import argparse
import sys
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout
from hevclient import HEVClient
from tab_plots import TabPlots

class MainView(QWidget):
    def __init__(self, *args, **kwargs):
        super(MainView, self).__init__(*args, **kwargs)
        hlayout = QHBoxLayout()
        vlayout = QVBoxLayout()
        self.tab_plots = TabPlots()
        vlayout.addWidget(self.tab_plots)
        hlayout.addLayout(vlayout)
        self.setLayout(hlayout)