from global_widgets.global_spinbox import labelledSpin
from widget_library.ok_cancel_buttons_widget import OkButtonWidget, CancelButtonWidget, OkSendButtonWidget
from global_widgets.global_send_popup import SetConfirmPopup

from PySide2 import QtWidgets, QtGui, QtCore

class ExpertHandler(QtWidgets.QWidget):  # chose QWidget over QDialog family because easier to modify

    #modeSwitched = QtCore.Signal(str)

    def __init__(self, NativeUI, confirmPopup, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def update_values(self):
        db = self.NativeUI.get_db('readback')
        if db == {}:
            return 0  # do nothing
        else:
            self.manuallyUpdatedDict = False
            for spin in self.spinDict:
                self.spinDict[spin].update_value(db)

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
