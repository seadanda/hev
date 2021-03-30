#!/usr/bin/env python3

"""
template_set_values.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

from PySide2 import QtWidgets, QtGui, QtCore
from global_widgets.global_spinbox import labelledSpin
from global_widgets.global_send_popup import SetConfirmPopup
from global_widgets.global_select_button import selectorButton
from global_widgets.global_ok_cancel_buttons import okButton, okSendButton, cancelButton
from global_widgets.global_lineEdit import labelledLineEdit


class TemplateSetValues(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(TemplateSetValues, self).__init__(*args, **kwargs)
        self.layoutList = []
        self.spinDict = {}
        self.NativeUI = NativeUI
        self.packet = "target"

        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)  # just faster than 60Hz
        self.timer.timeout.connect(self.update_settings_data)
        self.timer.start()

    def setPacketType(self, packetName):
        self.packet = packetName

    def finaliseLayout(self):
        vlayout = QtWidgets.QVBoxLayout()
        for layout in self.layoutList:
            vlayout.addLayout(layout)
        self.setLayout(vlayout)

    def addSpinSingleCol(self, settingsList):
        vOptionLayout = QtWidgets.QVBoxLayout()
        for info in settingsList:
            self.spinDict[info[0]] = labelledSpin(self.NativeUI, info)
            vOptionLayout.addWidget(self.spinDict[info[0]])
        self.layoutList.append(vOptionLayout)

    def addSpinDblCol(self, settingsList):
        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(0)
        vlayout = QtWidgets.QVBoxLayout()
        vlayout2 = QtWidgets.QVBoxLayout()
        i = 0
        for info in settingsList:

            if "_Low" in info[0]:
                self.spinDict[info[0]] = labelledSpin(
                    self.NativeUI, [info[0], "", info[2]]
                )
                self.spinDict[info[0] + "_2"] = labelledSpin(
                    self.NativeUI, ["", info[1], info[2]]
                )
                # hlayout = QtWidgets.QHBoxLayout()
                # hlayout.setSpacing(0)
                # hlayout.addWidget(self.spinDict[info[0]])
                # hlayout.addWidget(self.spinDict[info[0]+ '_2'])
                # if (i%2) == 0:
                #     vlayout.addLayout(hlayout)
                # else:
                #     vlayout2.addLayout(hlayout)
                grid.addWidget(self.spinDict[info[0]], int(i / 2), 2 * (i % 2), 1, 1)
                grid.addWidget(
                    self.spinDict[info[0] + "_2"], int(i / 2), 2 * (i % 2) + 1, 1, 1
                )
            else:
                self.spinDict[info[0]] = labelledSpin(self.NativeUI, info)
                # if (i%2) == 0:
                #     vlayout.addWidget(self.spinDict[info[0]])
                # else:
                #     vlayout2.addWidget(self.spinDict[info[0]])
                grid.addWidget(self.spinDict[info[0]], int(i / 2), 2 * (i % 2), 1, 2)
            i = i + 1
        # hlayoutMeta = QtWidgets.QHBoxLayout()
        # hlayoutMeta.addLayout(vlayout)
        # hlayoutMeta.addLayout(vlayout2)
        self.layoutList.append(grid)

    def addExpertControls(self, controlDict):
        vlayout = QtWidgets.QVBoxLayout()
        i = 0
        for section in controlDict.keys():

            self.titleLabel = QtWidgets.QLabel(section)
            self.titleLabel.setStyleSheet(
                "background-color:" + self.NativeUI.colors["background"].name() + ";"
                "color:" + self.NativeUI.colors["foreground"].name() + ";"
                "font-size: " + self.NativeUI.text_size + ";"
            )
            self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
            vlayout.addWidget(self.titleLabel)

            grid = QtWidgets.QGridLayout()
            grid.setMargin(0)
            grid.setSpacing(0)
            widg = QtWidgets.QFrame()
            widg.setStyleSheet(
                "QFrame{border: 2px solid "
                + self.NativeUI.colors["foreground"].name()
                + ";} QLabel{border:none} "
            )
            j = -1
            for boxInfo in controlDict[section]:
                j = j + 1

                self.spinDict[boxInfo[0]] = labelledSpin(self.NativeUI, boxInfo)

                grid.addWidget(
                    self.spinDict[boxInfo[0]], i + 1 + int(j / 3), 2 * (j % 3), 1, 2
                )

            widg.setLayout(grid)

            vlayout.addWidget(widg)

            i = i + 1 + int(j / 3) + 1
        self.layoutList.append(vlayout)

    def addPersonalCol(self, settingsList, textBoxes):
        vOptionLayout = QtWidgets.QVBoxLayout()
        for info in settingsList:
            if info[0] in textBoxes:
                self.spinDict[info[0]] = labelledLineEdit(self.NativeUI, info)
            else:
                self.spinDict[info[0]] = labelledSpin(self.NativeUI, info)
            vOptionLayout.addWidget(self.spinDict[info[0]])
        self.layoutList.append(vOptionLayout)

    def addButtons(self):
        hlayout = QtWidgets.QHBoxLayout()
        self.okButton = okButton(self.NativeUI)
        self.okButton.pressed.connect(self.okButtonPressed)
        hlayout.addWidget(self.okButton)

        self.cancelButton = cancelButton(self.NativeUI)
        self.cancelButton.pressed.connect(self.cancelButtonPressed)
        hlayout.addWidget(self.cancelButton)
        self.buttonsList = [self.okButton, self.cancelButton]
        self.layoutList.append(hlayout)

        for spin in self.spinDict:
            self.spinDict[spin].simpleSpin.manualChanged.connect(self.colourButtons)

    def addModeButtons(self):
        hlayout = QtWidgets.QHBoxLayout()
        self.okButton = okButton(self.NativeUI)
        self.okButton.pressed.connect(self.okButtonPressed)
        hlayout.addWidget(self.okButton)

        self.okSendButton = okSendButton(self.NativeUI)
        self.okSendButton.pressed.connect(self.okSendButtonPressed)
        hlayout.addWidget(self.okSendButton)

        self.cancelButton = cancelButton(self.NativeUI)
        self.cancelButton.pressed.connect(self.cancelButtonPressed)
        hlayout.addWidget(self.cancelButton)
        self.buttonsList = [self.okButton, self.okSendButton, self.cancelButton]
        self.layoutList.append(hlayout)

        for spin in self.spinDict:
            self.spinDict[spin].simpleSpin.manualChanged.connect(self.colourButtons)

    def colourButtons(self):
        for button in self.buttonsList:
            button.setColour(1)

    def update_settings_data(self):
        for widget in self.spinDict:
            if self.packet == "target":
                self.spinDict[
                    widget
                ].update_targets_value()  # pass database                elif self.packet == "readback":
            elif self.packet == "readback":
                self.spinDict[widget].update_readback_value()
            elif self.packet == "personal":
                self.spinDict[widget].update_personal_value()

    def okButtonPressed(self):
        message, command = [], []
        for widget in self.spinDict:
            if self.spinDict[widget].manuallyUpdated:
                setVal = self.spinDict[widget].simpleSpin.value()
                message.append("set" + widget + " to " + str(setVal))
                command.append(
                    [
                        self.spinDict[widget].cmd_type,
                        self.spinDict[widget].cmd_code,
                        setVal,
                    ]
                )
        self.popup = SetConfirmPopup(self, self.NativeUI, message, command)
        self.popup.okButton.pressed.connect(self.commandSent)
        self.popup.show()

    def okSendButtonPressed(self):
        message, command = [], []
        for widget in self.spinDict:
            if self.spinDict[widget].manuallyUpdated:
                setVal = self.spinDict[widget].simpleSpin.value()
                message.append("set" + widget + " to " + str(setVal))
                command.append(
                    [
                        self.spinDict[widget].cmd_type,
                        self.spinDict[widget].cmd_code,
                        setVal,
                    ]
                )
        self.popUp = SetConfirmPopup(self, self.NativeUI, message, command)
        self.popUp.ok_button_pressed()
        self.NativeUI.q_send_cmd("SET_MODE", self.mode)
        self.NativeUI.currentMode = self.mode
        self.NativeUI.topBar.tab_modeswitch.switchButton.setText(self.mode)
        self.NativeUI.topBar.tab_modeswitch.mode_popup.radioButtons[self.mode].click()
        self.popUp.setParent(None)
        self.commandSent()

    def commandSent(self):
        for button in self.buttonsList:
            button.setColour(0)
        for widget in self.spinDict:
            self.spinDict[widget].manuallyUpdated = False

    def cancelButtonPressed(self):
        for button in self.buttonsList:
            button.setColour(0)
        for widget in self.spinDict:
            if self.spinDict[widget].manuallyUpdated:
                self.spinDict[widget].manuallyUpdated = False
