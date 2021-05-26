#!/usr/bin/env python3

"""
info_display_widgets.py

Simple widgets to display various system information parameters including version
number(s), time since last maintenance, and time since last update.
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Benjamin Mummery"
__email__ = "benjamin.mummery@stfc.ac.uk"
__status__ = "Development"

import logging
from PySide2 import QtCore, QtWidgets


class VersionDisplayWidget(QtWidgets.QLabel):
    """
    Widget that displays the current version number.

    We don't need to override setFont as long as we're just subclassing the QLabel
    widget. If we later expand this class to include more complexity, we'll have to add
    setFont as a method to propogate the font to any subwidgets.
    """

    def __init__(self, colors, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__mcu_version: str = "???"
        self.__mcu_hash: str = None
        self.__ui_version: str = "???"
        self.__ui_hash: str = None

        self.setStyleSheet(
            "background-color:" + colors["page_background"].name() + ";"
            "border: none;"
            "color:" + colors["page_foreground"].name() + ";"
        )

        self.__refresh_display()

    def __refresh_display(self) -> int:
        """
        Update the display to show the current values of __ui_version and __mcu_version.
        """
        display_text = ""
        display_text += "MCU Software Version: %s" % self.__mcu_version
        if self.__mcu_hash is not None:
            display_text += " (%s)" % self.__mcu_hash
        display_text += "<br>UI Software Version: %s" % self.__ui_version
        if self.__ui_hash is not None:
            display_text += " (%s)" % self.__ui_hash
        self.setText(display_text)
        return 0

    @QtCore.Slot(str)
    def update_UI_version(self, version: str) -> int:
        """
        Update the value shown for the UI version
        """
        self.__ui_version = version
        self.__refresh_display()
        return 0

    @QtCore.Slot(str)
    def update_UI_hash(self, hash: str) -> int:
        """
        Update the value shown for the UI hash
        """
        self.__ui_hash = hash
        self.__refresh_display()
        return 0

    @QtCore.Slot(str)
    def update_mcu_version(self, version: str) -> int:
        """
        Update the value shown for the MCU version
        """
        self.__mcu_version = version
        self.__refresh_display()
        return 0

    @QtCore.Slot(str)
    def update_mcu_version(self, hash: str) -> int:
        """
        Update the value shown for the MCU hash
        """
        self.__mcu_hash = hash
        self.__refresh_display()
        return 0

    def set_size(self, x: int, y: int) -> int:
        """
        Set the size of the widget.
        """
        self.setFixedSize(x, y)
        return 0


class MaintenanceTimeDisplayWidget(QtWidgets.QLabel):
    """
    Widget that displays the time since the last maintenance.
    """

    def __init__(self, colors, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__time_since_maintenance: str = "???"
        self.__time_to_maintenance: str = "???"
        self.__maintenance_needed: bool = True

        self.__normal_color = colors["page_foreground"].name()
        self.__alert_color = colors["red"].name()

        self.setStyleSheet(
            "background-color:" + colors["page_background"].name() + ";"
            "border: none;"
            "color:" + self.__normal_color + ";"
        )

        self.__refresh_display()

    def __refresh_display(self) -> int:
        """
        Update the display to show the current values of time to, and since,
        maintenance.
        """
        self.setText(
            "%s since last maintenance. Maintenance due in %s."
            % (self.__time_since_maintenance, self.__time_to_maintenance)
        )
        if self.__maintenance_needed:
            self.setStyleSheet("color:%s" % self.__alert_color)
        else:
            self.setStyleSheet("color:%s" % self.__normal_color)
        return 0

    @QtCore.Slot(str, str, bool)
    def set_time_values(
        self,
        time_since_maintenance: str,
        time_to_maintenance: str,
        maintenance_needed: bool,
    ) -> int:
        """
        set the time since and to maintenance, and whether maintenance is needed.
        """
        self.__time_since_maintenance = time_since_maintenance
        self.__time_to_maintenance = time_to_maintenance
        self.__maintenance_needed = maintenance_needed
        return self.__refresh_display()


class UpdateTimeDisplayWidget(QtWidgets.QLabel):
    """
    Widget that displays the time since the last update.
    """

    def __init__(self, colors, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__time_since_update: str = "???"
        self.__time_to_update_check: str = "???"
        self.__update_check_needed: bool = True

        self.__normal_color = colors["page_foreground"].name()
        self.__alert_color = colors["red"].name()

        self.setStyleSheet(
            "background-color:" + colors["page_background"].name() + ";"
            "border: none;"
            "color:" + self.__normal_color + ";"
        )

        self.__refresh_display()

    def __refresh_display(self) -> int:
        """
        Update the display to show the current values of time to, and since,
        update.
        """
        self.setText(
            "%s since last update. Check for updates due in %s."
            % (self.__time_since_update, self.__time_to_update_check)
        )
        if self.__update_check_needed:
            self.setStyleSheet("color:%s" % self.__alert_color)
        else:
            self.setStyleSheet("color:%s" % self.__normal_color)
        return 0

    @QtCore.Slot(str, str, bool)
    def set_time_values(
        self,
        time_since_update: str,
        time_to_update_check: str,
        update_check_needed: bool,
    ) -> int:
        """
        set the time since and to maintenance, and whether maintenance is needed.
        """
        self.__time_since_update = time_since_update
        self.__time_to_update_check = time_to_update_check
        self.__update_check_needed = update_check_needed
        return self.__refresh_display()
