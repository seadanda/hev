from PySide2 import QtWidgets, QtGui, QtCore


class SetConfirmPopup(
    QtWidgets.QDialog
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, setList, *args, **kwargs):
        super().__init__(*args, **kwargs)

        listWidget = QtWidgets.QListWidget()
        for item in setList:
            listWidget.addItem(item)

        buttonHLayout = QtWidgets.QHBoxLayout()
        self.okButton = QtWidgets.QPushButton()
        self.okButton.setIcon(QtGui.QIcon("hev-display/svg/check-solid.svg"))
        self.okButton.setStyleSheet("background-color:white; border-radius:4px ")
        buttonHLayout.addWidget(self.okButton)

        self.cancelButton = QtWidgets.QPushButton()
        self.cancelButton.setIcon(QtGui.QIcon("figures/pic2.jpg"))
        self.cancelButton.setStyleSheet("background-color:white; border-radius:4px ")
        self.cancelButton.pressed.connect(self.cancel_button_pressed)
        buttonHLayout.addWidget(self.cancelButton)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(listWidget)
        vlayout.addLayout(buttonHLayout)

        self.setLayout(vlayout)
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint
        )  # no window title

    def cancel_button_pressed(self):
        self.close()
