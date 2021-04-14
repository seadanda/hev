from global_widgets.global_spinbox import labelledSpin
from widget_library.ok_cancel_buttons_widget import OkButtonWidget, CancelButtonWidget, OkSendButtonWidget
from global_widgets.global_send_popup import SetConfirmPopup

from PySide2 import QtWidgets, QtGui, QtCore

class ModeHandler(QtWidgets.QWidget):  # chose QWidget over QDialog family because easier to modify

    modeSwitched = QtCore.Signal(str)

    def __init__(self, NativeUI, confirmPopup, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #super(TabModes, self).__init__(NativeUI, *args, **kwargs)
        self.NativeUI = NativeUI
        self.spinDict = {}
        self.buttonDict = {}
        self.radioDict = {}
        self.manuallyUpdatedBoolDict = { mode: False for mode in self.NativeUI.modeList }
        self.popup = confirmPopup
       # for mode in self.NativeUI.modeList:
        #    self.popup.okButton.pressed.connect(lambda i=mode: self.commandSent(i))

    def add_widget(self, widget, key: str):
        if isinstance(widget, labelledSpin):
            self.spinDict[key] = widget
        if isinstance(widget, OkButtonWidget) or isinstance(widget, CancelButtonWidget) or isinstance(widget, OkSendButtonWidget):
            self.buttonDict[key] = widget
        if isinstance(widget, QtWidgets.QRadioButton):
            self.radioDict[key] = widget

    def update_values(self):
        db = self.NativeUI.get_db('targets')
        if db == {}:
            return 0  # do nothing
        else:
            self.manuallyUpdatedBoolDict = { mode: False for mode in self.NativeUI.modeList }
            for spin in self.spinDict:
                self.spinDict[spin].update_value(db)

    def handle_okbutton_click(self, key):
        print(key + ' pressed')
        mode = self.get_mode(key)
        message, command = [], []
        for widget in self.spinDict:
            if mode in widget:
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
        self.popup.okButton.pressed.connect(lambda i=mode: self.commandSent(i))
        #self.popup.okButton.pressed.connect(self.modeSwitched.emit())
        if 'send' in key:
            self.popup.okButton.click()
            self.modeSwitched.emit(mode)
        else:
            print('show popup')
            self.popup.show()

    def commandSent(self, mode):
        self.popup.clearPopup()
        print('toggle from command send')
        #self.toggleButtons(mode,0)
        for widget in self.spinDict:
            if mode in widget:
                self.spinDict[widget].manuallyUpdated = False
        self.refresh_button_colour()

    def handle_manual_change(self, changed_spin_key):
        self.refresh_button_colour()

    def handle_radio_toggled(self, radioButtonState, radioKey):
        mode = self.get_mode(radioKey)
        radioButton = self.radioDict[radioKey]
        spinKey= radioKey.replace('radio', 'spin')
        spinBox = self.spinDict[spinKey]
        radioButtonState = radioButton.isChecked()
        spinBox.simpleSpin.setEnabled(radioButtonState)
        spinBox.simpleSpin.setProperty("bgColour", str(int(not radioButtonState)))
        spinBox.simpleSpin.setProperty(
            "textColour", str(int(not radioButtonState))
        )

        spinBox.simpleSpin.style().unpolish(spinBox.simpleSpin)
        spinBox.simpleSpin.style().polish(spinBox.simpleSpin)

        if mode == self.NativeUI.currentMode:
            self.NativeUI.widgets.spin_buttons.setStackWidget(spinBox.label)

    def refresh_button_colour(self):
        self.manuallyUpdatedBoolDict = { mode: False for mode in self.NativeUI.modeList }
        for spin in self.spinDict:
            self.manuallyUpdatedBoolDict[self.get_mode(spin)] = self.manuallyUpdatedBoolDict[self.get_mode(spin)] or self.spinDict[spin].manuallyUpdated
        for button in self.buttonDict:
            mode = str(self.get_mode(button))
            if isinstance(self.buttonDict[button], OkSendButtonWidget) and (mode != self.NativeUI.currentMode):
                self.buttonDict[button].setColour(str(int(True)))
            else:
                self.buttonDict[button].setColour(str(int(self.manuallyUpdatedBoolDict[mode])))
            print(self.manuallyUpdatedBoolDict)


    def get_mode(self, key: str):
        for mode in self.NativeUI.modeList:
            if mode in key:
                return mode
