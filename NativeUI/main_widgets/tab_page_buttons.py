import os

from PySide2 import QtGui, QtWidgets
from PySide2.QtCore import QSize


class TabPageButtons(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(TabPageButtons, self).__init__(*args, **kwargs)

        self.__iconsize = QSize(50, 50)
        self.__iconpath = self.__find_icons()

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
            button.setIcon(QtGui.QIcon(os.path.join(self.__iconpath, icon)))
            button.setIconSize(self.__iconsize)
            layout.addWidget(button)

        self.setLayout(layout)

        self.button_signin.pressed.connect(self.__signin_pressed)
        self.button_alarms.pressed.connect(self.__alarms_pressed)
        self.button_cntrls.pressed.connect(self.__cntrls_pressed)

    def __signin_pressed(self):
        self.parent().parent().stack.setCurrentWidget(self.parent().parent().main_view)

    def __cntrls_pressed(self):
        self.parent().parent().stack.setCurrentWidget(
            self.parent().parent().settings_view
        )

    def __alarms_pressed(self):
        self.parent().parent().stack.setCurrentWidget(
            self.parent().parent().alarms_view
        )

    def __find_icons(self):
        initial_path = "hev-display/assets/svg/"
        # assume we're in the root directory
        temp_path = os.path.join(os.getcwd(), initial_path)
        if os.path.isdir(temp_path):
            return temp_path

        # assume we're one folder deep in the root directory
        temp_path = os.path.join("..", temp_path)
        if os.path.isdir(temp_path):
            return temp_path

        walk = os.walk(os.path.join(os.getcwd(), ".."))
        for w in walk:
            if "svg" in w[1]:
                temp_path = os.path.join(os.path.normpath(w[0]), "svg")
                return temp_path

        raise Exception(FileNotFoundError, "could not locate svg icon files")


if __name__ == "__main__":
    y = QtWidgets.QApplication()
    x = TabPageButtons()
