from PySide2 import QtWidgets, QtGui, QtCore
from settings_widgets.tab_expert import simpleSpin


class TemplateSetValues(
    QtWidgets.QWidget
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, *args, **kwargs):
        super(TemplateSetValues, self).__init__(*args, **kwargs)
        self.liveUpdating = True
        self.layoutList = []

        self.timer = QtCore.QTimer()
        self.timer.setInterval(160)  # just faster than 60Hz
        self.timer.timeout.connect(self.update_settings_data)
        self.timer.start()

    def finaliseLayout(self):
        vlayout = QtWidgets.QVBoxLayout()
        for layout in self.layoutList:
            vlayout.addLayout(layout)
        self.setLayout(vlayout)

    def addSpinSingleCol(self, settingsList):
        self.spinDict = {}
        vOptionLayout = QtWidgets.QVBoxLayout()
        for info in settingsList:
            self.spinDict[info[0]] = simpleSpin(info)
            vOptionLayout.addWidget(self.spinDict[info[0]])
        self.layoutList.append(vOptionLayout)

    def addButtons(self):
        hlayout = QtWidgets.QHBoxLayout()
        self.okButton = QtWidgets.QPushButton()
        self.okButton.setStyleSheet(
            "height:50px; background-color:white; border-radius:4px;"
        )
        self.okButton.pressed.connect(self.okButtonPressed)
        hlayout.addWidget(self.okButton)

        self.cancelButton = QtWidgets.QPushButton()
        self.cancelButton.setStyleSheet(
            "height:50px; background-color:white; border-radius:4px;"
        )
        self.cancelButton.pressed.connect(self.cancelButtonPressed)
        hlayout.addWidget(self.cancelButton)
        self.layoutList.append(hlayout)

    def update_settings_data(self):
        if self.liveUpdating:
            for widget in self.spinDict:
                self.spinDict[widget].update_targets_value()

    def okButtonPressed(self):
        message = []
        self.liveUpdating = True
        for widget in self.spinDict:
            # print(widget)
            if self.spinDict[widget].manuallyUpdated:
                setVal = self.spinDict[widget].simpleSpin.value()
                # print('manually updated')
                print("set" + widget + " to " + str(setVal))
                self.spinDict[widget].manuallyUpdated = False

    def cancelButtonPressed(self):
        self.liveUpdating = True
