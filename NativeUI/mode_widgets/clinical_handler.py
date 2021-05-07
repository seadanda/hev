from global_widgets.global_spinbox import labelledSpin
from widget_library.ok_cancel_buttons_widget import OkButtonWidget, CancelButtonWidget, OkSendButtonWidget
#from global_widgets.global_send_popup import SetConfirmPopup
from widget_library.spin_buttons_widget import SpinButton, SpinButtonsWidget

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
        self.spinDict = {}
        self.buttonDict = {}
        self.radioDict = {}
        self.commandList = []
        self.manuallyUpdated = False

        with open("NativeUI/configs/clinical_config.json") as json_file:
            clinicalDict = json.load(json_file)
        #self.relevantKeys = [print(setting) for setting in clinicalDict['settings']]

    def add_widget(self, widget, key: str):
        if isinstance(widget, labelledSpin):
            self.spinDict[key] = widget
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
        print('ok')

        message, command = [], []
        for widget in self.spinDict:
            if self.spinDict[widget].manuallyUpdated:
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

    def sendCommands(self):
        if self.commandList == []:
            a=1
        else:
            for command in self.commandList:
                self.NativeUI.q_send_cmd(*command)
            self.commandSent()
        return 0

    def commandSent(self):
        self.commandList = []
        for widget in self.spinDict:
            self.spinDict[widget].manuallyUpdated = False

        self.active_payload()
        self.refresh_button_colour()

    def handle_manual_change(self, changed_spin_key):
        self.active_payload()
        self.refresh_button_colour()


    def refresh_button_colour(self):
        self.manuallyUpdated = False
        for spin in dict(self.spinDict):
            self.manuallyUpdated = self.manuallyUpdated or self.spinDict[spin].manuallyUpdated
        for button in dict(self.buttonDict):
            if isinstance(self.buttonDict[button], OkSendButtonWidget):
                self.buttonDict[button].setColour(str(int(True)))
            else:
                self.buttonDict[button].setColour(str(int(self.manuallyUpdated)))


    def get_mode(self, key: str):
        for mode in self.modeList:
            if mode in key:
                return mode
