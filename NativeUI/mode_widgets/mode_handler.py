from global_widgets.global_spinbox import labelledSpin
from widget_library.ok_cancel_buttons_widget import OkButtonWidget, CancelButtonWidget, OkSendButtonWidget
#from global_widgets.global_send_popup import SetConfirmPopup
from widget_library.spin_buttons_widget import SpinButton, SpinButtonsWidget

from PySide2 import QtWidgets, QtGui, QtCore
from handler_library.handler import PayloadHandler
import logging
import json

class ModeHandler(PayloadHandler):

    modeSwitched = QtCore.Signal(str)
    UpdateModes = QtCore.Signal(dict)
    OpenPopup = QtCore.Signal(PayloadHandler, list)
    settingToggle = QtCore.Signal(str)

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(['TARGET'],*args, **kwargs)
        #super(TabModes, self).__init__(NativeUI, *args, **kwargs)
        self.NativeUI = NativeUI
        self.spinDict = {}
        self.buttonDict = {}
        self.radioDict = {}
        self.commandList = []
        self.mainSpinDict = {}
        self.mainButtonDict = {}
        self.modeList = self.NativeUI.modeList + ['CURRENT']
        self.manuallyUpdatedBoolDict = { mode: False for mode in self.modeList }
        self.mainManuallyUpdated = False
        self.activeMode = self.modeList[0]

        with open("NativeUI/configs/mode_config.json") as json_file:
            modeDict = json.load(json_file)

        self.relevantKeys = [setting[2] for setting in modeDict['settings']]

    def add_widget(self, widget, key: str):
        if isinstance(widget, labelledSpin):
            self.spinDict[key] = widget
        if isinstance(widget, OkButtonWidget) or isinstance(widget, CancelButtonWidget) or isinstance(widget, OkSendButtonWidget):
            if self.get_mode(key) == 'CURRENT':
                self.mainButtonDict[key] = widget
            else:
                self.buttonDict[key] = widget
        if isinstance(widget, QtWidgets.QRadioButton):
            self.radioDict[key] = widget
        if isinstance(widget, SpinButton):
            self.mainSpinDict[key] = widget

    def active_payload(self, *args) -> int:
        target_data = self.get_db()
        outdict = {}

        for key in self.relevantKeys:
            try:
                outdict[key] = target_data[key]
            except KeyError:
                logging.debug("Invalid key %s in measurement database", key)

        self.UpdateModes.emit(outdict)
        return 0


    def handle_okbutton_click(self, key):
        print('ok')
        print(key)
        mode = self.get_mode(key)
        print(mode)
        message, command = [], []
        for widget in self.spinDict:
            if (mode in widget) and self.spinDict[widget].manuallyUpdated:
                print('True')
                setVal = self.spinDict[widget].get_value()
                message.append("set" + widget + " to " + str(setVal))
                command.append(
                    [
                        self.spinDict[widget].cmd_type,
                        self.spinDict[widget].cmd_code,
                        setVal,
                    ]
                )
        # create a signal emitting message, command, handler identifier - in nativeui connect to a popup widget
        # command sending should occur in handler
        self.commandList = command
        self.OpenPopup.emit(self,message)

    def handle_mainokbutton_click(self):
        message, command = [], []
        for widget in self.mainSpinDict:
            if self.mainSpinDict[widget].manuallyUpdated:
                setVal = self.mainSpinDict[widget].get_value()
                message.append("set" + widget + " to " + str(setVal))
                command.append(
                    [
                        self.mainSpinDict[widget].cmd_type,
                        self.mainSpinDict[widget].cmd_code,
                        setVal,
                    ]
                )
        # create a signal emitting message, command, handler identifier - in nativeui connect to a popup widget
        # command sending should occur in handler
        self.commandList = command

        self.OpenPopup.emit(message)

    def sendCommands(self):
        if self.commandList == []:
            a=1
        else:
            for command in self.commandList:
                self.NativeUI.q_send_cmd(*command)
            self.modeSwitched.emit(self.activeMode)
            self.commandSent()
        return 0

    def commandSent(self):
        self.commandList = []
        for widget in self.spinDict:
            if self.activeMode in widget:
                self.spinDict[widget].manuallyUpdated = False
        for widget in self.mainSpinDict:
            self.mainSpinDict[widget].manuallyUpdated = False


        self.active_payload()
        self.refresh_button_colour()
        self.refresh_main_button_colour()

    def handle_manual_change(self, changed_spin_key):
        self.active_payload()
        self.refresh_button_colour()
        self.refresh_main_button_colour()

    def handle_radio_toggled(self, radioButtonState, radioKey):
        """TODO Docstring"""
        mode = self.get_mode(radioKey)
        spinKey= radioKey.replace('radio', 'spin')
        spinBox = self.spinDict[spinKey]
        spinBox.setEnabled(radioButtonState)

        if mode == self.NativeUI.currentMode:
            self.settingToggle.emit(spinBox.label)

    def refresh_button_colour(self):
        self.manuallyUpdatedBoolDict = { mode: False for mode in self.modeList }
        for spin in dict(self.spinDict):
            self.manuallyUpdatedBoolDict[self.get_mode(spin)] = self.manuallyUpdatedBoolDict[self.get_mode(spin)] or self.spinDict[spin].manuallyUpdated
        for button in dict(self.buttonDict):
            mode = str(self.get_mode(button))
            if isinstance(self.buttonDict[button], OkSendButtonWidget) and (mode != self.NativeUI.currentMode):
                self.buttonDict[button].setColour(str(int(True)))
            else:
                self.buttonDict[button].setColour(str(int(self.manuallyUpdatedBoolDict[mode])))


    def refresh_main_button_colour(self):
        self.manuallyUpdatedBoolDict['CURRENT'] = False
        for spin in self.mainSpinDict:
            self.manuallyUpdatedBoolDict['CURRENT'] = self.manuallyUpdatedBoolDict['CURRENT'] or self.mainSpinDict[spin].manuallyUpdated
        for button in self.mainButtonDict:
            self.mainButtonDict[button].setColour(str(int(self.manuallyUpdatedBoolDict['CURRENT'])))

    def get_mode(self, key: str):
        for mode in self.modeList:
            if mode in key:
                return mode
