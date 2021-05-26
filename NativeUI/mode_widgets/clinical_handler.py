from global_widgets.global_spinbox import labelledSpin
from widget_library.ok_cancel_buttons_widget import OkButtonWidget, CancelButtonWidget, OkSendButtonWidget
#from global_widgets.global_send_popup import SetConfirmPopup
from widget_library.spin_buttons_widget import SpinButton

from PySide2 import QtWidgets, QtGui, QtCore
from handler_library.handler import PayloadHandler
import logging
import json

class ClinicalHandler(PayloadHandler):

    #modeSwitched = QtCore.Signal(str)
    UpdateClinical = QtCore.Signal(dict)
    OpenPopup = QtCore.Signal(PayloadHandler, list)
    #settingToggle = QtCore.Signal(str)

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(['TARGET'],*args, **kwargs)
        #super(TabModes, self).__init__(NativeUI, *args, **kwargs)
        self.NativeUI = NativeUI
        self.limSpinDict = {}
        self.setSpinDict = {}
        self.buttonDict = {}
        self.radioDict = {}
        self.commandList = []
        self.manuallyUpdated = False
        self.valueDict = {}

        with open("NativeUI/configs/clinical_config.json") as json_file:
            clinicalDict = json.load(json_file)

        self.singleThresholds = clinicalDict["SingleThresholds"]
        self.absoluteLimits = clinicalDict["AbsoluteLimits"]
        self.limit_to_mode_dict = {}
        self.relevantKeys = []
        for setting in clinicalDict['settings']:
            if len(setting) == 3:
                limit_code = setting[0][2]
                mode_code = setting[1][2]
                mode_minimum = setting[1][5]
                mode_maximum = setting[1][6]
                limit_minimum = setting[0][5]
                limit_maximum = setting[-1][6]
                self.limit_to_mode_dict[limit_code] = [mode_code, mode_minimum, mode_maximum, limit_minimum, limit_maximum]

                self.relevantKeys.append(setting[1][2])


    def add_widget(self, widget, key: str):
        if isinstance(widget, labelledSpin):
            if 'min' in key or 'max' in key:
                self.limSpinDict[key] = widget
            elif 'set' in key:
                self.setSpinDict[key] = widget
            self.valueDict[key] = widget.get_value()
        if isinstance(widget, OkButtonWidget) or isinstance(widget, CancelButtonWidget) or isinstance(widget, OkSendButtonWidget):
            self.buttonDict[key] = widget
        if isinstance(widget, QtWidgets.QRadioButton):
            self.radioDict[key] = widget


    def active_payload(self, *args) -> int:
        target_data = self.get_db()
        outdict = {}


        for key in self.relevantKeys:
            try:
                outdict[key] = target_data[key]
            except KeyError:
                logging.debug("Invalid key %s in measurement database", key)

        self.UpdateClinical.emit(outdict)
        return 0


    def handle_okbutton_click(self):
        message, command = [], []
        for key, widget in dict(self.limSpinDict, **self.setSpinDict).items():
            if widget.manuallyUpdated:
                setVal = widget.get_value()
                if ('set' not in key):
                    setkey = key.replace('min', 'set').replace('max','set')
                    if (widget.label in self.absoluteLimits):
                        multiplier = 1
                    else:
                        multiplier = self.setSpinDict[setkey].get_value()/100

                    setVal = self.setSpinDict[setkey].get_value() + setVal*multiplier
                setVal = round(setVal,widget.decPlaces)
                message.append("set" + key + " to " + str(setVal))

                command.append(
                    [
                        widget.cmd_type,
                        widget.cmd_code,
                        setVal,
                    ]
                )
        # create a signal emitting message, command, handler identifier - in nativeui connect to a popup widget
        # command sending should occur in handler
        self.commandList = command
        self.OpenPopup.emit(self,message)

    def sendCommands(self):
        if self.commandList == []:
            a=1
        else:
            for command in self.commandList:
                self.NativeUI.q_send_cmd(*command)
            self.commandSent()
        return 0

    def handle_cancelbutton_click(self):
        for key, widget in dict(self.limSpinDict, **self.setSpinDict).items():
            widget.manuallyUpdated = False
            widget.set_value(self.valueDict[key])


        self.active_payload()
        self.refresh_button_colour()

    def handle_cancel_pressed(self,buttonMode):
        if buttonMode == self.NativeUI.currentMode:
            print('modes match ')
            self.commandSent()
        else:
            print('do nothing in clinical')

    def commandSent(self):
        self.commandList = []
        for key, widget in dict(self.limSpinDict, **self.setSpinDict).items():
            widget.manuallyUpdated = False
            self.valueDict[key] = widget.get_value()
            widget.set_value(widget.get_value())

        self.active_payload()
        self.refresh_button_colour()

    def handle_manual_change(self, changed_spin_key):

        self.active_payload()
        self.refresh_button_colour()



    def setpoint_changed(self, widget):
        """Respond to change in operational settings to modify alarm limits. If setpoint is close to an absolute maximum
         or minimum the alarm limits should respond.
         Takes the modified widget, uses its tag to identify corresponding alarm limits"""
        cmd_code = widget.tag
        for key, infoList in self.limit_to_mode_dict.items():
            if cmd_code in infoList[0]: # find entry in dictionary corresponding to the modified widget
                setValue = widget.get_value()
                minValue = float(infoList[1])
                maxValue = float(infoList[2])
                limMin = float(infoList[3])
                limMax = float(infoList[4])
                attrName = 'clinical_spin_' + key
                minLimitWidget = self.limSpinDict[attrName + '_min']
                maxLimitWidget = self.limSpinDict[attrName + '_max']
                if widget is not self.setSpinDict[attrName + '_set']: # handle incoming value from 'set point' spin boxes elsewhere in ui
                    if isinstance(widget, labelledSpin):
                        if self.NativeUI.currentMode.replace('/','_').replace('-','_') in widget.cmd_type:
                            self.setSpinDict[attrName + '_set'].simpleSpin.set_value(
                                widget.get_value())
                    elif isinstance(widget, SpinButton):
                        self.setSpinDict[attrName + '_set'].simpleSpin.set_value(widget.get_value())

                if widget.label in self.absoluteLimits:
                    denominator = 100 # just get difference if looking for absolute limit
                else:
                    denominator = setValue # get percentage if looking for percentage
                pct_to_max = 100*(maxValue - setValue)/denominator
                pct_to_min = 100*(minValue -setValue)/denominator
                # print('maximum is ' + str(limMax))
                # print('pct to max is ' + str(pct_to_max))
                # print('maxval is ' + str(maxValue))
                # print('setVal is ' + str(setValue))
                # print('denom is ' + str(denominator))

                if round(pct_to_max,4) <= round(limMax,4): # round to avoid errors with floating point numbers
                    maxLimitWidget.set_maximum(pct_to_max)
                elif round(pct_to_min,4) >= round(limMin,4):
                    minLimitWidget.set_minimum(pct_to_min)
                else:
                    maxLimitWidget.set_maximum(10)
                    minLimitWidget.set_minimum(-10)

        self.refresh_button_colour()

    def refresh_button_colour(self):
        '''Refresh button colour based on whether there are any manually updated spin widgets or not'''
        self.manuallyUpdated = False
        for spin in dict(self.limSpinDict, **self.setSpinDict).values():
            self.manuallyUpdated = self.manuallyUpdated or spin.manuallyUpdated
        for button in self.buttonDict:
            if isinstance(self.buttonDict[button], OkSendButtonWidget):
                self.buttonDict[button].setColour(str(int(True)))
            else:
                self.buttonDict[button].setColour(str(int(self.manuallyUpdated)))


    def get_mode(self, key: str):
        for mode in self.modeList:
            if mode in key:
                return mode
