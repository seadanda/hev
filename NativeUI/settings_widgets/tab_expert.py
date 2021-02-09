from PySide2 import QtWidgets, QtGui, QtCore
from global_widgets.global_spinbox import simpleSpin
from global_widgets.global_select_button import selectorButton
from global_widgets.global_send_popup import SetConfirmPopup


class TabExpert(
    QtWidgets.QWidget
):  # chose QWidget over QDialog family because easier to modify
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

        grid = QtWidgets.QGridLayout()
        self.spinDict = {}
        i = 0
        for section in controlDict.keys():

            self.titleLabel = QtWidgets.QLabel(section)
            self.titleLabel.setStyleSheet("background-color:white")
            self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
            grid.addWidget(self.titleLabel, i, 0, 1, 6)
            j = -1
            for boxInfo in controlDict[section]:
                j = j + 1
                # label, units = boxInfo, controlDict[section][boxInfo]
                self.spinDict[boxInfo[0]] = simpleSpin(boxInfo)
                grid.addWidget(
                    self.spinDict[boxInfo[0]], i + 1 + int(j / 3), 2 * (j % 3), 1, 2
                )

            i = i + 1 + int(j / 3) + 1

        self.okButton = QtWidgets.QPushButton()
        self.okButton.setStyleSheet(
            "height:50px; background-color:white; border-radius:4px;"
        )
        self.okButton.pressed.connect(self.okButtonPressed)
        grid.addWidget(self.okButton, i, 0, 1, 3)

        self.cancelButton = QtWidgets.QPushButton()
        self.cancelButton.setStyleSheet(
            "height:50px; background-color:white; border-radius:4px;"
        )
        self.cancelButton.pressed.connect(self.cancelButtonPressed)
        grid.addWidget(self.cancelButton, i, 3, 1, 3)

        self.setLayout(grid)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(160)  # just faster than 60Hz
        self.timer.timeout.connect(self.update_settings_data)
        self.timer.start()

    def update_settings_data(self):
        if self.liveUpdating:
            for spinBox in self.spinDict:
                self.spinDict[spinBox].update_readback_value()

    def okButtonPressed(self):
        message = []
        self.liveUpdating = True
        for widget in self.spinDict:
            # print(widget)
            if self.spinDict[widget].manuallyUpdated:
                setVal = self.spinDict[widget].simpleSpin.value()
                # print('manually updated')
                print("set" + widget + " to " + str(setVal))
                message.append(["set" + widget + " to " + str(setVal)])
                self.spinDict[widget].manuallyUpdated = False
        self.popup = SetConfirmPopup(message)
        self.popup.show()

    def cancelButtonPressed(self):
        self.liveUpdating = True
