#!/usr/bin/env python3

"""
tab_left_bar.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Benjamin Mummery"
__email__ = "benjamin.mummery@stfc.ac.uk"
__status__ = "Prototype"

from PySide2.QtCore import QSize
from global_widgets.tab_page_buttons import TabPageButtons
from global_widgets.tab_start_stop_buttons import TabStartStopStandbyButtons
from PySide2 import QtWidgets


class TabLeftBar(QtWidgets.QWidget):
    """
    TODO: docstring
    """

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout(self)

        button_width = 150

        self.tab_page_buttons = TabPageButtons(
            NativeUI, size=QSize(button_width, button_width)
        )
        self.tab_start_stop_buttons = TabStartStopStandbyButtons(
            NativeUI, size=QSize(button_width, int(button_width / 3))
        )

        self.widgets = [self.tab_page_buttons, self.tab_start_stop_buttons]

        for widget in self.widgets:
            layout.addWidget(widget)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)
