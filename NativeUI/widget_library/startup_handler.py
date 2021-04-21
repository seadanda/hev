from global_widgets.global_spinbox import labelledSpin
from widget_library.startup_calibration_widget import calibrationWidget
from widget_library.ok_cancel_buttons_widget import OkButtonWidget, CancelButtonWidget, OkSendButtonWidget
from global_widgets.global_send_popup import SetConfirmPopup
from datetime import datetime
import json
from PySide2 import QtWidgets, QtGui, QtCore

class StartupHandler(QtWidgets.QWidget):  # chose QWidget over QDialog family because easier to modify

    modeSwitched = QtCore.Signal(str)

    def __init__(self, NativeUI, confirmPopup, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buttonDict = {}
        self.spinDict = {}
        self.calibDict = {}
        self.popup = confirmPopup
        #super(TabModes, self).__init__(NativeUI, *args, **kwargs)


    def add_widget(self, widget, key: str):
        if isinstance(widget, labelledSpin):
            self.spinDict[key] = widget
            widget.cmd_type = widget.cmd_type.replace('startup', 'CURRENT')
        if isinstance(widget, calibrationWidget):
            self.calibDict[key] = widget
        if isinstance(widget, OkButtonWidget) or isinstance(widget, CancelButtonWidget) or isinstance(widget,OkSendButtonWidget):
            self.buttonDict[key] = widget

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
        self.popup.clearPopup()
        self.popup.populatePopup(message, command)
        #self.popup.okButton.pressed.connect(lambda i=mode: self.commandSent(i))
        #self.popup.okButton.pressed.connect(self.modeSwitched.emit())
        self.popup.okButton.click()



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
        self.buttonDict['nextButton'].style().polish(self.buttonDict['nextButton'])

    def handle_backbutton(self, stack):
        currentIndex = stack.currentIndex()
        nextIndex = currentIndex - 1
        #totalLength = stack.count()
        stack.setCurrentIndex(nextIndex)
        if nextIndex == 0:
            a = 1 # send
            self.buttonDict['backButton'].setColour(0)
        else:

            self.buttonDict['backButton'].setColour(1)
        self.buttonDict['nextButton'].setColour(1)
        self.buttonDict['backButton'].style().polish(self.buttonDict['backButton'])