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

# from global_widgets.global_ok_cancel_buttons import okButton, cancelButton
import sys
import os


class SetConfirmPopup(QtWidgets.QDialog):
    """Popup called when user wants to send new values to microcontroller.
    This popup shows changes and asks for confirmation"""

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setStyleSheet("background-color:rgba(255,0,255,50%);color:rgb(0,255,0)")

        self.NativeUI = NativeUI

        #elf.parentTemplate = parentTemplate
        #self.commandList = commandList

        self.listWidget = QtWidgets.QListWidget()

        # size = QtWidgets.QSize()
        #        s.setHeight(super(qtWidgets.QListWidget,listWidget).sizeHint().height())
        # listWidget.setStyleSheet('background-color:black;font:16pt; color:white; border:none')
        # self.setWindowOpacity(0.1)
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.listWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.listWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.listWidget.setFixedHeight(
        #     self.listWidget.sizeHintForRow(0) * self.listWidget.count() + 10
        # )

        buttonHLayout = QtWidgets.QHBoxLayout()

        self.okButton = OkButtonWidget(self.NativeUI)
        self.okButton.setEnabled(True)
        self.okButton.pressed.connect(self.ok_button_pressed)
        buttonHLayout.addWidget(self.okButton)

        self.cancelButton = CancelButtonWidget(self.NativeUI)
        self.cancelButton.setEnabled(True)
        self.cancelButton.pressed.connect(self.cancel_button_pressed)
        buttonHLayout.addWidget(self.cancelButton)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self.listWidget)
        vlayout.addLayout(buttonHLayout)

        self.setLayout(vlayout)
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint
        )  # no window title
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setWindowOpacity(0.5)

    def populatePopup(self, messageList, commandList ):
        if messageList == []:
            messageList = ["no values were set"]
        for item in messageList:
            listItem = QtWidgets.QListWidgetItem(item)
            listItem.setFlags(QtCore.Qt.NoItemFlags)
            self.listWidget.addItem(listItem)
        self.listWidget.setFixedHeight(
            self.listWidget.sizeHintForRow(0) * self.listWidget.count() + 10
        )
        self.listWidget.setFixedWidth(self.listWidget.sizeHintForColumn(0) * self.listWidget.count())

        self.listWidget.update()
        self.update()
        self.commandList = commandList

    def clearPopup(self):
        self.listWidget.clear()
        self.commandList = []


    def ok_button_pressed(self):
        """Send commands when ok button is clicked"""
        #self.parentTemplate.liveUpdating = True
        for command in self.commandList:
            self.NativeUI.q_send_cmd(*command)
        self.close()
        return 0

    def cancel_button_pressed(self):
        """Close popup when cancel button is clicked"""
        self.close()
        return 0


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


class confirmPopup(QtWidgets.QWidget):
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

        self.location_on_window()
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.Dialog
            | QtCore.Qt.WindowStaysOnTopHint
        )  # no window title

        self.setStyleSheet("background-color:green;")

        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)  # just faster than 60Hz
        self.timer.timeout.connect(self.adjustSize)
        self.timer.start()

    def addConfirmation(self, confirmMessage):
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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widg = SetConfirmPopup(
        None, ["test text", "test", "test", "tregfdgdfgd", "experiment"]
    )
    widg.show()
    sys.exit(app.exec_())
