#!/usr/bin/env python3

"""
tab_modeswitch_button.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

from PySide2 import QtCore, QtGui, QtWidgets
from widget_library.ok_cancel_buttons_widget import OkButtonWidget, CancelButtonWidget
import json

# from global_widgets.global_ok_cancel_buttons import okButton, cancelButton


class TabModeswitchButton(QtWidgets.QWidget):
    modeSwitched = QtCore.Signal(str)

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """Button opens popup for user to switch modes.
        The label is updated to show the current operating mode"""

        self.NativeUI = NativeUI

        layout = QtWidgets.QHBoxLayout(self)
        self.label = QtWidgets.QLabel("Mode: ")
        self.label.setFont(NativeUI.text_font)
        self.label.setStyleSheet(
            "background-color:" + NativeUI.colors["page_background"].name() + ";"
            "border: none;"
            "color:" + NativeUI.colors["page_foreground"].name() + ";"
        )

        self.switchButton = QtWidgets.QPushButton(self.NativeUI.modeList[0])
        layout.addWidget(self.label)
        layout.addWidget(self.switchButton)
        self.setLayout(layout)

        self.mode_popup = False
        self.switchButton.pressed.connect(self.switch_button_pressed)

        # self.mode_popup.okbutton.pressed.connect(self.changeText)

    def update_mode(self, mode):
        """Update button text to show operating mode"""
        self.switchButton.setText(mode)
        return 0

    def switch_button_pressed(self):
        """Button pressed, open popup, ensure correct mode is selected in popup."""
        if self.mode_popup == False:
            self.mode_popup = modeswitchPopup(self.NativeUI)
            self.mode_popup.okbutton.pressed.connect(self.changeText)
        else:
            self.mode_popup.radioButtons[self.NativeUI.currentMode].click()
        self.mode_popup.show()
        return 0

    def changeText(self):
        self.switchButton.setText(self.mode_popup.mode)
        self.modeSwitched.emit(self.mode_popup.mode)

    def set_size(self, x: int, y: int, spacing=10) -> int:
        self.setFixedSize(x, y)
        return 0


class modeswitchPopup(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        """A popup used to switch modes. Allows the user to compare the values they are setting with current setting
        and to navigate to mode setting page to edit those values."""
        super(modeswitchPopup, self).__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        with open("NativeUI/configs/mode_config.json") as json_file:
            modeDict = json.load(json_file)

        self.settingsList = modeDict['settings']
        modeList = self.NativeUI.modeList

        vradioLayout = QtWidgets.QVBoxLayout()
        groupBox = QtWidgets.QGroupBox()
        self.radioButtons = {}
        for mode in modeList:
            button = QtWidgets.QRadioButton(mode)
            goto_button = QtWidgets.QPushButton(mode)
            goto_button.pressed.connect(lambda j=mode: self.goto_pressed(j))
            hlayout = QtWidgets.QHBoxLayout()
            hlayout.addWidget(button)
            hlayout.addWidget(goto_button)
            self.radioButtons[mode] = button
            vradioLayout.addLayout(hlayout)
        groupBox.setLayout(vradioLayout)

        ## Values display

        valuesLayout = QtWidgets.QHBoxLayout()
        # Title labels:
        initLabel = QtWidgets.QLabel(" ")
        initVal = QtWidgets.QLabel("Current")
        initVal.setAlignment(QtCore.Qt.AlignCenter)
        newVal = QtWidgets.QLabel("New")
        newVal.setAlignment(QtCore.Qt.AlignCenter)
        newVal.setStyleSheet("color: red")

        # Populate actual values in loop
        self.labelList, self.currentLabelList, self.newLabelList = [], [], []
        vlayout1, vlayout2, vlayout3 = (
            QtWidgets.QVBoxLayout(),
            QtWidgets.QVBoxLayout(),
            QtWidgets.QVBoxLayout(),
        )
        vlayout1.addWidget(initLabel)
        vlayout2.addWidget(initVal)
        vlayout3.addWidget(newVal)
        for settings in self.settingsList:
            namelabel = QtWidgets.QLabel(settings[0])
            namelabel.setAlignment(QtCore.Qt.AlignRight)
            vlayout1.addWidget(namelabel)

            currentLabel = QtWidgets.QLabel("0")
            currentLabel.setAlignment(QtCore.Qt.AlignCenter)
            self.currentLabelList.append(currentLabel)
            vlayout2.addWidget(currentLabel)

            newLabel = QtWidgets.QLabel("0")
            newLabel.setAlignment(QtCore.Qt.AlignCenter)
            newLabel.setStyleSheet("color: red")
            self.newLabelList.append(newLabel)
            vlayout3.addWidget(newLabel)

        valuesLayout.addLayout(vlayout1)
        valuesLayout.addLayout(vlayout2)
        valuesLayout.addLayout(vlayout3)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(groupBox)
        hlayout.addLayout(valuesLayout)

        ## Ok Cancel Buttons
        hbuttonlayout = QtWidgets.QHBoxLayout()
        self.okbutton = OkButtonWidget(NativeUI)
        self.okbutton.setEnabled(True)
        self.okbutton.pressed.connect(self.ok_button_pressed)
        self.cancelbutton = CancelButtonWidget(NativeUI)
        self.cancelbutton.setEnabled(True)
        self.cancelbutton.pressed.connect(self.cancel_button_pressed)
        hbuttonlayout.addWidget(self.okbutton)
        hbuttonlayout.addWidget(self.cancelbutton)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addLayout(hbuttonlayout)

        for mode in modeList:
            button = self.radioButtons[mode]
            button.pressed.connect(lambda i=button: self.update_settings_data(i))
            if mode == self.NativeUI.currentMode:
                button.click()

        ## Final, general, initiation steps

        self.setLayout(vlayout)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        # self.radioButtons[self.NativeUI.currentMode].click()  # 1st button clicked by default
        # self.radioButtons[0].click()  # 1st button clicked by default
        # self.update_settings_data(radioButtons[0])

        self.setStyleSheet(
            "background-color:" + NativeUI.colors["page_background"].name() + ";"
            "color:" + NativeUI.colors["page_foreground"].name() + ";"
            "font: 16pt bold;"
        )
        # self.radioButtons[self.NativeUI.currentMode].click()

    def goto_pressed(self, mode):
        """On button press, show mode page in UI"""
        self.NativeUI.widgets.page_stack.setCurrentWidget(
            self.NativeUI.widgets.modes_page
        )
        self.NativeUI.widgets.page_buttons.set_pressed(["modes_button"])

        # Switch to the specific mode tab
        for button in self.NativeUI.widgets.modes_page.widget_list[
            0
        ].button_list:  # mode_settings_tab.buttonWidgets:
            if mode in button.text():
                self.NativeUI.widgets.modes_page.widget_list[0].setTab(button)

        # Close the popup
        self.close()

    def update_settings_data(self, button):
        """Respond to button press and update labels in modeswitch popup"""
        self.spinDict = self.NativeUI.mode_handler.spinDict
        self.mode = button.text()
        for settings, currentLabel, newLabel in zip(
            self.settingsList, self.currentLabelList, self.newLabelList
        ):
            currentVal = self.spinDict[
                "spin_" + self.NativeUI.currentMode + "_" + settings[2]
            ].get_value()
            currentLabel.setText(str(round(currentVal, 4)))
            setVal = self.spinDict["spin_" + self.mode + "_" + settings[2]].get_value()
            newLabel.setText(str(round(setVal, 4)))

    def ok_button_pressed(self):
        """Switch to selected mode"""
        if self.NativeUI.currentMode == self.mode:
            a = 1  # do nothing
        else:
            self.NativeUI.q_send_cmd(
                "SET_MODE", self.mode.replace("/", "_").replace("-", "_")
            )
            self.NativeUI.currentMode = self.mode
            self.close()
        return 0

    def cancel_button_pressed(self):
        """Close popup without doing anything"""
        self.close()
        return 0

    def update_mode(self, mode):
        """When mode is changed the popup radio buttons should show the new mode"""
        self.mode_popup.radioButtons[mode].click()
