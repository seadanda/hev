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
from CommsCommon import ReadbackFormat


class signallingSpinBox(QtWidgets.QDoubleSpinBox):
    """the base class for all the spinboxes.
    Additional functionality:
         A popup to edit the value appears when the box is double clicked.
         A signal is emitted when the user presses up or down buttons.
    """

    manualChanged = QtCore.Signal()
    programmaticallyChanged = QtCore.Signal()

    def __init__(self, NativeUI, popup, label_text, min, max, initVal, step, decPlaces):
        super().__init__()
        self.lineEdit().installEventFilter(self)
        self.editable = True
        self.label_text, self.min, self.max, self.initVal, self.step, self.decPlaces = label_text, min, max, initVal, step, decPlaces
        self.setRange(min, max)
        self.setSingleStep(step)
        self.setDecimals(decPlaces)
        self.setValue(initVal)
        self.NativeUI = NativeUI
        #self.populateVals = [label_text, min, max, initVal, step, decPlaces]
        self.popUp = popup# TypeValuePopup(NativeUI, label_text, min, max, initVal, step, decPlaces)
        #self.popUp.okButton.clicked.connect(self.okButtonPressed)
        #self.popUp.cancelButton.clicked.connect(self.cancelButtonPressed)

    def setEditability(self, setBool):
        self.editable = setBool

    def okButtonPressed(self):
        """Ok button press applies changes in popup to the spin box, closes the popup, and emits a signal"""
        val = float(self.popUp.lineEdit.text())
        self.setValue(val)
        self.popUp.close()
        self.manualChanged.emit()

    def cancelButtonPressed(self):
        """Cancel button press reverts changes and closes popup"""
        self.popUp.lineEdit.setText(self.popUp.lineEdit.saveVal)
        self.popUp.close()

    def stepBy(self, step):
        """Overrides stepBy to store previous value and emit a signal when called"""
        value = self.value()
        self.prevValue = value
        super(signallingSpinBox, self).stepBy(step)
        if self.value() != value:
            self.manualChanged.emit()

    def set_value(self, value):
        self.setValue(value)
        self.programmaticallyChanged.emit()

    def eventFilter(self, source, event):
        """Overrides event filter to implement response to double click """
        if (
            source is self.lineEdit()
            and event.type() == QtCore.QEvent.MouseButtonDblClick
        ):
            if not self.editable:
                return
            #self.popUp.lineEdit.setText(str(self.value()))
            #self.popUp.lineEdit.setFocus()
            self.popUp.populatePopup(self,self.NativeUI.display_stack.currentWidget())
            self.NativeUI.display_stack.setCurrentWidget(self.popUp)

            #self.popUp.show()
            return True
        return False


