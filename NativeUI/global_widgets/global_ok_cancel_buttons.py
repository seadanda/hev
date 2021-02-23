from PySide2 import QtWidgets, QtGui, QtCore
import os


class okButton(
    QtWidgets.QPushButton
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        iconpath_check = os.path.join(NativeUI.iconpath, "check-solid.png")
        self.setIcon(QtGui.QIcon(iconpath_check))
        self.setStyleSheet(
            "background-color: " + NativeUI.colors["background-enabled"].name() + ";"
            "border-radius:4px "
        )


class cancelButton(
    QtWidgets.QPushButton
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        iconpath_cross = os.path.join(NativeUI.iconpath, "times-solid.png")
        self.setIcon(QtGui.QIcon(iconpath_cross))
        self.setStyleSheet(
            "background-color: " + NativeUI.colors["background-enabled"].name() + ";"
            "border-radius:4px "
        )
