from PySide2 import QtWidgets, QtGui, QtCore
from global_widgets.global_ok_cancel_buttons import okButton, cancelButton
import sys
import os


class SetConfirmPopup(
    QtWidgets.QDialog
):  # chose QWidget ov   er QDialog family because easier to modify
    def __init__(self, parentTemplate, NativeUI, setList, commandList, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setStyleSheet("background-color:rgba(255,0,255,50%);color:rgb(0,255,0)")

        # if NativeUI is None:
        #     iconpath = "hev-display/svg/check-solid.svg"
        # else:
        #     iconpath_check = os.path.join(NativeUI.iconpath, "check-solid.png")
        #     iconpath_cross = os.path.join(NativeUI.iconpath, "times-solid.png")
        self.NativeUI = NativeUI
        if setList == []:
            setList = ["no values were set"]
        self.parentTemplate = parentTemplate
        self.commandList = commandList

        listWidget = QtWidgets.QListWidget()
        for item in setList:
            listItem = QtWidgets.QListWidgetItem(item)
            listItem.setFlags(QtCore.Qt.NoItemFlags)
            listWidget.addItem(listItem)
        # size = QtWidgets.QSize()
        #        s.setHeight(super(qtWidgets.QListWidget,listWidget).sizeHint().height())
        # listWidget.setStyleSheet('background-color:black;font:16pt; color:white; border:none')
        # self.setWindowOpacity(0.1)
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        listWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        listWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        listWidget.setFixedHeight(
            listWidget.sizeHintForRow(0) * listWidget.count() + 10
        )
        listWidget.setFixedWidth(listWidget.sizeHintForColumn(0) * listWidget.count())

        buttonHLayout = QtWidgets.QHBoxLayout()

        self.okButton = okButton(self.NativeUI)
        self.okButton.pressed.connect(self.ok_button_pressed)
        buttonHLayout.addWidget(self.okButton)

        self.cancelButton = cancelButton(self.NativeUI)
        self.cancelButton.pressed.connect(self.cancel_button_pressed)
        buttonHLayout.addWidget(self.cancelButton)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(listWidget)
        vlayout.addLayout(buttonHLayout)

        self.setLayout(vlayout)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # no window title
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setWindowOpacity(0.5)

    def ok_button_pressed(self):
        self.parentTemplate.liveUpdating = True
        for command in self.commandList:
            self.NativeUI.q_send_cmd(*command)
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
