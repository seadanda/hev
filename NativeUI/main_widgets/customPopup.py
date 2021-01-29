from PySide2 import QtWidgets, QtGui, QtCore
import sys


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
                                        }"""
        )
        self.lineEdit.setProperty("colour", "1")
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit.saveVal = self.lineEdit.text()
        self.lineEdit.setValidator(
            QtGui.QDoubleValidator(0.0, 100.0, 2)
        )  # ensures only doubles can be typed
        # self.lineEdit.installEventFilter(
        #    self
        # )  # override to respond to key press(enter and esc) defined in eventFilter
        grid.addWidget(self.lineEdit, 0, 0, 1, 2)

        self.okButton = QtWidgets.QPushButton()
        self.okButton.setIcon(QtGui.QIcon("hev-display/svg/check-solid.svg"))
        self.okButton.setStyleSheet("background-color:white; border-radius:4px ")
        grid.addWidget(self.okButton, 1, 0)

        self.cancelButton = QtWidgets.QPushButton()
        self.cancelButton.setIcon(QtGui.QIcon("figures/pic2.jpg"))
        self.cancelButton.setStyleSheet("background-color:white; border-radius:4px ")
        grid.addWidget(self.cancelButton, 1, 1)

        self.setLayout(grid)
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint
        )  # no window title

    def getValue(self):
        return self.lineEdit.text()

    def setTextColour(self, option):
        self.lineEdit.style().unpolish(self.lineEdit)
        self.lineEdit.style().polish(self.lineEdit)
        self.lineEdit.setProperty("colour", option)

    def setTextWhite(self):
        self.lineEdit.style().unpolish(self.lineEdit)
        self.lineEdit.style().polish(self.lineEdit)
        self.lineEdit.setProperty("colour", "2")

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.KeyPress and source is self.lineEdit:
            if event.text() == "\r":  # enter
                self.okButton.click()
                return True
            elif event.text() == "\x1b":  # Escape button
                self.cancelButton.click()
                return True
            else:
                return False  # think False means process normally


# def main():
#     if not QtWidgets.QApplication.instance():
#         app = QtWidgets.QApplication(sys.argv)
#     else:
#         app = QtWidgets.QApplication.instance()
#         # app = QtWidgets.QApplication(sys.argv)
#     main = customPopup()
#     main.show()
#     # second = gen.Ui_Dialog()
#     # second.show()
#     sys.exit(app.exec_())


# if __name__ == "__main__":
#     print("running")
#     main()
