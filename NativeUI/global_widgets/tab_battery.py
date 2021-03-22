#!/usr/bin/env python3

"""
tab_battery.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Benjamin Mummery"
__email__ = "benjamin.mummery@stfc.ac.uk"
__status__ = "Development"

import logging
import os

from PySide2 import QtCore, QtGui, QtWidgets


class TabBattery(QtWidgets.QWidget):
    """
    Widget that contains both the battery icon and a text readout of the current
    battery charge.
    """

    def __init__(self, NativeUI, *args, **kwargs):
        super(TabBattery, self).__init__(*args, **kwargs)
        self.NativeUI = NativeUI

        layout = QtWidgets.QHBoxLayout(self)
        self.widgets = [BatteryIcon(NativeUI), BatteryText(NativeUI)]

        for widget in self.widgets:
            layout.addWidget(widget)

        self.setLayout(layout)
        self.setFixedSize(200, 75)

        self.battery_power = False
        self.mains_power = False
        self.battery_percent = 0
        self.electrical_problem = False

        self.status = {}
        self.set_default_status()

        self.update_value()

    def set_default_status(self) -> dict:
        """
        Set the default battery status, to be assumed until told otherwise.

        For safety, the default assumption is that the ventilator is on battery power
        with 0 % battery life remaining and an electrical problem.
        """
        self.status = {
            "on_mains_power": False,
            "on_battery_power": True,
            "battery_percent": 0,
            "electrical_problem": "No Battery Info",
        }
        return self.status

    @QtCore.Slot(dict)
    def update_value(self):
        battery_data = self.NativeUI.get_db("battery")

        # Update status
        try:
            self.status["on_mains_power"] = bool(battery_data["ok"])
        except KeyError:
            logging.debug("Keyerror in battery payload: 'ok'")
        try:
            self.status["on_battery_power"] = bool(battery_data["bat"])
        except KeyError:
            logging.debug("Keyerror in battery payload: 'bat'")
        try:
            self.status["battery_percent"] = self.compute_battery_percent(battery_data)
        except KeyError:
            logging.debug("Keyerror in battery payload: 'bat85'")
        try:
            if bool(battery_data["prob_elec"]):
                self.status["electrical_problem"] = "ERROR ELEC."
            else:
                self.status["electrical_problem"] = None
        except KeyError:
            logging.debug("Keyerror in battery payload: 'prob_elec'")

        # Sanity checks
        if self.status["on_mains_power"] == self.status["on_battery_power"]:
            # If there is conflicting information w.r.t. power source, report a problem
            self.status["on_mains_power"] = False
            self.status["on_battery_power"] = False
            self.status["electrical_problem"] = "ERROR ELEC."

        # Update widgets with new status
        for widget in self.widgets:
            widget.update_value(self.status)
        return 0

    def compute_battery_percent(self, battery_data: dict) -> float:
        """
        Determine the current battery percentage from the information in battery_data.

        As of 17/03/21 battery payloads only contain enough information to
        determine if the battery is above or below 85% battery life.

        Unless provided with specific information to the contrary, assume that the
        battery is on 0% so that we should never overestimate how much remains.
        """

        if battery_data["bat85"] == 1:
            return 85.0
        elif battery_data["bat85"] == 0:
            return 0.0

        return 0.0


class BatteryText(QtWidgets.QWidget):
    """
    """

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel("0 %")
        layout.addWidget(self.label)

        self.label.setStyleSheet(
            "background-color:" + NativeUI.colors["background"].name() + ";"
            "border: none;"
            "font:" + NativeUI.text_size + ";"
            "color:" + NativeUI.colors["foreground"].name() + ";"
        )

        self.setLayout(layout)

    def update_value(self, status):
        """"""
        if status["electrical_problem"] is not None:
            self.label.setText(status["electrical_problem"])
            return 0
        if status["on_mains_power"]:
            self.label.setText("")
            return 0

        self.label.setText(str(status["battery_percent"]) + " %")
        return 0


class BatteryIcon(QtWidgets.QWidget):
    """
    Widget to display the current battery icon
    """

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        iconsize = QtCore.QSize(25, 25)
        self.__icon_list = self.__make_icon_list()
        self.__mains_icon = os.path.join(self.NativeUI.iconpath, "plug-solid.png")
        self.__alert_icon = os.path.join(
            self.NativeUI.iconpath, "exclamation-triangle-solid.png"
        )
        self.__icon_percentiles = self.__make_percentile_ranges()

        layout = QtWidgets.QVBoxLayout()
        self.icon_display = QtWidgets.QPushButton("")
        self.icon_display.setIconSize(iconsize)
        layout.addWidget(self.icon_display)

        self.icon_display.setEnabled(False)
        self.icon_display.setStyleSheet(
            "background-color:" + NativeUI.colors["background"].name() + ";"
            "border: none"
        )

        self.setLayout(layout)

    def update_value(self, status):
        """
        Update the icon to match that of the specified battery percentage value.
        """
        if status["electrical_problem"] is not None:
            self.icon_display.setIcon(QtGui.QIcon(self.__alert_icon))
            return 0
        if status["on_mains_power"]:
            self.icon_display.setIcon(QtGui.QIcon(self.__mains_icon))
            return 0

        self.icon_display.setIcon(
            QtGui.QIcon(
                self.__icon_list[self.__get_range_index(status["battery_percent"])]
            )
        )
        return 0

    def __get_range_index(self, battery_percent):
        """
        Determine which of the percentile ranges the current battery value falls into.
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

        return [(a, b) for a, b in zip(lower_bounds, upper_bounds)]

    def __make_icon_list(self):
        """
        Make a list of paths to battery icons, in order of the battery charge
        they represent
        """
        icon_list = [
            "battery-empty-solid.png",
            "battery-quarter-solid.png",
            "battery-half-solid.png",
            "battery-three-quarters-solid.png",
        ]
        icon_list = [os.path.join(self.NativeUI.iconpath, icon) for icon in icon_list]
        return icon_list
