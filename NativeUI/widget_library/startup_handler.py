from global_widgets.global_spinbox import labelledSpin
from widget_library.startup_calibration_widget import calibrationWidget
from widget_library.ok_cancel_buttons_widget import OkButtonWidget, CancelButtonWidget, OkSendButtonWidget
from global_widgets.global_send_popup import SetConfirmPopup
from PySide2.QtWidgets import QRadioButton
from datetime import datetime
import json
from PySide2 import QtWidgets, QtGui, QtCore

class StartupHandler(QtWidgets.QWidget):  # chose QWidget over QDialog family because easier to modify

    UpdateModes = QtCore.Signal(dict)
    OpenPopup = QtCore.Signal(list)
    settingToggle = QtCore.Signal(str)

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.NativeUI = NativeUI
        self.buttonDict = {}
        self.spinDict = {}
        self.calibDict = {}
        self.modeRadioDict = {}
        self.settingsRadioDict = {}

    def add_widget(self, widget, key: str):
        if isinstance(widget, labelledSpin):
            self.spinDict[key] = widget
            widget.cmd_type = widget.cmd_type.replace('startup', 'CURRENT')
        if isinstance(widget, calibrationWidget):
            self.calibDict[key] = widget
        if isinstance(widget, OkButtonWidget) or isinstance(widget, CancelButtonWidget) or isinstance(widget,OkSendButtonWidget):
            self.buttonDict[key] = widget
        if isinstance(widget, QRadioButton):
            if widget.text() in self.NativeUI.modeList:
                self.modeRadioDict[key] = widget
            else:
                self.settingsRadioDict[key] = widget

    def handle_mode_radiobutton(self, checked, radio):
        if checked:
            self.NativeUI.currentMode = radio.text()

    def handle_settings_radiobutton(self, radioButtonState, radioKey):
        """TODO Docstring"""
        mode = self.get_mode(radioKey)
        spinKey= radioKey.replace('radio', 'spin')
        spinBox = self.spinDict[spinKey]
        spinBox.setEnabled(radioButtonState)

        if mode == self.NativeUI.currentMode:
            self.settingToggle.emit(spinBox.label)

    def handle_calibrationPress(self, calibrationWidget):
        calibrationWidget.progBar.setValue(100)
        calibrationWidget.lineEdit.setText('completed')

        with open('NativeUI/configs/startup_config.json', 'r') as json_file:
            startupDict = json.load(json_file)
            startupDict[calibrationWidget.key]['last_performed'] = int(datetime.now().timestamp())
        with open('NativeUI/configs/startup_config.json', 'w') as json_file:
            json.dump(startupDict, json_file)


    def handle_sendbutton(self):
        message, command = [], []
        for widget in self.spinDict:
            setVal = self.spinDict[widget].get_value()
            message.append("set" + widget + " to " + str(setVal))
            command.append(
                [
                    self.spinDict[widget].cmd_type,
                    self.spinDict[widget].cmd_code,
                    setVal,
                ]
            )
        for com in command:
            self.NativeUI.q_send_cmd(*com)
        self.NativeUI.q_send_cmd(
            "SET_MODE", self.NativeUI.currentMode.replace("/", "_").replace("-", "_")
        )


    def handle_nextbutton(self, stack):
        currentIndex = stack.currentIndex()
        nextIndex = currentIndex + 1
        totalLength = stack.count()
        stack.setCurrentIndex(nextIndex)
        if nextIndex == totalLength -1:
            self.buttonDict['nextButton'].setColour(0)
        else:
            self.buttonDict['nextButton'].setColour(1)
        self.buttonDict['backButton'].setColour(1)

    def handle_backbutton(self, stack):
        currentIndex = stack.currentIndex()
        nextIndex = currentIndex - 1
        stack.setCurrentIndex(nextIndex)
        if nextIndex == 0:
            self.buttonDict['backButton'].setColour(0)
        else:
            self.buttonDict['backButton'].setColour(1)
        self.buttonDict['nextButton'].setColour(1)

    def get_mode(self, key: str):
        for mode in self.NativeUI.modeList:
            if mode in key:
                return mode
