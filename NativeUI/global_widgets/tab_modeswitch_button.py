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
from global_widgets.global_ok_cancel_buttons import okButton, cancelButton


class TabModeswitchButton(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.NativeUI = NativeUI

        layout = QtWidgets.QHBoxLayout(self)
        self.label = QtWidgets.QLabel("Mode: ")
        self.switchButton = QtWidgets.QPushButton(self.NativeUI.modeList[0])
        layout.addWidget(self.label)
        layout.addWidget(self.switchButton)
        self.setLayout(layout)

        self.mode_popup = False
        self.switchButton.pressed.connect(self.switch_button_pressed)

    def switch_button_pressed(self):
        if self.mode_popup == False:
            self.mode_popup = modeswitchPopup(self.NativeUI)
            self.mode_popup.okbutton.pressed.connect(self.changeText)
        else:
            self.mode_popup.radioButtons[self.NativeUI.currentMode].click()
        self.mode_popup.show()

    def changeText(self):
        self.switchButton.setText(self.mode_popup.mode)


class modeswitchPopup(QtWidgets.QDialog):
    def __init__(self, NativeUI, *args, **kwargs):
        super(modeswitchPopup, self).__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        self.settingsList = self.NativeUI.modes_view.modeTab.settingsList
        modeList = self.NativeUI.modeList
        self.spinDict = self.NativeUI.modes_view.modeTab.spinDict

        vradioLayout = QtWidgets.QVBoxLayout()
        groupBox = QtWidgets.QGroupBox()
        self.radioButtons = {}
        for mode in modeList:
            button = QtWidgets.QRadioButton(mode)
            self.radioButtons[mode] = button
            vradioLayout.addWidget(button)
            button.pressed.connect(lambda i=button: self.update_settings_data(i))
        groupBox.setLayout(vradioLayout)

        valuesLayout = QtWidgets.QVBoxLayout()

        initlabel = settingsLabel(" ")  # titles
        initlabel.currentLabel.setText("Current")
        initlabel.settingLabel.setText("New")
        valuesLayout.addWidget(initlabel)

        self.labelList = []
        for settings in self.settingsList:
            label = settingsLabel(settings[0])
            self.labelList.append(label)
            # settingVal = spinDict
            valuesLayout.addWidget(label)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(groupBox)
        hlayout.addLayout(valuesLayout)

        hbuttonlayout = QtWidgets.QHBoxLayout()
        self.okbutton = okButton(NativeUI)
        self.okbutton.pressed.connect(self.ok_button_pressed)
        self.cancelbutton = cancelButton(NativeUI)
        self.cancelbutton.pressed.connect(self.cancel_button_pressed)
        hbuttonlayout.addWidget(self.okbutton)
        hbuttonlayout.addWidget(self.cancelbutton)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addLayout(hbuttonlayout)

        self.setLayout(vlayout)

        self.radioButtons[self.NativeUI.currentMode].click()
        #self.update_settings_data(self.radioButtons[0]) # should update according to the mode we're in

    def update_settings_data(self, button):
        self.mode = button.text()
        data = self.NativeUI.get_db("targets")
        for label, settings in zip(self.labelList, self.settingsList):
            currentVal = data[settings[2]]
            setVal = self.spinDict[self.mode + settings[0]].simpleSpin.value()
            label.update_values(currentVal, setVal)

    def ok_button_pressed(self):
        self.NativeUI.q_send_cmd("SET_MODE", self.mode)
        self.NativeUI.currentMode = self.mode
        # need to decide whetehr this sets individual values or just mode
        # for label,settings in zip(self.labelList,self.settingsList):
        #     currentVal = data[settings[2]]
        #     setVal = self.spinDict[self.mode + settings[0]].simpleSpin.value()
        #     label.update_values(currentVal, setVal)
        self.close()

    def cancel_button_pressed(self):
        self.close()


class settingsLabel(QtWidgets.QWidget):
    def __init__(self, name, *args, **kwargs):
        super(settingsLabel, self).__init__(*args, **kwargs)

        self.nameLabel = QtWidgets.QLabel(name)
        self.currentLabel = QtWidgets.QLabel(str(0))
        self.settingLabel = QtWidgets.QLabel(str(0))
        self.settingLabel.setStyleSheet("color:red")

        hlayout = QtWidgets.QHBoxLayout()
        labels = [self.nameLabel, self.currentLabel, self.settingLabel]
        for label in labels:
            hlayout.addWidget(label)
        self.setLayout(hlayout)

    def update_values(self, currentVal, setVal):
        self.currentLabel.setText(str(currentVal))
        self.settingLabel.setText(str(setVal))
