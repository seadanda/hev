from PySide2 import QtWidgets, QtGui, QtCore
import sys


def catch_exceptions(t, val, tb):
    # QtWidgets.QMessageBox.critical(None,
    #                                "An exception was raised",
    #                                "Exception type: {}".format(t))
    old_hook(t, val, tb)


old_hook = sys.excepthook
sys.excepthook = catch_exceptions


class customPopup(
    QtWidgets.QDialog
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self):
        super().__init__()

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(1)

        self.setStyleSheet("border-radius:4px; background-color:black")

        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setText("4")
        self.lineEdit.setStyleSheet(
            """QLineEdit{font: 16pt;
                                            background-color:white;
                                            border-radius:4px }
                                        QLineEdit[colour = "0"]{
                                            color:green
                                        }
                                        QLineEdit[colour = "1"]{
                                            color:rgb(144,231,211);
                                        }
                                        QLineEdit[colour = "2"]{
                                            color:red
                                        }

                                            """
        )
        self.lineEdit.setProperty("colour", "1")
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit.saveVal = self.lineEdit.text()
        self.lineEdit.setValidator(
            QtGui.QDoubleValidator(0.0, 100.0, 2)
        )  # ensures only doubles can be typed
        self.lineEdit.installEventFilter(
            self
        )  # override to respond to key press(enter and esc) defined in eventFilter
        grid.addWidget(self.lineEdit, 0, 0, 1, 2)

        self.okButton = QtWidgets.QPushButton()
        self.okButton.setIcon(QtGui.QIcon("figures/pic1.png"))
        self.okButton.setStyleSheet("background-color:white; border-radius:4px ")
        grid.addWidget(self.okButton, 1, 0)

        self.cancelButton = QtWidgets.QPushButton()
        self.cancelButton.setIcon(QtGui.QIcon("figures/pic2.jpg"))
        self.cancelButton.setStyleSheet("background-color:white; border-radius:4px ")
        grid.addWidget(self.cancelButton, 1, 1)

        self.setLayout(grid)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # no window title
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        # self.show()

    def getValue(self):
        return self.lineEdit.text()

    def setTextRed(self):
        # self.lineEdit.setStyleSheet(self.boxStyleString + self.upArrowStyleString + self.downArrowStyleString + self.upArrowPressedStyleString + self.downArrowPressedStyleString)
        self.lineEdit.style().unpolish(self.lineEdit)
        self.lineEdit.style().polish(self.lineEdit)
        self.lineEdit.setProperty("colour", "0")

    def setTextWhite(self):
        # self.lineEdit.setStyleSheet(boxStyleString + upArrowStyleString + downArrowStyleString + upArrowPressedStyleString + downArrowPressedStyleString)
        self.lineEdit.style().unpolish(self.lineEdit)
        self.lineEdit.style().polish(self.lineEdit)
        self.lineEdit.setProperty("colour", "2")

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.KeyPress and source is self.lineEdit:
            if event.text() == "\r":
                self.okButton.click()
                return True
            elif event.text() == "\x1b":
                self.cancelButton.click()
                return True
            # elif not str.isnumeric(event.text()):
            #     print('not numeric')
            #
            #     return False
            else:
                return False  # return False meansstandard processing


def main():
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
        # app = QtWidgets.QApplication(sys.argv)
    main = customPopup()
    main.show()
    # second = gen.Ui_Dialog()
    # second.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    print("running")
    main()
