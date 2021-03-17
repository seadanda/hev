#!/usr/bin/env python3

"""
tab_top_bar.py

Part of NativeUI. Provides the TabTopBar widget.
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

from global_widgets.tab_battery import TabBattery
from global_widgets.tab_personal import TabPersonal
from global_widgets.tab_modeswitch_button import TabModeswitchButton
from PySide2 import QtCore, QtGui, QtWidgets


class TabTopBar(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QHBoxLayout(self)
        self.tab_modeswitch = TabModeswitchButton(NativeUI)
        self.tab_personal = TabPersonal(NativeUI)
        self.tab_battery = TabBattery(NativeUI)
        self.widgets = [self.tab_modeswitch, self.tab_personal, self.tab_battery]
        for widget in self.widgets:
            layout.addWidget(widget)
        self.setLayout(layout)
