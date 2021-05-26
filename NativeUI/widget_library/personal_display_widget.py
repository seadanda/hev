#!/usr/bin/env python3

"""
personal_display_widget.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

from PySide2 import QtGui, QtWidgets, QtCore


class PersonalDisplayWidget(QtWidgets.QWidget):
    """
    Display the current status of the personal information database
    """

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.info_label = QtWidgets.QLabel("No personal information set.")
        self.info_label.setStyleSheet(
            "color:" + NativeUI.colors["page_foreground"].name() + ";"
        )
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.info_label)
        self.setLayout(hlayout)

    def set_size(self, x: int, y: int, spacing=None) -> int:
        """
        Set the size of the personal display widget.

        A size can be left free to change by setting its value to None.
        """
        x_set, y_set = False, False
        if x is not None:
            x_set = True
        if y is not None:
            y_set = True

        if x_set and y_set:
            self.setFixedSize(x, y)
            self.info_label.setFixedSize(x, y)
        elif x_set and not y_set:
            self.setFixedWidth(x)
            self.info_label.setFixedWidth(x)
        elif y_set and not x_set:
            self.setFixedHeight(y)
            self.info_label.setFixedHeight(y)
        else:
            raise ValueError("set_size called with no size information")

        return 0

    def setFont(self, font: QtGui.QFont) -> int:
        """
        Overrides the existing setFont method in order to propogate the change to
        subwidgets.
        """
        self.info_label.setFont(font)
        return 0

    @QtCore.Slot(dict)
    def update_status(self, new_info: dict) -> int:
        """
        Update the display information.
        """
        outtxt = "{name}, {height}m".format(**new_info)
        self.info_label.set_text(outtxt)
        return 0
