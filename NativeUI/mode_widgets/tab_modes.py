#!/usr/bin/env python3

"""
tab_modes.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Development"

from PySide2 import QtWidgets, QtGui, QtCore
from global_widgets.global_select_button import selectorButton

# from global_widgets.global_spinbox import simpleSpin
from global_widgets.template_set_values import TemplateSetValues


class TabModes(TemplateSetValues):
    def __init__(self, NativeUI, *args, **kwargs):
        super(TabModes, self).__init__(NativeUI, *args, **kwargs)
        self.settingsList = [
            [
                "Respiratory Rate",
                "/min",
                "respiratory_rate",
                "SET_TARGET_",
                "RESPIRATORY_RATE",
            ],
            ["Inhale Time", "s", "inhale_time", "SET_TARGET_", "INHALE_TIME"],
            ["IE Ratio", "", "ie_ratio", "SET_TARGET_", "IE_RATIO"],
            [
                "Inhale Trigger Sensitivity",
                "",
                "inhale_trigger_threshold",
                "SET_TARGET_",
                "INHALE_TRIGGER_THRESHOLD",
            ],
            [
                "Exhale Trigger Sensitivity",
                "",
                "exhale_trigger_threshold",
                "SET_TARGET_",
                "EXHALE_TRIGGER_THRESHOLD",
            ],
            [
                "Inhale Pressure",
                "",
                "inspiratory_pressure",
                "SET_TARGET_",
                "INSPIRATORY_PRESSURE",
            ],
            ["Inhale volume", "", "volume", "SET_TARGET_", "VOLUME"],
            ["Percentage O2", "", "fiO2_percent", "SET_TARGET_", "FIO2_PERCENT"],
        ]
        self.addModeStack(self.settingsList)
        self.addButtons()
        self.finaliseLayout()

    def _setColour(self, buttonWidg):
        for button, page in zip(self.buttonWidgets, self.pageList):
            if button == buttonWidg:
                button.setProperty("selected", "1")
                self.stack.setCurrentWidget(page)
            else:
                button.setProperty("selected", "0")
            button.style().unpolish(button)
            button.style().polish(button)
