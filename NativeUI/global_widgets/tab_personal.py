#!/usr/bin/env python3

"""
tab_personal.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

from PySide2 import QtWidgets, QtCore


class TabPersonalDisplay(QtWidgets.QWidget):
    """
    Display the current status of the personal information database
    """

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.info_label = QtWidgets.QLabel("Person person, 55kg")
        self.info_label.setStyleSheet(
            "font:" + NativeUI.text_size + ";"
            "color:" + NativeUI.colors["page_foreground"].name() + ";"
        )
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(self.info_label)
        self.setLayout(hlayout)
