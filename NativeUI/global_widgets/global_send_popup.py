#!/usr/bin/env python3

"""
global_send_popup.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

from PySide2 import QtWidgets, QtGui, QtCore
from widget_library.ok_cancel_buttons_widget import OkButtonWidget, CancelButtonWidget
from widget_library.expert_handler import ExpertHandler
from mode_widgets.personal_handler import PersonalHandler
from mode_widgets.mode_handler import ModeHandler
from mode_widgets.clinical_handler import ClinicalHandler
import logging


# from global_widgets.global_ok_cancel_buttons import okButton, cancelButton
import sys
import os


class SetConfirmPopup(QtWidgets.QDialog):
    """Popup called when user wants to send new values to microcontroller.
    This popup shows changes and asks for confirmation"""

    ExpertSend = QtCore.Signal()
    ModeSend = QtCore.Signal()
    PersonalSend = QtCore.Signal()
    ClinicalSend = QtCore.Signal()

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        self.handler = None

        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        buttonHLayout = QtWidgets.QHBoxLayout()

        self.okButton = OkButtonWidget(self.NativeUI)
        self.okButton.setEnabled(True)
        self.okButton.pressed.connect(self.ok_button_pressed)
        buttonHLayout.addWidget(self.okButton)

        self.cancelButton = CancelButtonWidget(self.NativeUI)
        self.cancelButton.setEnabled(True)
        buttonHLayout.addWidget(self.cancelButton)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self.listWidget)
        vlayout.addLayout(buttonHLayout)

        self.setLayout(vlayout)
        # self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        # self.setWindowOpacity(0.5)

    def populatePopup(self, handlerWidget, messageList):
        self.handler = handlerWidget
        self.clearPopup()
        if messageList == []:
            messageList = ["no values were set"]
        for item in messageList:
            listItem = QtWidgets.QListWidgetItem(item)
            listItem.setFlags(QtCore.Qt.NoItemFlags)
            self.listWidget.addItem(listItem)
        self.listWidget.setFixedHeight(
            self.listWidget.sizeHintForRow(0) * self.listWidget.count() + 10
        )
        self.listWidget.setFixedWidth(
            self.listWidget.sizeHintForColumn(0) * self.listWidget.count()
        )

        self.listWidget.update()
        self.update()

    def clearPopup(self):
        self.listWidget.clear()
        self.commandList = []

    def ok_button_pressed(self):
        """Send commands when ok button is clicked"""
        # self.parentTemplate.liveUpdating = True
        if self.handler is None:
            logging.error("Popup ok_button_pressed called before popupatePopup")
            return 1

        if isinstance(self.handler, ExpertHandler):
            self.ExpertSend.emit()
        elif isinstance(self.handler, ModeHandler):
            self.ModeSend.emit()
        elif isinstance(self.handler, PersonalHandler):
            self.PersonalSend.emit()
        elif isinstance(self.handler, ClinicalHandler):
            self.ClinicalSend.emit()
        else:
            logging.warning("Unrecognised handler type: %s", type(self.handler))
        return 0

    # def cancel_button_pressed(self):
    #     """Close popup when cancel button is clicked"""
    #     print("CANCEL BUTTON PRESSED")
    #     # self.close()
    #     return 0


class confirmWidget(QtWidgets.QWidget):
    def __init__(self, NativeUI, confirmMessage, *args, **kwargs):
        super(confirmWidget, self).__init__(*args, **kwargs)
        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.setSpacing(0)
        self.hlayout.setMargin(0)
        self.confirmMessage = confirmMessage

        iconLabel = QtWidgets.QLabel()
        iconpath_check = os.path.join(NativeUI.iconpath, "exclamation-circle-solid.png")
        pixmap = QtGui.QPixmap(iconpath_check).scaledToHeight(40)
        iconLabel.setPixmap(pixmap)
        self.hlayout.addWidget(iconLabel)

        textLabel = QtWidgets.QLabel()
        textLabel.setText(self.confirmMessage)
        textLabel.setFixedHeight(40)
        textLabel.setFixedWidth(400)
        textLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.hlayout.addWidget(textLabel)

        self.setLayout(self.hlayout)
        self.setFixedHeight(50)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(10000)
        self.timer.timeout.connect(self.confirmTimeout)
        self.timer.start()

    def confirmTimeout(self):
        self.parent().confirmDict.pop(
            self.confirmMessage.replace("/", "_").replace("-", "_")
        )
        self.setParent(None)


class confirmPopup(QtWidgets.QDialog):
    """Popup when a command is confirmed by microcontroller.
    This popup is a frame containing a confirmWidget object for
    each successful command."""

    def __init__(self, NativeUI, *args, **kwargs):
        super(confirmPopup, self).__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        self.confirmDict = {}
        self.vlayout = QtWidgets.QVBoxLayout()
        self.vlayout.setSpacing(0)
        self.vlayout.setMargin(0)
        self.setLayout(self.vlayout)

        self.setStyleSheet("background-color:green;")
        self.location_on_window()
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.Dialog
            | QtCore.Qt.WindowStaysOnTopHint
        )  # no window title

        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)  # just faster than 60Hz
        self.timer.timeout.connect(self.adjustSize)
        self.timer.start()

    def addConfirmation(self, confirmMessage):
        print('adding confirmation')
        """Add a confirmation to the popup. Triggered when UI receives a confirmation from the microcontroller"""
        self.confirmDict[confirmMessage] = confirmWidget(
            self.NativeUI, confirmMessage
        )  # record in dictionary so it can be accessed and deleted
        self.vlayout.addWidget(self.confirmDict[confirmMessage])
        return 0

    def location_on_window(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        # widget = self.geometry()
        x = screen.width() - screen.width() / 2
        y = 0  # screen.height() - widget.height()
        self.move(x, y)
