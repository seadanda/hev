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

    # a signal for each handler, so the UI knows which values were updated
    ExpertSend = QtCore.Signal()
    ModeSend = QtCore.Signal()
    PersonalSend = QtCore.Signal()
    ClinicalSend = QtCore.Signal()

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        self.handler = None

        # list widget displays the changes to be sent to MCU in human readable way
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


    def populatePopup(self, handlerWidget, messageList):
        """One popup is used for all the handlers. It is populated when called by a particular handler"""
        self.handler = handlerWidget
        self.listWidget.clear()
        if messageList == []:
            messageList = ["no values were set"]
        for item in messageList:
            listItem = QtWidgets.QListWidgetItem(item)
            listItem.setFlags(QtCore.Qt.NoItemFlags)
            self.listWidget.addItem(listItem)
        # adjust size according to list contents
        self.listWidget.setFixedHeight(
            self.listWidget.sizeHintForRow(0) * self.listWidget.count() + 10
        )
        self.listWidget.setFixedWidth(
            self.listWidget.sizeHintForColumn(0) * self.listWidget.count()
        )

        self.listWidget.update()
        self.update()
        return 0

    def ok_button_pressed(self):
        """Emit signal to connect with handler corresponding to editted values."""
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
    """A widget displaying an individual command confirmation from the MCU. Is contained in confirmPopup"""

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

        # create timer to handle timeout
        self.timer = QtCore.QTimer()
        self.timer.setInterval(10000)
        self.timer.timeout.connect(self.confirmTimeout)
        self.timer.start()

    def confirmTimeout(self):
        """Widget should expire after a defined time"""
        self.parent().confirmDict.pop(
            self.confirmMessage.replace("/", "_").replace("-", "_") # - and / are not used in dictionary keys
        )
        self.setParent(None) # delete self


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
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.adjustSize) # container needs to adjust to a new number of confirmWidgets
        self.timer.start()

    def addConfirmation(self, confirmMessage):
        """Add a confirmation to the popup. Triggered when UI receives a confirmation from the microcontroller"""
        self.confirmDict[confirmMessage] = confirmWidget(
            self.NativeUI, confirmMessage
        )  # record in dictionary so it can be accessed and deleted
        self.vlayout.addWidget(self.confirmDict[confirmMessage])
        return 0

    def location_on_window(self):
        """Places confirmWidgets at the top center of the screen"""
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        # widget = self.geometry()
        x = screen.width() - screen.width() / 2
        y = 0  # screen.height() - widget.height()
        self.move(x, y)
        return 0
