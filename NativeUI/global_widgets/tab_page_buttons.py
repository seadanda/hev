import os
from PySide2 import QtGui, QtWidgets
from PySide2.QtCore import QSize
import logging
from global_widgets.tab_start_stop_buttons import TabStartStopStandbyButtons


class TabPageButtons(QtWidgets.QWidget):
    def __init__(self, *args, background_color=None, foreground_color=None, **kwargs):
        super(TabPageButtons, self).__init__(*args, **kwargs)

        self.__iconsize = QSize(80, 80)
        self.__iconpath = self.__find_icons()
        self.__background_color = self.__interpret_color(background_color)
        self.__foreground_color = self.__interpret_color(foreground_color)

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
            "user-md-solid",
            "exclamation-triangle-solid",
            "fan-solid",
            "sliders-h-solid",
        ]
        self.__icons = [ic + ".png" for ic in self.__icons]

        for button, icon in zip(self.__buttons, self.__icons):
            pixmap = QtGui.QPixmap(os.path.join(self.__iconpath, icon))

            # set icon color
            mask = pixmap.mask()
            pixmap.fill(self.__foreground_color)
            pixmap.setMask(mask)

            # set button appearance
            button.setStyleSheet(
                "background-color: " + self.__background_color.name() + ";"
            )

            button.setIcon(QtGui.QIcon(pixmap))
            button.setIconSize(self.__iconsize)
            layout.addWidget(button)

        self.setLayout(layout)

        self.button_signin.pressed.connect(self.__signin_pressed)
        self.button_alarms.pressed.connect(self.__alarms_pressed)
        self.button_fancon.pressed.connect(self.__fancon_pressed)
        self.button_cntrls.pressed.connect(self.__cntrls_pressed)

    def __interpret_color(self, color):
        if color is None:
            logging.warning("No color provided for TabPageButtons")
            return QtGui.QColor.fromRgb(255, 0, 0)
        elif isinstance(color, tuple):
            return QtGui.QColor.fromRgb(*color)
        elif isinstance(color, list):
            return QtGui.QColor.fromRgb(*tuple(color))
        elif isinstance(color, QtGui.QColor):
            return color
        raise TypeError("Unrecognised type for color")

    def __signin_pressed(self):
        self.parent().parent().parent().stack.setCurrentWidget(
            self.parent().parent().parent().main_view
        )

    def __cntrls_pressed(self):
        self.parent().parent().parent().stack.setCurrentWidget(
            self.parent().parent().parent().settings_view
        )

    def __alarms_pressed(self):
        self.parent().parent().parent().stack.setCurrentWidget(
            self.parent().parent().parent().alarms_view
        )

    def __fancon_pressed(self):
        self.parent().parent().parent().stack.setCurrentWidget(
            self.parent().parent().parent().modes_view
        )

    def __find_icons(self):
        initial_path = "hev-display/assets/png/"
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
            if "png" in w[1]:
                temp_path = os.path.join(os.path.normpath(w[0]), "png")
                return temp_path

        raise Exception(FileNotFoundError, "could not locate png icon files")


if __name__ == "__main__":
    y = QtWidgets.QApplication()
    x = TabPageButtons()
