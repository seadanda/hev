from PySide2 import QtWidgets, QtGui, QtCore
from global_widgets.global_select_button import selectorButton
from global_widgets.global_spinbox import simpleSpin
from global_widgets.template_set_values import TemplateSetValues


class TabModes(
    TemplateSetValues
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, NativeUI, *args, **kwargs):
        super(TabModes, self).__init__(NativeUI, *args, **kwargs)

        settingsList = [
            ["Respiratory Rate", "/min", "respiratory_rate"],
            ["Inhale Time", "s", "inhale_time"],
            ["IE Ratio", "", "ie_ratio"],
            ["Inhale Trigger Sensitivity", "", "inhale_trigger_threshold"],
            ["Exhale Trigger Sensitivity", "", "exhale_trigger_threshold"],
            ["Inhale Pressure", "", "inspiratory_pressure"],
            ["Inhale volume", "", "volume"],
            ["Percentage O2", "", "fiO2_percent"],
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
        self.pageList = [self.pcacPage, self.prvcPage, self.psvPage, self.cpapPage]
        self.valsList = [self.pcacVals, self.prvcVals, self.psvVals, self.cpapVals]
        for button, page, enableList, vals in zip(
            self.buttonWidgets, self.pageList, enableList, self.valsList
        ):
            hlayout.addWidget(button)
            page.addSpinSingleCol(settingsList)
            page.finaliseLayout()
            self._setEnabled(page, enableList, vals)
            button.pressed.connect(lambda i=button: self._setColour(i))
        self.layoutList.append(hlayout)

        labels = ["PCAC", "PRVC", "PSV", "CPAP"]
        vlayout = QtWidgets.QVBoxLayout()
        self.stack = QtWidgets.QStackedWidget()
        for box, label in zip(self.pageList, labels):
            self.stack.addWidget(box)
            for widg in box.spinDict:
                self.spinDict[label + widg] = box.spinDict[widg]
        self.stack.setCurrentWidget(self.pcacPage)
        vlayout.addWidget(self.stack)
        self.layoutList.append(vlayout)

        self.addButtons()
        self.finaliseLayout()

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
            if enableBool == 0:
                box.spinDict[widget].simpleSpin.setProperty("bgColour", "1")
            box.spinDict[widget].simpleSpin.style().unpolish(
                box.spinDict[widget].simpleSpin
            )
            box.spinDict[widget].simpleSpin.style().polish(
                box.spinDict[widget].simpleSpin
            )
            box.spinDict[widget].simpleSpin.setValue(value)
