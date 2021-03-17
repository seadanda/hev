#!/usr/bin/env python3

"""
global_sendconfirm_popup.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

from PySide2 import QtCore, QtGui, QtWidgets
import sys
import os


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
        self.parent().confirmDict.pop(self.confirmMessage)
        self.setParent(None)


class confirmPopup(QtWidgets.QWidget):
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
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog
        )  # no window title

        self.setStyleSheet("background-color:green;")

        self.shadow = QtWidgets.QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(10)
        self.shadow.setYOffset(10)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.adjustSize)
        self.timer.start()

    def addConfirmation(self, confirmMessage):
        self.confirmDict[confirmMessage] = confirmWidget(self.NativeUI, confirmMessage)
        self.vlayout.addWidget(self.confirmDict[confirmMessage])

    def location_on_window(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        # widget = self.geometry()
        x = screen.width() - screen.width() / 2
        y = 0  # screen.height() - widget.height()
        self.move(x, y)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widg = confirmPopup()
    widg.addConfirmation("new confirmation")
    widg.addConfirmation("new confirmation2")
    widg.show()
    sys.exit(app.exec_())
