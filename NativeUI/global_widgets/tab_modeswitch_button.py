
from PySide2 import QtCore, QtGui, QtWidgets
from global_widgets.global_ok_cancel_buttons import okButton, cancelButton

class TabModeswitchButton(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.NativeUI = NativeUI

        layout = QtWidgets.QHBoxLayout(self)
        self.label = QtWidgets.QLabel('Mode: ')
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
        self.spinDict = self.NativeUI.modes_view.modeTab.spinDict

        vradioLayout = QtWidgets.QVBoxLayout()
        groupBox = QtWidgets.QGroupBox()
        radioButtons = []
        for mode in modeList:
            button = QtWidgets.QRadioButton(mode)
            radioButtons.append(button)
            vradioLayout.addWidget(button)
            button.pressed.connect(lambda i=button: self.update_settings_data(i))
        groupBox.setLayout(vradioLayout)
        
        valuesLayout = QtWidgets.QVBoxLayout()
        
        initlabel = settingsLabel(' ') # titles
        initlabel.currentLabel.setText('Current')
        initlabel.settingLabel.setText('New')
        valuesLayout.addWidget(initlabel)

        self.labelList = []
        for settings in self.settingsList:
            label = settingsLabel(settings[0])
            self.labelList.append(label)
            #settingVal = spinDict
            valuesLayout.addWidget(label)

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(groupBox)
        hlayout.addLayout(valuesLayout)

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

        self.setLayout(vlayout)

        radioButtons[0].click()
        self.update_settings_data(radioButtons[0])

    def update_settings_data(self,button):
        self.mode = button.text()
        data = self.NativeUI.get_targets_db()
        for label,settings in zip(self.labelList,self.settingsList):
            currentVal = data[settings[2]]
            setVal = self.spinDict[self.mode + settings[0]].simpleSpin.value()
            label.update_values(currentVal, setVal)

    def ok_button_pressed(self):
        self.NativeUI.q_send_cmd('SET_MODE', self.mode)
        # need to decide whetehr this sets individual values or just mode
        # for label,settings in zip(self.labelList,self.settingsList):
        #     currentVal = data[settings[2]]
        #     setVal = self.spinDict[self.mode + settings[0]].simpleSpin.value()
        #     label.update_values(currentVal, setVal)
        self.close()
    
    
    def cancel_button_pressed(self):
        self.close()



class settingsLabel(QtWidgets.QWidget):
    def __init__(self, name, *args, **kwargs):
        super(settingsLabel, self).__init__(*args, **kwargs)
        
        self.nameLabel = QtWidgets.QLabel(name)
        self.currentLabel = QtWidgets.QLabel(str(0))
        self.settingLabel = QtWidgets.QLabel(str(0))
        self.settingLabel.setStyleSheet('color:red')

        hlayout = QtWidgets.QHBoxLayout()
        labels = [self.nameLabel, self.currentLabel, self.settingLabel]
        for label in labels:
            hlayout.addWidget(label)
        self.setLayout(hlayout)

    def update_values(self,currentVal, setVal):
        self.currentLabel.setText(str(currentVal))
        self.settingLabel.setText(str(setVal))