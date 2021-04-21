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

    def __init__(self, NativeUI):
        super().__init__()
        self.lineEdit().installEventFilter(self)
        self.editable = True

        self.popUp = TypeValuePopup(NativeUI)
        self.popUp.okButton.clicked.connect(self.okButtonPressed)
        self.popUp.cancelButton.clicked.connect(self.cancelButtonPressed)

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

    def eventFilter(self, source, event):
        """Overrides event filter to implement response to double click """
        if (
            source is self.lineEdit()
            and event.type() == QtCore.QEvent.MouseButtonDblClick
        ):
            if not self.editable:
                return
            self.popUp.lineEdit.setText(str(self.value()))
            self.popUp.show()
            return True
        return False


class labelledSpin(QtWidgets.QWidget):
    """Combines signalling spin box with information relevant to its layout and to handle value updates.
    It is created by an information array which indicates labels, units, command type and code for value setting,
    and the range of permitted values"""

    def __init__(self, NativeUI, infoArray, *args, **kwargs):
        super(labelledSpin, self).__init__(*args, **kwargs)
        # print(infoArray)
        # a = ReadbackFormat()
        # print(a)

        self.NativeUI = NativeUI
        self.cmd_type, self.cmd_code = "", ""
        self.min, self.max, self.step = 0, 10000, 0.3
        self.initVal = 1
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
        textStyle = "color:white;" "font-size: " + NativeUI.text_size + ";"

        # if self.label != "":
        self.nameLabel = QtWidgets.QLabel(self.label)
        self.nameLabel.setStyleSheet(textStyle)
        self.nameLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.simpleSpin = signallingSpinBox(NativeUI)
        self.simpleSpin.setValue(self.initVal)
        self.simpleSpin.setRange(self.min, self.max)
        self.simpleSpin.setSingleStep(self.step)
        self.simpleSpin.setDecimals(self.decPlaces)
        self.simpleSpin.setStyleSheet(
            "QDoubleSpinBox{"
            "    width:100px;"  # TODO: unhardcode
            "    font:" + NativeUI.text_size + ";"
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
            "background-color:white;"
            "color:black;"
            "}"
            "QDoubleSpinBox::down-button{"
            "width:20px;"
            "height:20px; "
            "border:none;"
            "}"
        )
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

    # def update_readback_value(self):
    #     newVal = self.NativeUI.get_db("readback")
    #     if newVal == {} or self.manuallyUpdated:
    #         a = 1  # do nothing
    #     else:
    #         self.simpleSpin.setValue(newVal[self.tag])
    #         self.simpleSpin.setProperty("textColour", "0")
    #         self.simpleSpin.style().polish(self.simpleSpin)

    # def update_targets_value(self):
    #     newVal = self.NativeUI.get_db("targets")
    #     if (newVal == {}) or (self.tag == "") or self.manuallyUpdated:
    #         a = 1  # do nothing
    #     else:
    #         self.simpleSpin.setValue(newVal[self.tag])
    #         self.simpleSpin.setProperty("textColour", "0")
    #         self.simpleSpin.style().polish(self.simpleSpin)

    # def update_personal_value(self):
    #     newVal = self.NativeUI.get_db("personal")
    #     if (newVal == {}) or (self.tag == ""):
    #         a = 1  # do nothing
    #     else:
    #         self.simpleSpin.setValue(newVal[self.tag])
    #         self.simpleSpin.setProperty("textColour", "0")
    #         self.simpleSpin.style().polish(self.simpleSpin)

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
