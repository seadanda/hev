#!/usr/bin/env python3

"""
tab_expert.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Benjamin Mummery"
__email__ = "benjamin.mummery@stfc.ac.uk"
__status__ = "Development"

from PySide2 import QtWidgets, QtGui, QtCore

# from global_widgets.global_spinbox import simpleSpin
from global_widgets.global_select_button import selectorButton
from global_widgets.global_send_popup import SetConfirmPopup
from global_widgets.template_set_values import TemplateSetValues


class TabExpert(TemplateSetValues):
    def __init__(self, NativeUI, *args, **kwargs):
        super(TabExpert, self).__init__(NativeUI, *args, **kwargs)
        self.liveUpdating = True
        self.setPacketType("readback")

        controlDict = {
            "Buffers": [
                [
                    "Calibration",
                    "ms",
                    "duration_calibration",
                    "SET_DURATION",
                    "CALIBRATION",
                    0,
                    1000,
                    50,
                    0,
                ],
                ["Purge", "ms", "duration_buff_purge", "SET_DURATION", "BUFF_PURGE"],
                ["Flush", "ms", "duration_buff_flush", "SET_DURATION", "BUFF_FLUSH"],
                [
                    "Pre-fill",
                    "ms",
                    "duration_buff_prefill",
                    "SET_DURATION",
                    "BUFF_PREFILL",
                ],
                ["Fill", "ms", "duration_buff_prefill", "SET_DURATION", "BUFF_FILL"],
                [
                    "Pre-inhale",
                    "ms",
                    "duration_buff_pre_inhale",
                    "SET_DURATION",
                    "BUFF_PRE_INHALE",
                ],
            ],
            "PID": [
                ["KP", "", "kp", "SET_PID", "KP"],
                ["KI", "", "ki", "SET_PID", "KI"],
                ["KD", "", "kd", "SET_PID", "KD"],
                ["PID Gain", "", "pid_gain", "SET_PID", "PID_GAIN"],
                [
                    "Max. PP",
                    "",
                    "max_patient_pressure",
                    "SET_PID",
                    "MAX_PATIENT_PRESSURE",
                ],
            ],
            "Valves": [
                ["Air in", "", "valve_air_in"],
                ["O2 in", "", "valve_o2_in"],
                ["Inhale", "", "valve_inhale"],
                ["Exhale", "", "valve_exhale"],
                ["Purge valve", "", "valve_purge"],
                ["Inhale Opening", "%", "valve_inhale_percent"],
                ["Exhale Opening", "%", "valve_exhale_percent"],
            ],
            "Breathing": [
                ["Inhale", "ms", "duration_inhale", "SET_DURATION", "INHALE"],
                ["Pause", "ms", "duration_pause", "SET_DURATION", "PAUSE"],
                ["Exhale fill", "ms", "duration_exhale", "SET_DURATION", "EXHALE_FILL"],
                ["Exhale", "ms", "duration_exhale", "SET_DURATION", "EXHALE"],
                ["I:E Ratio", "", "inhale_exhale_ratio"],
            ],
        }

        self.addExpertControls(controlDict)
        self.addButtons()
        self.finaliseLayout()

    # def update_settings_data(self):
    #     if self.liveUpdating:
    #         for widget in self.spinDict:
    #             self.spinDict[widget].update_readback_value()
