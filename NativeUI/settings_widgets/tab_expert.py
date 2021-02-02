from PySide2 import QtWidgets, QtGui, QtCore
import sys


class simpleSpin(QtWidgets.QWidget):
    def __init__(self, infoArray, *args, **kwargs):
        super(simpleSpin, self).__init__(*args, **kwargs)

        self.label, self.units, self.tag = infoArray

        layout = QtWidgets.QHBoxLayout()

        textStyle = "color:white; font: 16pt"

        self.nameLabel = QtWidgets.QLabel(self.label)
        self.nameLabel.setStyleSheet(textStyle)
        self.nameLabel.setAlignment(QtCore.Qt.AlignRight)
        layout.addWidget(self.nameLabel)

        self.simpleSpin = QtWidgets.QSpinBox()
        self.simpleSpin.setStyleSheet(
            """QSpinBox{background-color:white; width:100px; font:16pt}
                                        QSpinBox[colour="0"]{color:black}
                                        QSpinBox[colour="1"]{color:red}
                                        QSpinBox::up-button{width:20; }
                                        QSpinBox::down-button{width:20; }
                                        """
        )
        self.simpleSpin.setProperty("colour", "1")
        self.simpleSpin.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus
        )
        self.simpleSpin.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.simpleSpin)

        self.unitLabel = QtWidgets.QLabel(self.units)
        self.unitLabel.setStyleSheet(textStyle)
        self.unitLabel.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(self.unitLabel)

        self.setLayout(layout)

    def update_value(self):
        newVal = (
            self.parent()
            .parent()
            .parent()
            .parent()
            .parent()
            .parent()
            .readback[self.tag]
        )
        self.simpleSpin.setValue(newVal)


class TabExpert(
    QtWidgets.QWidget
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, *args, **kwargs):
        super(TabExpert, self).__init__(*args, **kwargs)

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
                ["Purge", "", "valve_purge"],
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
        grid.addWidget(self.okButton, i, 0, 1, 3)

        self.cancelButton = QtWidgets.QPushButton()
        self.cancelButton.setStyleSheet(
            "height:50px; background-color:white; border-radius:4px;"
        )
        grid.addWidget(self.cancelButton, i, 3, 1, 3)

        self.setLayout(grid)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(160)  # just faster than 60Hz
        self.timer.timeout.connect(self.update_settings_data)
        self.timer.start()

    def update_settings_data(self):
        for spinBox in self.spinDict:
            self.spinDict[spinBox].update_value()
