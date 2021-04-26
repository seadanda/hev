from global_widgets.global_spinbox import labelledSpin
from widget_library.ok_cancel_buttons_widget import OkButtonWidget, CancelButtonWidget, OkSendButtonWidget
from global_widgets.global_send_popup import SetConfirmPopup

from PySide2 import QtWidgets, QtGui, QtCore
from handler_library.handler import Handler
import logging


class ExpertHandler(Handler, QtCore.QObject):  # chose QWidget over QDialog family because easier to modify

    UpdateExpert = QtCore.Signal(dict)

    def __init__(self, NativeUI, confirmPopup, *args, **kwargs):
        super().__init__(*args, **kwargs)
        QtCore.QObject.__init__(self)
        self.NativeUI = NativeUI
        self.spinDict = {}
        self.buttonDict = {}
        self.manuallyUpdated = False
        self.popup = confirmPopup
        self.popup.okButton.pressed.connect(lambda: self.commandSent()) # not sure why, but lambda is necessary here


    def add_widget(self, widget, key: str):
        if isinstance(widget, labelledSpin):
            self.spinDict[key] = widget
        if isinstance(widget, OkButtonWidget) or isinstance(widget, CancelButtonWidget) or isinstance(widget,OkSendButtonWidget):
            self.buttonDict[key] = widget


    def active_payload(self) -> int:
        readback_data = self.get_db()
        outdict = {}
        self.UpdateExpert.emit(readback_data)
        return 0
        # for key in [
        #     "respiratory_rate",
        #     "fiO2_percent",
        #     "inhale_trigger_threshold",
        #     "exhale_trigger_threshold",
        #     "volume",
        #     "inspiratory_pressure",
        #     "inhale_time",
        #     "ie_ratio",
        # ]:
        #     try:
        #         outdict[key] = readback_data[key]
        #     except KeyError:
        #         logging.debug("Invalid key %s in measurement database", key)

        # self.UpdateExpert.emit(readback_dict)
        # return 0


    def handle_okbutton_click(self, key):
        message, command = [], []
        for widget in self.spinDict:
            if self.spinDict[widget].manuallyUpdated:
                setVal = self.spinDict[widget].get_value()
                message.append("set" + widget + " to " + str(setVal))
                command.append(
                    [
                        self.spinDict[widget].cmd_type,
                        self.spinDict[widget].cmd_code,
                        setVal,
                    ]
                )
        self.popup.clearPopup()
        self.popup.populatePopup(message, command)
        if 'send' in key:
            self.popup.okButton.click()
        else:
            self.popup.show()

    def commandSent(self):
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
