from PySide2 import QtCore, QtGui, QtWidgets
from global_widgets.global_ok_cancel_buttons import okButton, cancelButton


class TabModeswitchButton(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.NativeUI = NativeUI

        layout = QtWidgets.QHBoxLayout(self)
        self.label = QtWidgets.QLabel("Mode: ")
        self.switchButton = QtWidgets.QPushButton("PCAC")
        layout.addWidget(self.label)
        layout.addWidget(self.switchButton)
        self.setLayout(layout)

        self.switchButton.pressed.connect(self.switch_button_pressed)

    def switch_button_pressed(self):
        self.mode_popup = modeswitchPopup(self.NativeUI)
        self.mode_popup.show()
        self.mode_popup.okbutton.pressed.connect(self.changeText)

    def changeText(self):
        self.switchButton.setText(self.mode_popup.mode)


class modeswitchPopup(QtWidgets.QDialog):
    def __init__(self, NativeUI, *args, **kwargs):
        super(modeswitchPopup, self).__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        self.settingsList = self.NativeUI.modes_view.modeTab.settingsList
        modeList = self.NativeUI.modes_view.modeTab.modeList
        self.modeSpinDict = self.NativeUI.modes_view.modeTab.spinDict

        ## Radio buttons

        vradioLayout = QtWidgets.QVBoxLayout()
        groupBox = (
            QtWidgets.QGroupBox()
        )  # handles exclusive button selection of radio buttons
        radioButtons = []
        for mode in modeList:
            button = QtWidgets.QRadioButton(mode)
            radioButtons.append(button)
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
        self.okbutton = okButton(NativeUI)
        self.okbutton.pressed.connect(self.ok_button_pressed)
        self.cancelbutton = cancelButton(NativeUI)
        self.cancelbutton.pressed.connect(self.cancel_button_pressed)
        hbuttonlayout.addWidget(self.okbutton)
        hbuttonlayout.addWidget(self.cancelbutton)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addLayout(hbuttonlayout)

        ## Final, general, initiation steps

        self.setLayout(vlayout)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        radioButtons[0].click()  # 1st button clicked by default
        # self.update_settings_data(radioButtons[0])

        self.setStyleSheet(
            "background-color:" + NativeUI.colors["background"].name() + ";"
            "color:" + NativeUI.colors["foreground"].name() + ";"
            "font: 16pt bold;"
        )

        self.update_settings_data(radioButtons[0])

    def update_settings_data(self, radioButton):
        self.mode = radioButton.text()
        data = self.NativeUI.get_targets_db()
        for currentLabel, newLabel, settings in zip(
            self.currentLabelList, self.newLabelList, self.settingsList
        ):
            currentLabel.setText(str(round(data[settings[2]], 4)))
            setVal = self.modeSpinDict[self.mode + settings[0]].simpleSpin.value()
            newLabel.setText(str(round(setVal, 4)))

    def ok_button_pressed(self):
        self.NativeUI.q_send_cmd("SET_MODE", self.mode)
        self.close()

    def cancel_button_pressed(self):
        self.close()
