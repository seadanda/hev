from PySide2 import QtWidgets, QtGui, QtCore
import sys
import os


class SetConfirmPopup(
    QtWidgets.QDialog
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, NativeUI, setList, commandList, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("background-color:rgba(255,0,255,50%);color:rgb(0,255,0)")

        if NativeUI is None:
            iconpath = "hev-display/svg/check-solid.svg"
        else:
            iconpath = os.path.join(NativeUI.iconpath, "check-solid.png")

        if setList == []:
            setList = ["no values were set"]
        self.commandList = commandList

        listWidget = QtWidgets.QListWidget()
        for item in setList:
            listWidget.addItem(item)
        # size = QtWidgets.QSize()
        #        s.setHeight(super(qtWidgets.QListWidget,listWidget).sizeHint().height())
        # listWidget.setStyleSheet('background-color:black;font:16pt; color:white; border:none')
        # self.setWindowOpacity(0.1)
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        listWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        listWidget.setFixedHeight(listWidget.sizeHintForRow(0) * listWidget.count())
        # listWidget.setFixedWidth(listWidget.sizeHintForColumn(0)*listWidget.count())

        buttonHLayout = QtWidgets.QHBoxLayout()
        self.okButton = QtWidgets.QPushButton()
        self.okButton.setIcon(QtGui.QIcon(iconpath))
        self.okButton.setStyleSheet("background-color:white; border-radius:4px ")
        buttonHLayout.addWidget(self.okButton)

        self.cancelButton = QtWidgets.QPushButton()
        self.cancelButton.setIcon(QtGui.QIcon("figures/pic2.jpg"))
        # self.cancelButton.setStyleSheet("background-color:white; border-radius:4px ")
        self.cancelButton.pressed.connect(self.cancel_button_pressed)
        buttonHLayout.addWidget(self.cancelButton)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(listWidget)
        vlayout.addLayout(buttonHLayout)

        self.setLayout(vlayout)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # no window title
        # self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setWindowOpacity(0.5)

    def ok_button_pressed(self):
        for command in self.commandList:
            self.NativeUI.q_send_cmd(*command)
            print(command)
        self.close()

    def cancel_button_pressed(self):
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widg = SetConfirmPopup(
        None, ["test text", "test", "test", "tregfdgdfgd", "experiment"]
    )
    widg.show()
    sys.exit(app.exec_())
