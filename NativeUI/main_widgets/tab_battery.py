#!/usr/bin/env python3

"""
tab_battery.py
"""

__author__     = "Benjamin Mummery"
__copyright__  = "© Copyright [] 2021" # TODO
__credits__    = ["Tiago Sarmento", "Benjamin Mummery", "Dónal Murray"]
__license__    = "GPL"
__version__    = "0.0.1"
__maintainer__ = "Benjamin Mummery"
__email__      = "benjamin.mummery@stfc.ac.uk"
__status__     = "Prototype"

import os
from PySide2 import QtCore, QtGui, QtWidgets


class TabBattery(QtWidgets.QWidget):
    """
    Widget that contains both the battery icon and a text readout of the current
    battery charge.
    """
    def __init__(self, *args, **kwargs):
        super(TabBattery, self).__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout(self)
        self.battery_icon = BatteryIcon()
        self.battery_text = BatteryText()
        layout.addWidget(self.battery_icon)
        layout.addWidget(self.battery_text)

        self.setLayout(layout)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(16)  # just faster than 60Hz
        self.timer.timeout.connect(self.battery_icon.update_value)
        self.timer.start()

class BatteryText(QtWidgets.QWidget):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel("0 %")
        layout.addWidget(self.label)

        self.label.setStyleSheet("background-color: transparent; border: 0px")

        self.setLayout(layout)

    def update_value(self):
        """
        """
        pass

class BatteryIcon(QtWidgets.QWidget):
    """
    Widget to display the current battery icon
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__icon_list = self.__make_icon_list()
        self.__icon_percentiles = self.__make_percentile_ranges()

        layout = QtWidgets.QVBoxLayout()
        self.icon_display = QtWidgets.QPushButton("")
        layout.addWidget(self.icon_display)

        self.icon_display.setEnabled(False)
        self.icon_display.setStyleSheet("background-color: transparent; border: 0px")

        self.setLayout(layout)

    def update_value(self):
        """
        """
        self.icon_display.setIcon(QtGui.QIcon(self.__icon_list[0]))
        data = vars(self.parent().parent().parent())["battery"]
        # print(data)
        # try:
        #     print(data)
        # finally:
        #     return

    def __make_percentile_ranges(self, zero_point:float=15):
        """
        zero_point: percentage of battery life at which the icon shows empty
        """
        if self.__icon_list is None:
            self.__icon_list = self.__make_icon_list()
        n_icons = len(self.__icon_list)
        percent_per_icon = 100.0/n_icons
        if percent_per_icon < zero_point:
            zero_point = percent_per_icon
        lower_bounds = [0.0]
        upper_bounds = [zero_point]
        while upper_bounds[-1] + percent_per_icon < 100:
            lower_bounds.append(upper_bounds[-1])
            upper_bounds.append(upper_bounds[-1] + percent_per_icon)
        lower_bounds.append(upper_bounds[-1])
        upper_bounds.append(100.0)

        # assert len(lower_bounds) == len(self.__icon_list)
        # assert len(upper_bounds) == len(lower_bounds)

        return [(a, b) for a, b in zip(lower_bounds, upper_bounds)]


    def __make_icon_list(self):
        """
        Make a list of paths to battery icons, in order of the battery charge 
        they represent
        """
        iconpath = "hev-display/assets/svg" # TODO better path
        icon_list = [
            'battery-empty-solid.svg', 
            'battery-quarter-solid.svg',
            'battery-half-solid.svg',
            'battery-three-quarters-solid.svg',
        ]
        icon_list = [os.path.join(iconpath, icon) for icon in icon_list]
        return icon_list

