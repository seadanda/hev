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

# from global_widgets.global_ok_cancel_buttons import okButton, cancelButton


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
        self.settingsList = self.NativeUI.widgets.mode_settings_tab.settingsList
        modeList = self.NativeUI.modeList
        self.spinDict = self.NativeUI.widgets.mode_settings_tab.spinDict

        vradioLayout = QtWidgets.QVBoxLayout()
        groupBox = QtWidgets.QGroupBox()
        self.radioButtons = {}
        for mode in modeList:
            button = QtWidgets.QRadioButton(mode)
            self.radioButtons[mode] = button
            vradioLayout.addWidget(button)
            button.pressed.connect(lambda i=button: self.update_settings_data(i))
        groupBox.setLayout(vradioLayout)

        ## Values display

        valuesLayout = QtWidgets.QHBoxLayout()

        initLabel = QtWidgets.QLabel(" ")  # titles
        initVal = QtWidgets.QLabel("Current")
        initVal.setAlignment(QtCore.Qt.AlignCenter)
        newVal = QtWidgets.QLabel("New")
        newVal.setAlignment(QtCore.Qt.AlignCenter)
        newVal.setStyleSheet("color: red")

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
        self.okbutton.pressed.connect(self.ok_button_pressed)
        self.cancelbutton = CancelButtonWidget(NativeUI)
        self.cancelbutton.pressed.connect(self.cancel_button_pressed)
        hbuttonlayout.addWidget(self.okbutton)
        hbuttonlayout.addWidget(self.cancelbutton)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addLayout(hbuttonlayout)

        ## Final, general, initiation steps

        self.setLayout(vlayout)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        # self.radioButtons[0].click()  # 1st button clicked by default
        # self.update_settings_data(radioButtons[0])

        self.setStyleSheet(
            "background-color:" + NativeUI.colors["page_background"].name() + ";"
            "color:" + NativeUI.colors["page_foreground"].name() + ";"
            "font: 16pt bold;"
        )

        self.radioButtons[self.NativeUI.currentMode].click()
        # self.update_settings_data(self.radioButtons[0]) # should update according to the mode we're in

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
