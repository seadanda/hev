from PySide2 import QtWidgets, QtGui, QtCore
from global_widgets.global_select_button import selectorButton

# from global_widgets.global_spinbox import signallingSpinBox
from global_widgets.template_main_pages import TemplateMainPages
from global_widgets.template_set_values import TemplateSetValues


class TabModes(
    TemplateMainPages
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, NativeUI, *args, **kwargs):
        super(TabModes, self).__init__(NativeUI, *args, **kwargs)
        self.NativeUI = NativeUI
        self.settingsList = [
            [
                "Respiratory Rate",
                "/min",
                "respiratory_rate",
                "SET_TARGET_",
                "RESPIRATORY_RATE",
            ],
            ["Inhale Time", "s", "inhale_time", "SET_TARGET_", "INHALE_TIME"],
            ["IE Ratio", "", "ie_ratio", "SET_TARGET_", "IE_RATIO"],
            [
                "Inhale Trigger Sensitivity",
                "",
                "inhale_trigger_threshold",
                "SET_TARGET_",
                "INHALE_TRIGGER_THRESHOLD",
            ],
            [
                "Exhale Trigger Sensitivity",
                "",
                "exhale_trigger_threshold",
                "SET_TARGET_",
                "EXHALE_TRIGGER_THRESHOLD",
            ],
            [
                "Inhale Pressure",
                "",
                "inspiratory_pressure",
                "SET_TARGET_",
                "INSPIRATORY_PRESSURE",
            ],
            ["Inhale Volume", "", "volume", "SET_TARGET_", "VOLUME"],
            ["Percentage O2", "", "fiO2_percent", "SET_TARGET_", "FIO2_PERCENT"],
        ]

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.setSpacing(0)
        self.pcacButton = selectorButton(NativeUI, "PC/AC")
        self.pcacButton.setProperty("selected", "1")
        self.pcacButton.style().polish(self.pcacButton)
        self.pcacEnable = [1, 0, 1, 1, 0, 1, 0, 1]
        self.pcacVals = [1, 2, 3, 4, 5, 6, 7, 8]
        self.pcacPage = TemplateSetValues(NativeUI)

        self.prvcButton = selectorButton(NativeUI, "PC/AC-PRVC")
        self.prvcEnable = [1, 1, 0, 1, 0, 1, 1, 1]
        self.prvcVals = [2, 3, 4, 5, 6, 7, 8, 9]
        self.prvcPage = TemplateSetValues(NativeUI)

        self.psvButton = selectorButton(NativeUI, "PC-PSV")
        self.psvEnable = [1, 1, 0, 1, 0, 1, 0, 1]
        self.psvVals = [3, 4, 5, 6, 7, 8, 9, 1]
        self.psvPage = TemplateSetValues(NativeUI)

        self.cpapButton = selectorButton(NativeUI, "CPAP")
        self.cpapEnable = [1, 0, 1, 1, 0, 1, 0, 1]
        self.cpapVals = [4, 5, 6, 7, 8, 9, 1, 2]
        self.cpapPage = TemplateSetValues(NativeUI)

        self.buttonWidgets = [
            self.pcacButton,
            self.prvcButton,
            self.psvButton,
            self.cpapButton,
        ]
        enableList = [self.pcacEnable, self.prvcEnable, self.psvEnable, self.cpapEnable]
        self.tabsDict = { 'PC/AC':self.pcacPage, 'PC/AC-PRVC':self.prvcPage, 'PC-PSV':self.psvPage, 'CPAP':self.cpapPage}
        self.valsList = [self.pcacVals, self.prvcVals, self.psvVals, self.cpapVals]
        self.modeList = self.NativeUI.modeList
        self.spinDict = {}
        for tab, mode, enable, vals in zip(
            self.tabsDict.values(), self.modeList, enableList, self.valsList
        ):
            #mode = mode.replace("/", "_")
            #mode = mode.replace("-", "_")
            tempSettingsList = [
                [
                    target.replace("SET_TARGET_", "SET_TARGET_" + mode.replace("/", "_").replace("-", "_"))
                    for target in spinInfo
                ]
                for spinInfo in self.settingsList
            ]
            tab.addSpinSingleCol(tempSettingsList)
            tab.mode = mode
            tab.buttonGroup = QtWidgets.QButtonGroup()
            for labelledSpin in tab.spinDict:
                if tab.spinDict[labelledSpin].label == "Inhale Time":
                    tab.radioButtonTime = QtWidgets.QRadioButton()
                    tab.radioButtonTime.setChecked(bool(enable[1]))
                    tab.radioButtonTime.toggled.connect(
                        lambda i=tab.radioButtonTime, j=tab.spinDict[
                            labelledSpin
                        ], k=tab.mode: self.radioPressed(i, j, k)
                    )
                    tab.spinDict[labelledSpin].insertWidget(tab.radioButtonTime, 1)
                    tab.buttonGroup.addButton(tab.radioButtonTime)

                if tab.spinDict[labelledSpin].label == "IE Ratio":
                    tab.radioButtonRat = QtWidgets.QRadioButton()
                    tab.radioButtonRat.setChecked(bool(enable[2]))
                    tab.radioButtonRat.toggled.connect(
                        lambda i=tab.radioButtonRat, j=tab.spinDict[
                            labelledSpin
                        ], k=tab.mode: self.radioPressed(i, j, k)
                    )
                    tab.spinDict[labelledSpin].insertWidget(tab.radioButtonRat, 1)
                    tab.buttonGroup.addButton(tab.radioButtonRat)

            tab.addModeButtons()
            tab.finaliseLayout()
            self._setEnabled(tab, enable, vals)
            self.spinDict[mode] = tab.spinDict

        # self.addRadioButtons()
        self.tabsList = self.tabsDict.values()
        self.buildPage(self.buttonWidgets, self.tabsList)

    # def addRadioButtons(self):
    #     for tab in self.tabsList:
    #         tab.buttonGroup = QtWidgets.QButtonGroup()
    #         for labelledSpin in tab.spinDict:
    #             if tab.spinDict[labelledSpin].label == "Inhale Time":
    #                 tab.radioButtonTime = QtWidgets.QRadioButton()
    #                 tab.radioButtonTime.toggled.connect(
    #                     lambda i=tab.radioButtonTime, j=tab.spinDict[
    #                         labelledSpin
    #                     ], k=tab.mode: self.radioPressed(i, j, k)
    #                 )
    #                 tab.spinDict[labelledSpin].insertWidget(tab.radioButtonTime, 1)
    #                 tab.buttonGroup.addButton(tab.radioButtonTime)

    #             if tab.spinDict[labelledSpin].label == "IE Ratio":
    #                 tab.radioButtonRat = QtWidgets.QRadioButton()
    #                 tab.radioButtonRat.toggled.connect(
    #                     lambda i=tab.radioButtonRat, j=tab.spinDict[
    #                         labelledSpin
    #                     ]: self.radioPressed(i, j, k)
    #                 )
    #                 tab.spinDict[labelledSpin].insertWidget(tab.radioButtonRat, 1)
    #                 tab.buttonGroup.addButton(tab.radioButtonRat)

    def radioPressed(self, radioButtonState, labelledSpin, tabMode):
        labelledSpin.simpleSpin.setEnabled(radioButtonState)
        labelledSpin.simpleSpin.setProperty("bgColour", str(int(not radioButtonState)))
        labelledSpin.simpleSpin.setProperty(
            "textColour", str(int(not radioButtonState))
        )

        labelledSpin.simpleSpin.style().unpolish(labelledSpin.simpleSpin)
        labelledSpin.simpleSpin.style().polish(labelledSpin.simpleSpin)

        if tabMode == self.NativeUI.currentMode:
            a=1
            self.NativeUI.widgets.spin_buttons.setStackWidget(labelledSpin.label)

    def _setColour(self, buttonWidg):
        for button, box in zip(self.buttonWidgets, self.pageList):
            if button == buttonWidg:
                button.setProperty("selected", "1")
                self.stack.setCurrentWidget(box)
            else:
                button.setProperty("selected", "0")
            button.style().unpolish(button)
            button.style().polish(button)

    def _modeSwitch(self, box):
        self.stack.setCurrentWidget(box)

    def _setEnabled(self, box, enableList, values):
        for widget, enableBool, value in zip(box.spinDict, enableList, values):
            box.spinDict[widget].simpleSpin.setEnabled(enableBool)
            if enableBool == 1:
                box.spinDict[widget].simpleSpin.setProperty("bgColour", "0")
                box.spinDict[widget].simpleSpin.setProperty("textColour", "0")
            if enableBool == 0:
                box.spinDict[widget].simpleSpin.setProperty("bgColour", "1")
                box.spinDict[widget].simpleSpin.setProperty("textColour", "1")
            box.spinDict[widget].simpleSpin.style().unpolish(
                box.spinDict[widget].simpleSpin
            )
            box.spinDict[widget].simpleSpin.style().polish(
                box.spinDict[widget].simpleSpin
            )
            box.spinDict[widget].simpleSpin.setValue(value)
