from os import path

from PySide2 import QtGui, QtWidgets
from PySide2.QtCore import QSize


class TabPageButtons(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(TabPageButtons, self).__init__(*args, **kwargs)

        self.__iconsize = QSize(50, 50)
        self.__iconpath = "hev-display/assets/svg/"  # TODO better path

        layout = QtWidgets.QVBoxLayout()

        self.button_signin = QtWidgets.QPushButton()
        self.button_alarms = QtWidgets.QPushButton()
        self.button_fancon = QtWidgets.QPushButton()
        self.button_cntrls = QtWidgets.QPushButton()

        self.__buttons = [
            self.button_signin,
            self.button_alarms,
            self.button_fancon,
            self.button_cntrls,
        ]
        self.__icons = [
            "user-md-solid.svg",
            "exclamation-triangle-solid.svg",
            "fan-solid.svg",
            "sliders-h-solid.svg",
        ]

        for button, icon in zip(self.__buttons, self.__icons):
            button.setIcon(QtGui.QIcon(path.join(self.__iconpath, icon)))
            button.setIconSize(self.__iconsize)
            layout.addWidget(button)

        self.setLayout(layout)
