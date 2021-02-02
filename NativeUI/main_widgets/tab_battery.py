#!/usr/bin/env python3

"""
tab_battery.py
"""

__author__ = "Benjamin Mummery"
__copyright__ = "© Copyright [] 2021"  # TODO
__credits__ = ["Tiago Sarmento", "Benjamin Mummery", "Dónal Murray"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Benjamin Mummery"
__email__ = "benjamin.mummery@stfc.ac.uk"
__status__ = "Prototype"

import os

from PySide2 import QtCore, QtGui, QtWidgets


class TabBattery(QtWidgets.QWidget):
    """
    Widget that contains both the battery icon and a text readout of the current
    battery charge.
    """

    def __init__(self, *args, **kwargs):
        super(TabBattery, self).__init__(*args, **kwargs)

        layout = QtWidgets.QHBoxLayout(self)
        self.widgets = [BatteryIcon(), BatteryText()]

        for widget in self.widgets:
            layout.addWidget(widget)

        self.setLayout(layout)
        self.setMaximumSize(150, 50)

        # self.timer = QtCore.QTimer()
        # self.timer.setInterval(16)  # just faster than 60Hz
        # self.timer.timeout.connect(self.update_value())
        # self.timer.start()

    @QtCore.Slot(dict)
    def update_value(self, battery_info: dict):
        for widget in self.widgets:
            widget.update_value(battery_info["bat"])
        return 0


class BatteryText(QtWidgets.QWidget):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel("0 %")
        layout.addWidget(self.label)

        self.label.setStyleSheet(
            "background-color: transparent;" "border: 0px;" "color: white"
        )

        self.setLayout(layout)

    def update_value(self, battery_percent):
        """
        """
        self.label.setText(str(battery_percent) + " %")
        return 0


class BatteryIcon(QtWidgets.QWidget):
    """
    Widget to display the current battery icon
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__iconsize = QtCore.QSize(25, 25)
        self.__icon_list = self.__make_icon_list()
        self.__icon_percentiles = self.__make_percentile_ranges()

        layout = QtWidgets.QVBoxLayout()
        self.icon_display = QtWidgets.QPushButton("")
        self.icon_display.setIconSize(self.__iconsize)
        layout.addWidget(self.icon_display)

        self.icon_display.setEnabled(False)
        self.icon_display.setStyleSheet("background-color: transparent;" "border: 0px")

        self.setLayout(layout)
        self.update_value(0)

    def update_value(self, battery_percent):
        """
        Update the icon to match that of the specified battery percentage value.
        """
        self.icon_display.setIcon(
            QtGui.QIcon(self.__icon_list[self.__get_range_index(battery_percent)])
        )
        return 0

    def __get_range_index(self, battery_percent):
        """
        Determine which of the percentile ranges the current battery value falls into.
        TODO: do this in a less slow way!
        """
        i = 0
        while i < len(self.__icon_percentiles):
            if (battery_percent >= self.__icon_percentiles[i][0]) and (
                battery_percent < self.__icon_percentiles[i][1]
            ):
                return i
            i += 1
        raise Exception("battery value out of range?")

    def __make_percentile_ranges(self, zero_point: float = 15):
        """
        zero_point: percentage of battery life at which the icon shows empty
        """
        if self.__icon_list is None:
            self.__icon_list = self.__make_icon_list()
        n_icons = len(self.__icon_list)
        percent_per_icon = 100.0 / n_icons
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
        iconpath = self.__find_icons()
        icon_list = [
            "battery-empty-solid.svg",
            "battery-quarter-solid.svg",
            "battery-half-solid.svg",
            "battery-three-quarters-solid.svg",
        ]
        icon_list = [os.path.join(iconpath, icon) for icon in icon_list]
        return icon_list

    def __find_icons(self):
        """
        TODO: remove and find a way to do this without having this function
        both here and in tab_page_buttons.
        """
        initial_path = "hev-display/assets/svg/"
        # assume we're in the root directory
        temp_path = os.path.join(os.getcwd(), initial_path)
        if os.path.isdir(temp_path):
            return temp_path

        # assume we're one folder deep in the root directory
        temp_path = os.path.join("..", temp_path)
        if os.path.isdir(temp_path):
            return temp_path

        walk = os.walk(os.path.join(os.getcwd(), ".."))
        for w in walk:
            if "svg" in w[1]:
                temp_path = os.path.join(os.path.normpath(w[0]), "svg")
                return temp_path

        raise Exception(FileNotFoundError, "could not locate svg icon files")
