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


class modeswitchPopup(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(modeswitchPopup, self).__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        self.settingsList = [
            "Respiratory Rate",
            "Inhale Time",
            "IE Ratio",
            "Inhale Trigger Sensitivity",
            "Exhale Trigger Sensitivity",
            "Inhale Pressure",
            "Inhale Volume",
            "Percentage O2",
        ]  # self.NativeUI.modes_view.modeTab.settingsList
        modeList = self.NativeUI.modeList

        vradioLayout = QtWidgets.QVBoxLayout()
        groupBox = QtWidgets.QGroupBox()
        self.radioButtons = {}
        for mode in modeList:
            button = QtWidgets.QRadioButton(mode)
            goToButton = QtWidgets.QPushButton(mode)
            goToButton.pressed.connect(lambda j=mode: self.goToPressed(j))
            hlayout = QtWidgets.QHBoxLayout()
            hlayout.addWidget(button)
            hlayout.addWidget(goToButton)
            self.radioButtons[mode] = button
            vradioLayout.addLayout(hlayout)
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
            namelabel = QtWidgets.QLabel(settings)
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
        self.radioButtons[self.NativeUI.currentMode].click()

    def goToPressed(self, mode):
        # Switch to the modes page
        self.NativeUI.widgets.page_stack.setCurrentWidget(
            self.NativeUI.widgets.modes_page
        )
        self.NativeUI.widgets.page_buttons.set_pressed(["modes_button"])

        # Switch to the specific mode tab
        for button in self.NativeUI.widgets.mode_settings_tab.buttonWidgets:
            print(button.text())
            print(mode)
            if mode in button.text():
                print("match!")
                print(mode)
                button.click()

        # Close the popup
        self.close()

    def update_settings_data(self, button):
        self.spinDict = self.NativeUI.widgets.mode_settings_tab.spinDict
        self.mode = button.text().replace("/", "_").replace("-", "_")

        data = self.NativeUI.get_db("targets")
        for settings, currentLabel, newLabel in zip(
            self.settingsList, self.currentLabelList, self.newLabelList
        ):
            currentVal = self.spinDict[
                self.NativeUI.currentMode.replace("/", "_").replace("-", "_")
            ][settings].simpleSpin.value()
            currentLabel.setText(str(round(currentVal, 4)))
            setVal = self.spinDict[self.mode][settings].simpleSpin.value()
            newLabel.setText(str(round(setVal, 4)))

    def ok_button_pressed(self):
        self.NativeUI.q_send_cmd("SET_MODE", self.mode)
        self.NativeUI.currentMode = self.mode
        self.close()

    def cancel_button_pressed(self):
        self.close()
