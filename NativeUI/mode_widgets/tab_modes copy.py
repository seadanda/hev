from PySide2 import QtWidgets, QtGui, QtCore
from global_widgets.global_select_button import selectorButton
from global_widgets.global_spinbox import simpleSpin
from global_widgets.template_set_values import TemplateSetValues


class TabModes(
    TemplateSetValues
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, *args, **kwargs):
        super(TabModes, self).__init__(*args, **kwargs)

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
        self.pcacButton = selectorButton("PC/AC")
        self.pcacButton.setProperty("selected", "1")
        self.pcacButton.style().polish(self.pcacButton)
        self.pcacEnable = [1, 0, 1, 1, 0, 1, 0, 1]
        self.pcacVals = [1, 2, 3, 4, 5, 6, 7, 8]
        # self.pcacBoxes = TemplateSetValues()
        # self.pcacBoxes.addSpinSingleCol(settingsList)
        # self.pcacBoxes.finaliseLayout()

        self.prvcButton = selectorButton("PC/AC-PRVC")
        self.prvcEnable = [1, 1, 0, 1, 0, 1, 1, 1]
        self.prvcVals = [2, 3, 4, 5, 6, 7, 8, 9]
        # self.prvcBoxes = TemplateSetValues()
        # self.prvcBoxes.addSpinSingleCol(settingsList)
        # self.prvcBoxes.finaliseLayout()

        self.psvButton = selectorButton("PC-PSV")
        self.psvEnable = [1, 1, 0, 1, 0, 1, 0, 1]
        self.psvVals = [3, 4, 5, 6, 7, 8, 9, 1]
        # self.psvBoxes = TemplateSetValues()
        # self.psvBoxes.addSpinSingleCol(settingsList)
        # self.psvBoxes.finaliseLayout()

        self.cpapButton = selectorButton("CPAP")
        self.cpapEnable = [1, 0, 1, 1, 0, 1, 0, 1]
        self.cpapVals = [4, 5, 6, 7, 8, 9, 1, 2]
        # self.cpapBoxes = TemplateSetValues()
        # self.cpapBoxes.addSpinSingleCol(settingsList)
        # self.cpapBoxes.finaliseLayout()

        self.buttonWidgets = [
            self.pcacButton,
            self.prvcButton,
            self.psvButton,
            self.cpapButton,
        ]
        enableList = [self.pcacEnable, self.prvcEnable, self.psvEnable, self.cpapEnable]
        # self.boxes = [self.pcacBoxes, self.prvcBoxes, self.psvBoxes, self.cpapBoxes]
        self.valsList = [self.pcacVals, self.prvcVals, self.psvVals, self.cpapVals]
        for button, array, vals in zip(self.buttonWidgets, enableList, self.valsList):
            hlayout.addWidget(button)
            #            self.modeSwitch2(box, array)
            button.pressed.connect(lambda i=button: self.setColour(i))
            # button.pressed.connect(lambda i=array: self.modeSwitch(i))
            button.pressed.connect(lambda i=vals: self.modeSwitch(i))
        self.layoutList.append(hlayout)

        # vlayout = QtWidgets.QVBoxLayout()
        # self.stack = QtWidgets.QStackedWidget()
        # for box in self.boxes:
        #     self.stack.addWidget(box)
        # self.stack.setCurrentWidget(self.pcacBoxes)
        # vlayout.addWidget(self.stack)
        # self.layoutList.append(vlayout)
        self.addSpinSingleCol(settingsList)
        # self.addSpinSingleCol(settingsList)
        self.addButtons()
        self.finaliseLayout()

        for spinBox in
        # self.modeSwitch(self.pcacEnable)

    def setColour(self, buttonWidg):
        for button in self.buttonWidgets:
            if button == buttonWidg:
                button.setProperty("selected", "1")
            else:
                button.setProperty("selected", "0")
            button.style().unpolish(button)
            button.style().polish(button)

    def modeSwitch(self, vals):
        for widget, value in zip(self.spinDict, vals):
            self.spinDict[widget].simpleSpin.setValue(value)

    def modeSwitch3(self, box):
        self.stack.setCurrentWidget(box)

    def modeSwitch2(self, box, enableList):
        for widget, enableBool in zip(box.spinDict, enableList):
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

    def modeSwitch3(self, enableList):
        for widget, enableBool in zip(self.spinDict, enableList):
            self.spinDict[widget].simpleSpin.setEnabled(enableBool)
            if enableBool == 1:
                self.spinDict[widget].simpleSpin.setProperty("bgColour", "0")
            if enableBool == 0:
                self.spinDict[widget].simpleSpin.setProperty("bgColour", "1")
            self.spinDict[widget].simpleSpin.style().unpolish(
                self.spinDict[widget].simpleSpin
            )
            self.spinDict[widget].simpleSpin.style().polish(
                self.spinDict[widget].simpleSpin
            )


