import os
from PySide2 import QtGui, QtWidgets
from PySide2.QtCore import QSize
import logging


class TabPageButtons(QtWidgets.QWidget):
    """
    Widget to contain the buttons that allow movement between pages. Buttons
    are oriented vertically.

    Button colors may be dictated by setting the colors dict, wherein
    foreground and background colors are provided in QColor types. If button
    colors are not set they default to red.
    """

    def __init__(self, *args, colors: dict = None, **kwargs):
        super(TabPageButtons, self).__init__(*args, **kwargs)

        self.__iconsize = QSize(80, 80)
        self.__iconpath = self.__find_icons()
        self.__colors = self.__interpret_colors(colors)

        layout = QtWidgets.QVBoxLayout()

        self.button_signin = QtWidgets.QPushButton("")
        self.button_alarms = QtWidgets.QPushButton("")
        self.button_fancon = QtWidgets.QPushButton("")
        self.button_cntrls = QtWidgets.QPushButton("")

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
            mask = pixmap.mask()  # mask from alpha
            pixmap.fill(self.__colors["foreground"])  # fill with color
            pixmap.setMask(mask)  # reapply mask

            # set button appearance
            button.setStyleSheet(
                "background-color: " + self.__colors["background"].name() + ";"
            )

            button.setIcon(QtGui.QIcon(pixmap))
            button.setIconSize(self.__iconsize)
            layout.addWidget(button)

        self.setLayout(layout)

        self.button_signin.pressed.connect(self.__signin_pressed)
        self.button_alarms.pressed.connect(self.__alarms_pressed)
        self.button_fancon.pressed.connect(self.__fancon_pressed)
        self.button_cntrls.pressed.connect(self.__cntrls_pressed)

    def __interpret_colors(self, colors):
        try:
            _, _ = colors["foreground"], colors["background"]
            return colors
        except TypeError:
            logging.warning("Color dict not set")
        except KeyError:
            logging.warning("missing key in color dict: %s" % str(colors))
        return {
            "foreground": QtGui.QColor.fromRgb(255, 0, 0),
            "background": QtGui.QColor.fromRgb(0, 255, 0),
        }

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
