from PySide2 import QtWidgets, QtGui, QtCore
from global_widgets.global_spinbox import simpleSpin
from global_widgets.global_select_button import selectorButton
from global_widgets.global_send_popup import SetConfirmPopup
from global_widgets.template_set_values import TemplateSetValues

class TabExpert(
    TemplateSetValues
): 
    def __init__(self, *args, **kwargs):
        super(TabExpert, self).__init__(*args, **kwargs)
        self.liveUpdating = True
        self.modifications = []
        controlDict = {
            "Buffers": [
                ["Calibration", "ms", "duration_calibration"],
                ["Purge", "ms", "duration_buff_purge"],
                ["Flush", "ms", "duration_buff_flush"],
                ["Pre-fill", "ms", "duration_buff_prefill"],
                ["Fill", "ms", "duration_buff_prefill"],
                ["Pre-inhale", "ms", "duration_buff_pre_inhale"],
            ],
            "PID": [
                ["KP", "", "kp"],
                ["KI", "", "ki"],
                ["KD", "", "kd"],
                ["PID Gain", "", "pid_gain"],
                ["Max. PP", "", "max_patient_pressure"],
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
                ["Inhale", "ms", "duration_inhale"],
                ["Pause", "ms", "duration_pause"],
                ["Exhale fill", "ms", "duration_exhale"],
                ["Exhale", "ms", "duration_exhale"],
                ["I:E Ratio", "", "inhale_exhale_ratio"],
            ],
        }

        self.addExpertControls(controlDict)
        self.addButtons()
        self.finaliseLayout()

        # self.timer = QtCore.QTimer()
        # self.timer.setInterval(160)  # just faster than 60Hz
        # self.timer.timeout.connect(self.update_settings_data)
        # self.timer.start()

