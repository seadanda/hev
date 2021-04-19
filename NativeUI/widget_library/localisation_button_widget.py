#!/usr/bin/.hev_env python3

"""
localisation_button_widget.py

Part of NativeUI. Defines the LocalisationButtonWidget class to allow the user to set
the language for the interface.
"""

__author__ = "Benjamin Mummery"
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Benjamin Mummery"
__email__ = "benjamin.mummery@stfc.ac.uk"
__status__ = "Development"

from PySide2 import QtWidgets
import json
import os
from PySide2.QtCore import Signal


class LocalisationButtonWidget(QtWidgets.QPushButton):
    """
    TODO BM: add set_size and setFont
    """

    SetLocalisation = Signal(dict)

    def __init__(self, localisation_config_file_paths: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__localisation_dict: dict = {}
        self.__localisation_files_list: list = localisation_config_file_paths
        self.__current_localisation_index: int = -1

        self.set_localisation(0)

        self.pressed.connect(self.on_press)

    def on_press(self) -> int:
        """
        When the button is pressed, update the localisation.
        """
        index = self.__current_localisation_index + 1
        if index >= len(self.__localisation_files_list):
            index = 0
        self.set_localisation(index)
        return 0

    def set_localisation(self, index: int) -> int:
        """
        Set the current localisation parameters to those of the the specified index,
        then emit the SetLocalisation signal to propogate that change.
        """

        if index == self.__current_localisation_index:
            return 0

        self.__current_localisation_index = index

        self.__import_localisation_config()
        self.setText(self.__localisation_dict["language_name"])
        self.SetLocalisation.emit(self.__localisation_dict)
        return 0

    def __import_localisation_config(self) -> int:
        """
        Read in the current configuration
        """
        with open(
            self.__localisation_files_list[self.__current_localisation_index]
        ) as infile:
            self.__localisation_dict = json.load(infile)
        return 0
