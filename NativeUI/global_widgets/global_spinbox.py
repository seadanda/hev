#!/usr/bin/env python3

"""
global_spinbox.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

from PySide2 import QtWidgets, QtGui, QtCore
from global_widgets.global_typeval_popup import TypeValuePopup


class signallingSpinBox(QtWidgets.QDoubleSpinBox):
    manualChanged = QtCore.Signal()

    def __init__(self, NativeUI):
        super().__init__()
        self.lineEdit().installEventFilter(self)

        self.popUp = TypeValuePopup(NativeUI)
        self.popUp.okButton.clicked.connect(self.okButtonPressed)
        self.popUp.cancelButton.clicked.connect(self.cancelButtonPressed)

    def okButtonPressed(self):
        val = float(self.popUp.lineEdit.text())
        self.setValue(val)
        self.popUp.close()
        self.manualChanged.emit()

    def cancelButtonPressed(self):
        self.popUp.lineEdit.setText(self.popUp.lineEdit.saveVal)
        self.popUp.close()

    def stepBy(self, step):
        value = self.value()
        self.prevValue = value
        super(signallingSpinBox, self).stepBy(step)
        if self.value() != value:
            self.manualChanged.emit()

    def eventFilter(self, source, event):
        if (
            source is self.lineEdit()
            and event.type() == QtCore.QEvent.MouseButtonDblClick
        ):
            self.popUp.lineEdit.setText(str(self.value()))
            self.popUp.show()
            return True
        return False


class labelledSpin(QtWidgets.QWidget):
    def __init__(self, template, NativeUI, infoArray, *args, **kwargs):
        super(labelledSpin, self).__init__(*args, **kwargs)
        # print(infoArray)
        self.NativeUI = NativeUI
        self.template = template
        self.cmd_type, self.cmd_code = "", ""
        self.min, self.max, self.step = 0, 10000, 0.3
        self.decPlaces = 2
        if len(infoArray) == 9:
            self.label, self.units, self.tag, self.cmd_type, self.cmd_code, self.min, self.max, self.step, self.decPlaces = (
                infoArray
            )
        elif len(infoArray) == 5:
            self.label, self.units, self.tag, self.cmd_type, self.cmd_code = infoArray
        elif len(infoArray) == 3:
            self.label, self.units, self.tag = infoArray
        self.manuallyUpdated = False
        layout = QtWidgets.QHBoxLayout()
        widgetList = []
        textStyle = "color:white;" "font-size: " + NativeUI.text_size + ";"

        if self.label != "":
            self.nameLabel = QtWidgets.QLabel(self.label)
            self.nameLabel.setStyleSheet(textStyle)
            self.nameLabel.setAlignment(QtCore.Qt.AlignRight)
            widgetList.append(self.nameLabel)

        self.simpleSpin = signallingSpinBox(NativeUI)
        self.simpleSpin.setRange(self.min, self.max)
        self.simpleSpin.setSingleStep(self.step)
        self.simpleSpin.setDecimals(self.decPlaces)
        self.simpleSpin.setStyleSheet(
            "QDoubleSpinBox{"
            "   width: 100px"
            "   font-size: " + NativeUI.text_size + ";"
            "}"
            "QDoubleSpinBox[bgColour='0']{"
            "   background-color:white;"
            "}"
            "QDoubleSpinBox[bgColour='1']{"
            "   background-color:grey;"
            "}"
            "QDoubleSpinBox[textColour='0']{"
            "   color:black"
            "}"
            "QDoubleSpinBox[textColour='1']{"
            "   color:red"
            "}"
            "QDoubleSpinBox::up-button{"
            "   width:20;"
            "   border:solid white;"
            "   color:black"
            "}"
            "QDoubleSpinBox::down-button{"
            "   width:20;"
            "}"
        )
        self.simpleSpin.setProperty("textColour", "0")
        self.simpleSpin.setProperty("bgColour", "0")
        self.simpleSpin.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus
        )
        self.simpleSpin.setAlignment(QtCore.Qt.AlignCenter)
        if self.cmd_type == "":
            self.simpleSpin.setReadOnly(True)
            self.simpleSpin.setProperty("bgColour", "1")
        widgetList.append(self.simpleSpin)

        if self.units != "":
            self.unitLabel = QtWidgets.QLabel(self.units)
            self.unitLabel.setStyleSheet(textStyle)
            self.unitLabel.setAlignment(QtCore.Qt.AlignLeft)
            widgetList.append(self.unitLabel)

        for widget in widgetList:
            layout.addWidget(widget)

        self.setLayout(layout)
        self.simpleSpin.manualChanged.connect(self.manualStep)
        # self.simpleSpin.valueChanged.connect(self.valChange)

    def manualStep(self):
        if self.manuallyUpdated != True:
            self.oldValue = self.simpleSpin.prevValue
        self.template.liveUpdating = False
        self.manuallyUpdated = True
        if self.simpleSpin.value() != self.oldValue:
            self.simpleSpin.setProperty("textColour", "1")
        else:
            self.simpleSpin.setProperty("textColour", "0")
            self.manuallyUpdated = False
        self.simpleSpin.style().polish(self.simpleSpin)

    def update_readback_value(self):
        newVal = self.NativeUI.get_readback_db()
        if newVal == {}:
            a = 1  # do nothing
        else:
            self.simpleSpin.setValue(newVal[self.tag])
            self.simpleSpin.setProperty("textColour", "0")
            self.simpleSpin.style().polish(self.simpleSpin)

    def update_targets_value(self):
        newVal = self.NativeUI.get_targets_db()
        if (newVal == {}) or (self.tag == ""):
            a = 1  # do nothing
        else:
            self.simpleSpin.setValue(newVal[self.tag])
            self.simpleSpin.setProperty("textColour", "0")
            self.simpleSpin.style().polish(self.simpleSpin)
