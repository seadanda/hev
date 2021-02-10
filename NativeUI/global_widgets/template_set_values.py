from PySide2 import QtWidgets, QtGui, QtCore
from settings_widgets.tab_expert import simpleSpin
from global_widgets.global_send_popup import SetConfirmPopup


class TemplateSetValues(
    QtWidgets.QWidget
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, *args, **kwargs):
        super(TemplateSetValues, self).__init__(*args, **kwargs)
        self.liveUpdating = True
        self.layoutList = []
        self.spinDict = {}

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
        vOptionLayout = QtWidgets.QVBoxLayout()
        for info in settingsList:
            self.spinDict[info[0]] = simpleSpin(info)
            vOptionLayout.addWidget(self.spinDict[info[0]])
        self.layoutList.append(vOptionLayout)

    def addSpinDblCol(self, settingsList):
        grid = QtWidgets.QGridLayout()
        i = 0
        for info in settingsList:
            self.spinDict[info[0]] = simpleSpin(info)
            grid.addWidget(self.spinDict[info[0]], int(i / 2), i % 2)
            i = i + 1
        self.layoutList.append(grid)

    def addExpertControls(self, controlDict):
        grid = QtWidgets.QGridLayout()
        i = 0
        for section in controlDict.keys():

            self.titleLabel = QtWidgets.QLabel(section)
            self.titleLabel.setStyleSheet("background-color:white")
            self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
            grid.addWidget(self.titleLabel, i, 0, 1, 6)
            j = -1
            for boxInfo in controlDict[section]:
                j = j + 1
                # label, units = boxInfo, controlDict[section][boxInfo]
                self.spinDict[boxInfo[0]] = simpleSpin(boxInfo)
                # self.spinInfo.append(boxInfo)
                grid.addWidget(
                    self.spinDict[boxInfo[0]], i + 1 + int(j / 3), 2 * (j % 3), 1, 2
                )

            i = i + 1 + int(j / 3) + 1
        self.layoutList.append(grid)

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
                # Added to avoid the error this throws making the output unreadable
                try:
                    self.spinDict[widget].update_targets_value()
                except AttributeError:
                    return

    def okButtonPressed(self):
        message = []
        self.liveUpdating = True
        for widget in self.spinDict:
            if self.spinDict[widget].manuallyUpdated:
                setVal = self.spinDict[widget].simpleSpin.value()
                self.spinDict[widget].manuallyUpdated = False
                message.append("set" + widget + " to " + str(setVal))
        self.popup = SetConfirmPopup(message)
        self.popup.show()

    def cancelButtonPressed(self):
        self.liveUpdating = True
