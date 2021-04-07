#!/usr/bin/env python3

"""
tab_hold_buttons.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

import logging
from PySide2 import QtCore, QtGui, QtWidgets
from widget_library.ok_cancel_buttons_widget import OkButtonWidget, CancelButtonWidget

# from global_widgets.global_ok_cancel_buttons import okButton, cancelButton
import time


class timerConfirmPopup(QtWidgets.QWidget):
    """Popup when start stop standby buttons are pressed. Counts a certain amount of time before switching on,
    showing a progress bar meanwhile"""

    def __init__(self, NativeUI, *args, **kwargs):
        super(timerConfirmPopup, self).__init__(*args, **kwargs)

        self.setAttribute(
            QtCore.Qt.WA_ShowWithoutActivating
        )  # keep the main page activated to maintain button hold
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint
        )  # ensures focus is not stolen by alarm or confirmation

        self.setStyleSheet(
            "background-color: "
            + NativeUI.colors["button_background_enabled"].name()
            + ";"
            "color: " + NativeUI.colors["button_foreground_disabled"].name() + ";"
            "border:none"
        )

        self.stack = QtWidgets.QStackedWidget()

        # Define progress bar
        vlayout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel("progressing")
        vlayout.addWidget(self.label)

        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMaximum(3000)
        self.progressBar.setFormat("")

        vlayout.addWidget(self.progressBar)
        self.progressWidg = QtWidgets.QWidget()
        self.progressWidg.setLayout(vlayout)
        self.stack.addWidget(self.progressWidg)

        # Define confirmation message and buttons
        self.completeLayout = QtWidgets.QVBoxLayout()
        self.completeLabel = QtWidgets.QLabel("confirm it")

        buttonLayout = QtWidgets.QHBoxLayout()
        self.okButton = OkButtonWidget(NativeUI)
        buttonLayout.addWidget(self.okButton)
        self.cancelButton = CancelButtonWidget(NativeUI)
        self.okButton.setEnabled(True)
        self.cancelButton.setEnabled(True)
        buttonLayout.addWidget(self.cancelButton)

        self.completeLayout.addWidget(self.completeLabel)
        self.completeLayout.addLayout(buttonLayout)

        self.completeWidg = QtWidgets.QWidget()
        self.completeWidg.setLayout(self.completeLayout)
        self.stack.addWidget(self.completeWidg)

        # set layout
        stackLayout = QtWidgets.QVBoxLayout()
        stackLayout.addWidget(self.stack)
        self.setLayout(stackLayout)

        # place popup in screen
        qtRectangle = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        # self.move(QtGui.QApplication.desktop().screen().rect().center() - self.rect().center())


class holdButton(QtWidgets.QPushButton):
    """Subclass push button to count press time and update progress bar. handleClick() is overridden.
    Popup with progress bar appears on click, fills as button is held."""

    def __init__(self, NativeUI, *args, **kwargs):
        super(holdButton, self).__init__(*args, **kwargs)

        self.NativeUI = NativeUI

        self.timeOut = 3000
        self.timeStep = 60

        self.setAutoRepeat(True)
        self.setAutoRepeatDelay(self.timeStep)
        self.setAutoRepeatInterval(self.timeStep)

        self.pressTime = 0
        self.state = 0
        self.complete = False

        self.clicked.connect(self.handleClick)

        self.popUp = timerConfirmPopup(NativeUI)

        self.popUp.okButton.pressed.connect(self.okButtonPressed)
        self.popUp.cancelButton.pressed.connect(self.closePopup)

    def handleClick(self):
        """Over ride handleClick to count button hold time.
        Shows popup, sets progress bar, and updates it"""
        self.now = time.time()
        if self.state == 0:
            # print('pressed')
            self.popUp.show()
            self.initial = time.time()
        if self.isDown():
            if self.pressTime == self.timeOut:
                self.complete = True
                logging.debug(self.now - self.initial)
                self.popUp.stack.setCurrentWidget(self.popUp.completeWidg)

            self.pressTime = self.pressTime + self.timeStep
            self.state = 1
            self.popUp.progressBar.setValue(self.pressTime)
            self.popUp.progressBar.update()
        else:
            self.pressTime = 0
            logging.debug(
                "holdButton.handleClick():\nself.complete: %s\nself.state: %s"
                % (self.complete, self.state)
            )
            if self.state == 1:
                logging.debug("holdButton released")
            if not self.complete:
                self.popUp.close()
            self.state = 0

    def okButtonPressed(self):
        """Respond to ok button press by sending command corresponding to button type"""
        logging.debug(self.text())
        self.NativeUI.q_send_cmd(
            "GENERAL", self.text()
        )  # text is stand stop or standby
        self.closePopup()
        return 0

    def closePopup(self):
        """Reset progress bar and widget stack, and close popup"""
        self.popUp.progressBar.setValue(0)
        self.popUp.stack.setCurrentWidget(self.popUp.progressWidg)
        self.popUp.close()
        return 0


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widg = holdButton("Standby")
    widg.show()
    sys.exit(app.exec_())