# class TabModes(
#     QtWidgets.QWidget
# ):  # chose QWidget over QDialog family because easier to modify
#     def __init__(self, *args, **kwargs):
#         super(TabModes, self).__init__(*args, **kwargs)

#         hlayout = QtWidgets.QHBoxLayout()
#         self.pcacButton = QtWidgets.QPushButton('PC/AC')
#         self.pcacEnable = [1,0,1,1,0,1,0,1]
#         self.prvcButton = QtWidgets.QPushButton('PC/AC-PRVC')
#         self.prvcEnable = [1,1,0,1,0,1,1,1]
#         self.psvButton = QtWidgets.QPushButton('PC-PSV')
#         self.psvEnable = [1,1,0,1,0,1,0,1]
#         self.cpapButton = QtWidgets.QPushButton('CPAP')
#         self.cpapEnable = [1,0,1,1,0,1,0,1]
#         buttonWidgets = [self.pcacButton,self.prvcButton,self.psvButton,self.cpapButton]
#         enableList = [self.pcacEnable, self.prvcEnable, self.psvEnable, self.cpapEnable]
#         for button, array in zip(buttonWidgets,enableList):
#             hlayout.addWidget(button)
#             button.pressed.connect(lambda i=array: self.modeSwitch(i))

#         self.liveUpdating = True
#         settingsList = [
#             ["Respiratory Rate", "/min", "respiratory_rate"],
#             ["Inhale Time", "s", "inhale_time"],
#             ["IE Ratio", "", "ie_ratio"],
#             ["Inhale Trigger Sensitivity", "", "inhale_trigger_threshold"],
#             ["Exhale Trigger Sensitivity", "", "exhale_trigger_threshold"],
#             ["Inhale Pressure", "", "inspiratory_pressure"],
#             ["Inhale volume", "", "volume"],
#             ["Percentage O2", "", "fiO2_percent"]
#         ]
#         self.spinDict = {}
#         vOptionLayout = QtWidgets.QVBoxLayout()
#         for info in settingsList:
#             self.spinDict[info[0]] = simpleSpin(info)
#             vOptionLayout.addWidget(self.spinDict[info[0]])

#         hlayout2 = QtWidgets.QHBoxLayout()
#         self.okButton = QtWidgets.QPushButton()
#         self.okButton.setStyleSheet(
#             "height:50px; background-color:white; border-radius:4px;"
#         )
#         self.okButton.pressed.connect(self.okButtonPressed)
#         hlayout2.addWidget(self.okButton)

#         self.cancelButton = QtWidgets.QPushButton()
#         self.cancelButton.setStyleSheet(
#             "height:50px; background-color:white; border-radius:4px;"
#         )
#         self.cancelButton.pressed.connect(self.cancelButtonPressed)
#         hlayout2.addWidget(self.cancelButton)

#         vlayout = QtWidgets.QVBoxLayout()
#         vlayout.addLayout(hlayout)
#         vlayout.addLayout(vOptionLayout)
#         vlayout.addLayout(hlayout2)
#         self.setLayout(vlayout)

#         self.timer = QtCore.QTimer()
#         self.timer.setInterval(160)  # just faster than 60Hz
#         self.timer.timeout.connect(self.update_settings_data)
#         self.timer.start()

#     def update_settings_data(self):
#         if self.liveUpdating:
#             for widget in self.spinDict:
#                 self.spinDict[widget].update_targets_value()

#     def okButtonPressed(self):
#         message = []
#         self.liveUpdating = True
#         for widget in self.spinDict:
#             #print(widget)
#             if self.spinDict[widget].manuallyUpdated:
#                 setVal = self.spinDict[widget].simpleSpin.value()
#                 #print('manually updated')
#                 print('set'  + widget + ' to ' + str(setVal) )
#                 self.spinDict[widget].manuallyUpdated = False

#     def cancelButtonPressed(self):
#         self.liveUpdating = True

#     def modeSwitch(self,enableList):
#         print('switching')
#         print(enableList)
#         for widget,enableBool in zip(self.spinDict, enableList):
#             self.spinDict[widget].simpleSpin.setEnabled(enableBool)
#             print(enableBool)
#             if enableBool==1:
#                 print('doing it')
#                 self.spinDict[widget].simpleSpin.setProperty("bgColour", "0")
#             if enableBool ==0:
#                 print('again')
#                 self.spinDict[widget].simpleSpin.setProperty("bgColour", "1")
#             self.spinDict[widget].simpleSpin.style().unpolish(self.spinDict[widget].simpleSpin)
#             self.spinDict[widget].simpleSpin.style().polish(self.spinDict[widget].simpleSpin)
#             print('exiting')