class labelledSpin(QtWidgets.QWidget):
    """Combines signalling spin box with information relevant to its layout and to handle value updates.
    It is created by an information array which indicates labels, units, command type and code for value setting,
    and the range of permitted values"""

    def __init__(self, NativeUI, popup, infoArray, *args, **kwargs):
        super(labelledSpin, self).__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        self.cmd_type, self.cmd_code = "", ""
        self.min, self.max, self.step = 0, 10000, 0.3
        self.initVal = 1
        self.currentDbValue = self.initVal
        self.decPlaces = 2
        self.label = "default"
        if len(infoArray) == 10:
            self.label, self.units, self.tag, self.cmd_type, self.cmd_code, self.min, self.max, self.initVal, self.step, self.decPlaces = (
                infoArray
            )
        if len(infoArray) == 9:
            self.label, self.units, self.tag, self.cmd_type, self.cmd_code, self.min, self.max, self.step, self.decPlaces = (
                infoArray
            )
        elif len(infoArray) == 5:
            self.label, self.units, self.tag, self.cmd_type, self.cmd_code = infoArray
        elif len(infoArray) == 3:
            self.label, self.units, self.tag = infoArray
        self.manuallyUpdated = False

        self.layout = QtWidgets.QHBoxLayout()
        textStyle = "color:white;"

        # if self.label != "":
        self.nameLabel = QtWidgets.QLabel(self.label)
        self.nameLabel.setStyleSheet(textStyle)
        self.nameLabel.setFont(NativeUI.text_font)
        self.nameLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.simpleSpin = signallingSpinBox(NativeUI, popup, self.label, self.min, self.max, self.initVal, self.step, self.decPlaces)
        # self.simpleSpin.setRange(self.min, self.max)
        # self.simpleSpin.setSingleStep(self.step)
        # self.simpleSpin.setDecimals(self.decPlaces)
        # self.simpleSpin.setValue(self.initVal)
        self.simpleSpin.setStyleSheet(
            "QDoubleSpinBox{"
            "    width:100px;"  # TODO: unhardcode
            "}"
            "QDoubleSpinBox[bgColour='1']{"
            "    background-color:" + NativeUI.colors["page_foreground"].name() + ";"
            "}"
            "QDoubleSpinBox[bgColour='0']{"
            "    background-color:" + NativeUI.colors["page_background"].name() + ";"
            "}"
            "QDoubleSpinBox[textColour='1']{"
            "    color:" + NativeUI.colors["page_background"].name() + ";"
            "}"
            "QDoubleSpinBox[textColour='0']{"
            "    color:" + NativeUI.colors["page_foreground"].name() + ";"
            "}"
            "QDoubleSpinBox[textColour='2']{"
            "    color:" + NativeUI.colors["red"].name() + ";"
            "}"
            "QDoubleSpinBox::up-button{"
            "width:20; "
            "}"
            "QDoubleSpinBox::down-button{"
            "width:20px;"
            "height:20px; "
            "}"
        )
        self.simpleSpin.setFont(NativeUI.text_font)
        self.simpleSpin.setProperty("textColour", "1")
        self.simpleSpin.setProperty("bgColour", "1")
        self.simpleSpin.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus
        )
        self.simpleSpin.setAlignment(QtCore.Qt.AlignCenter)
        if self.cmd_type == "":
            self.simpleSpin.setReadOnly(True)
            # self.simpleSpin.setProperty("bgColour", "1")
            # self.simpleSpin.setProperty("textColour", "2")
            self.simpleSpin.setEditability(False)
            self.simpleSpin.style().polish(self.simpleSpin)

        self.unitLabel = QtWidgets.QLabel(self.units)
        self.unitLabel.setStyleSheet(textStyle)
        self.unitLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self.widgetList = [self.nameLabel, self.simpleSpin, self.unitLabel]
        for widget in self.widgetList:
            self.layout.addWidget(widget)

        self.setLayout(self.layout)
        self.simpleSpin.manualChanged.connect(self.manualStep)
        self.simpleSpin.programmaticallyChanged.connect(self.manualStep)
        # self.simpleSpin.valueChanged.connect(self.valChange)

    def manualStep(self):
        """Handle changes in value. Change colour if different to set value, set updating values."""
        if self.manuallyUpdated:
            roundVal = round(self.currentDbValue, self.decPlaces)
            if self.decPlaces == 0:
                roundVal = int(roundVal)
            if self.simpleSpin.value() == roundVal:
                self.simpleSpin.setProperty("textColour", "1")
                self.manuallyUpdated = False
                self.simpleSpin.style().polish(self.simpleSpin)
        else:
            self.simpleSpin.setProperty("textColour", "2")
            self.manuallyUpdated = True
            self.simpleSpin.style().polish(self.simpleSpin)
        return 0

    def setEnabled(self, bool):
        self.simpleSpin.setEnabled(bool)
        self.simpleSpin.setProperty("bgColour", str(int(bool)))
        self.simpleSpin.setProperty("textColour", str(int(bool)))
        self.simpleSpin.style().polish(self.simpleSpin)

    def update_value(self, db):
        if self.tag == "":
            a = 1  # do nothing
        else:
            newVal = db[self.tag]
            if self.manuallyUpdated:
                a = 1  # do nothing
            else:
                self.currentDbValue = newVal
                self.simpleSpin.setValue(newVal)
                self.simpleSpin.setProperty("textColour", "1")
                self.simpleSpin.style().polish(self.simpleSpin)

    def insertWidget(self, widget, position):
        self.insertedWidget = widget
        self.widgetList.insert(position, widget)
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        # newLayout = QtWidgets.QHBoxLayout()
        for widget in self.widgetList:
            self.layout.addWidget(widget)
        self.setLayout(self.layout)

    def get_value(self):
        return self.simpleSpin.value()

    def set_value(self, value):
        self.simpleSpin.setValue(value)
        self.simpleSpin.setProperty("textColour", "1")
        self.simpleSpin.style().polish(self.simpleSpin)
        return 0

    def set_maximum(self, max):
        self.max = max
        if self.simpleSpin.value() > self.max:
            self.simpleSpin.set_value(max)
        self.simpleSpin.setRange(self.min, self.max)

    def set_minimum(self, min):
        self.min = min
        if self.simpleSpin.value() < self.min:
            self.simpleSpin.stepBy(self.min - self.simpleSpin.value())
        self.simpleSpin.setRange(self.min, self.max)