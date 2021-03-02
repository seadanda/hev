from PySide2 import QtWidgets, QtGui, QtCore
from global_widgets.global_spinbox import labelledSpin
from global_widgets.global_send_popup import SetConfirmPopup
from global_widgets.global_select_button import selectorButton
from global_widgets.global_ok_cancel_buttons import okButton, cancelButton


class TemplateSetValues(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(TemplateSetValues, self).__init__(*args, **kwargs)
        self.liveUpdating = True
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
            self.spinDict[info[0]] = labelledSpin(self, self.NativeUI, info)
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
                    self, self.NativeUI, [info[0], "", info[2]]
                )
                self.spinDict[info[0] + "_2"] = labelledSpin(
                    self, self.NativeUI, ["", info[1], info[2]]
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
                self.spinDict[info[0]] = labelledSpin(self, self.NativeUI, info)
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
        grid = QtWidgets.QGridLayout()
        i = 0
        for section in controlDict.keys():

            self.titleLabel = QtWidgets.QLabel(section)
            self.titleLabel.setStyleSheet(
                "background-color:" + self.NativeUI.colors["background"].name() + ";"
                "color:" + self.NativeUI.colors["foreground"].name() + ";"
                "font: 20pt;"
            )
            self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
            grid.addWidget(self.titleLabel, i, 0, 1, 6)
            j = -1
            for boxInfo in controlDict[section]:
                j = j + 1
                # label, units = boxInfo, controlDict[section][boxInfo]
                self.spinDict[boxInfo[0]] = labelledSpin(self, self.NativeUI, boxInfo)
                # self.spinInfo.append(boxInfo)
                grid.addWidget(
                    self.spinDict[boxInfo[0]], i + 1 + int(j / 3), 2 * (j % 3), 1, 2
                )

            i = i + 1 + int(j / 3) + 1
        self.layoutList.append(grid)

    def addModeStack(self, settingsList):
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setSpacing(0)
        self.pcacButton = selectorButton(self.NativeUI, "PC/AC")
        self.pcacButton.setProperty("selected", "1")
        self.pcacEnable = [1, 0, 1, 1, 0, 1, 0, 1]
        self.pcacVals = [1, 2, 3, 4, 5, 6, 7, 8]

        self.prvcButton = selectorButton(self.NativeUI, "PC/AC-PRVC")
        self.prvcEnable = [1, 1, 0, 1, 0, 1, 1, 1]
        self.prvcVals = [2, 3, 4, 5, 6, 7, 8, 9]

        self.psvButton = selectorButton(self.NativeUI, "PC-PSV")
        self.psvEnable = [1, 1, 0, 1, 0, 1, 0, 1]
        self.psvVals = [3, 4, 5, 6, 7, 8, 9, 1]

        self.cpapButton = selectorButton(self.NativeUI, "CPAP")
        self.cpapEnable = [1, 0, 1, 1, 0, 1, 0, 1]
        self.cpapVals = [4, 5, 6, 7, 8, 9, 1, 2]

        self.buttonWidgets = [
            self.pcacButton,
            self.prvcButton,
            self.psvButton,
            self.cpapButton,
        ]
        enableMetaList = [
            self.pcacEnable,
            self.prvcEnable,
            self.psvEnable,
            self.cpapEnable,
        ]
        self.valsMetaList = [self.pcacVals, self.prvcVals, self.psvVals, self.cpapVals]
        self.modeList = ["PC_AC", "PC_AC_PRVC", "PC_PSV", "CPAP"]
        self.pageList = []
        self.stack = QtWidgets.QStackedWidget()

        for button, enableList, valsList, mode in zip(
            self.buttonWidgets, enableMetaList, self.valsMetaList, self.modeList
        ):
            hlayout.addWidget(button)
            vOptionLayout = QtWidgets.QVBoxLayout()
            for info, enable, vals in zip(settingsList, enableList, valsList):
                info[3] = "SET_TARGET_" + mode
                self.spinDict[mode + info[0]] = labelledSpin(self, self.NativeUI, info)
                vOptionLayout.addWidget(self.spinDict[mode + info[0]])
                self.spinDict[mode + info[0]].simpleSpin.setEnabled(enable)
                if enable == 1:
                    self.spinDict[mode + info[0]].simpleSpin.setProperty(
                        "bgColour", "0"
                    )
                if enable == 0:
                    self.spinDict[mode + info[0]].simpleSpin.setProperty(
                        "bgColour", "1"
                    )
                self.spinDict[mode + info[0]].simpleSpin.style().polish(
                    self.spinDict[mode + info[0]].simpleSpin
                )
                self.spinDict[mode + info[0]].simpleSpin.setValue(vals)
            widget = QtWidgets.QWidget()
            widget.setLayout(vOptionLayout)
            self.pageList.append(widget)
            self.stack.addWidget(widget)

            button.pressed.connect(lambda i=button: self._setColour(i))
        self.stack.setCurrentWidget(self.pageList[0])
        self.layoutList.append(hlayout)
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self.stack)
        self.layoutList.append(vlayout)

    def addButtons(self):
        hlayout = QtWidgets.QHBoxLayout()
        self.okButton = okButton(self.NativeUI)
        self.okButton.pressed.connect(self.okButtonPressed)
        hlayout.addWidget(self.okButton)

        self.cancelButton = cancelButton(self.NativeUI)
        self.cancelButton.pressed.connect(self.cancelButtonPressed)
        hlayout.addWidget(self.cancelButton)
        self.layoutList.append(hlayout)

    def update_settings_data(self):
        if self.liveUpdating:
            for widget in self.spinDict:
                if self.packet == "target":
                    self.spinDict[widget].update_targets_value()
                elif self.packet == "readback":
                    self.spinDict[widget].update_readback_value()

    def okButtonPressed(self):
        message, command = [], []
        for widget in self.spinDict:
            if self.spinDict[widget].manuallyUpdated:
                setVal = self.spinDict[widget].simpleSpin.value()
                message.append("set" + widget + " to " + str(setVal))
                command.append(
                    [self.spinDict[widget].cmd_type, self.spinDict[widget].cmd_code, setVal]
                )
        self.popup = SetConfirmPopup(self, self.NativeUI, message, command)
        self.popup.okButton.pressed.connect(self.commandSent)
        self.popup.show()

    def commandSent(self):
        for widget in self.spinDict:
            if self.spinDict[widget].manuallyUpdated:
                self.spinDict[widget].manuallyUpdated = False

    def cancelButtonPressed(self):
        for widget in self.spinDict:
            if self.spinDict[widget].manuallyUpdated:
                self.spinDict[widget].manuallyUpdated = False
        self.liveUpdating = True
