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

from PySide2 import QtCore, QtGui, QtWidgets
from global_widgets.global_ok_cancel_buttons import okButton, cancelButton
import time


class timerConfirmPopup(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super(timerConfirmPopup, self).__init__(*args, **kwargs)

        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint
        )  # ensures focus is not stolen by alarm or confirmation

        self.setStyleSheet(
            "background-color: " + NativeUI.colors["background-enabled"].name() + ";"
            "color: " + NativeUI.colors["foreground"].name() + ";"
            "border-color: " + NativeUI.colors["foreground"].name() + ";"
            "border:none"
        )

        self.stack = QtWidgets.QStackedWidget()

        vlayout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel("progressing")
        vlayout.addWidget(self.label)

        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMaximum(3000)
        self.progressBar.setFormat("")
        # self.progressBar
        vlayout.addWidget(self.progressBar)
        self.progressWidg = QtWidgets.QWidget()
        self.progressWidg.setLayout(vlayout)
        self.stack.addWidget(self.progressWidg)
        # self.setLayout(vlayout)

        self.completeLayout = QtWidgets.QVBoxLayout()
        self.completeLabel = QtWidgets.QLabel("confirm it")

        buttonLayout = QtWidgets.QHBoxLayout()
        self.okButton = okButton(NativeUI)
        buttonLayout.addWidget(self.okButton)
        self.cancelButton = cancelButton(NativeUI)
        buttonLayout.addWidget(self.cancelButton)

        self.completeLayout.addWidget(self.completeLabel)
        self.completeLayout.addLayout(buttonLayout)

        self.completeWidg = QtWidgets.QWidget()
        self.completeWidg.setLayout(self.completeLayout)
        self.stack.addWidget(self.completeWidg)

        stackLayout = QtWidgets.QVBoxLayout()
        stackLayout.addWidget(self.stack)
        self.setLayout(stackLayout)


class holdButton(QtWidgets.QPushButton):
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
        self.now = time.time()
        if self.state == 0:
            # print('pressed')
            self.popUp.show()
            self.initial = time.time()
        if self.isDown():
            if self.pressTime == self.timeOut:
                self.complete = True
                print(self.now - self.initial)
                self.popUp.stack.setCurrentWidget(self.popUp.completeWidg)

            self.pressTime = self.pressTime + self.timeStep
            self.state = 1
            self.popUp.progressBar.setValue(self.pressTime)
            self.popUp.progressBar.update()
        else:
            self.pressTime = 0
            print("aa")
            print(self.complete)
            print(self.state)
            if self.state == 1:
                print("released")
            if not self.complete:
                self.popUp.close()
            self.state = 0

    def okButtonPressed(self):
        self.NativeUI.q_send_cmd("GENERAL", self.text())
        self.closePopup()

    def closePopup(self):
        self.popUp.progressBar.setValue(0)
        self.popUp.stack.setCurrentWidget(self.popUp.progressWidg)
        self.popUp.close()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widg = holdButton("Standby")
    widg.show()
    sys.exit(app.exec_())
