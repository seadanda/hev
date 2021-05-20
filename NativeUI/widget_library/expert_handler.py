from global_widgets.global_spinbox import labelledSpin
from widget_library.ok_cancel_buttons_widget import OkButtonWidget, CancelButtonWidget, OkSendButtonWidget

from PySide2 import QtWidgets, QtGui, QtCore
from handler_library.handler import PayloadHandler
import logging
import json

class ExpertHandler(PayloadHandler):  # chose QWidget over QDialog family because easier to modify

    UpdateExpert = QtCore.Signal(dict)
    OpenPopup = QtCore.Signal(PayloadHandler,list)

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(['READBACK'],*args, **kwargs)
        self.NativeUI = NativeUI
        self.spinDict = {}
        self.buttonDict = {}
        self.manuallyUpdated = False
        self.commandList = []

        with open("NativeUI/configs/expert_config.json") as json_file:
            controlDict = json.load(json_file)

        self.relevantKeys = [list[2] for key in controlDict for list in controlDict[key]]

    def add_widget(self, widget, key: str):
        if isinstance(widget, labelledSpin):
            self.spinDict[key] = widget
        if isinstance(widget, OkButtonWidget) or isinstance(widget, CancelButtonWidget) or isinstance(widget,OkSendButtonWidget):
            self.buttonDict[key] = widget


    def active_payload(self, *args) -> int:
        readback_data = self.get_db()
        outdict = {}
        for key in self.relevantKeys:
            try:
                outdict[key] = readback_data[key]
            except KeyError:
                logging.debug("Invalid key %s in measurement database", key)
        self.UpdateExpert.emit(outdict)
        return 0

    def handle_okbutton_click(self, key):
        message, command = [], []
        for widget in self.spinDict:
            if self.spinDict[widget].manuallyUpdated:
                setVal = self.spinDict[widget].get_value()
                setVal = round(setVal, widget.decPlaces)
                message.append("set" + widget + " to " + str(setVal))
                command.append(
                    [
                        self.spinDict[widget].cmd_type,
                        self.spinDict[widget].cmd_code,
                        setVal,
                    ]
                )
        self.commandList = command
        if 'send' in key:
            self.sendCommands()
        else:
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
        self.refresh_button_colour()


    def handle_manual_change(self, changed_spin_key):
        self.refresh_button_colour()

    def refresh_button_colour(self):
        self.manuallyUpdated = False
        for spin in self.spinDict:
            self.manuallyUpdated = self.manuallyUpdated or self.spinDict[spin].manuallyUpdated
        for button in self.buttonDict:
            self.buttonDict[button].setColour(str(int(self.manuallyUpdated)))
