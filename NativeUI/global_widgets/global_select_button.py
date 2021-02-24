from PySide2 import QtWidgets, QtGui, QtCore


class selectorButton(QtWidgets.QPushButton):
    def __init__(self, NativeUI, *args, **kwargs):
        super(selectorButton, self).__init__(*args, **kwargs)
        fontsize = 20

        style = (
            "QPushButton{"
            "font: " + str(fontsize) + "pt;"
            "}"
            "QPushButton[selected='0']{"
            "font: " + str(fontsize) + "pt;"
            "color: " + NativeUI.colors["foreground"].name() + ";"
            "background-color: " + NativeUI.colors["background-enabled"].name() + ";"
            "border:none"
            "}"
            "QPushButton[selected='1']{"
            "font: " + str(fontsize) + "pt;"
            "color: " + NativeUI.colors["background"].name() + ";"
            "background-color: " + NativeUI.colors["foreground-disabled"].name() + ";"
            "border:none"
            "}"
        )

        self.setStyleSheet(style)
        self.setProperty("selected", "0")
