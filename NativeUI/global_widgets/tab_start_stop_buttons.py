"""
TODO
"""
import logging
from PySide2 import QtGui, QtWidgets
from PySide2.QtCore import QSize


class TabStartStopStandbyButtons(QtWidgets.QWidget):
    """
    TODO
    """

    def __init__(self, *args, size: QSize = None, colors: dict = None, **kwargs):
        super(TabStartStopStandbyButtons, self).__init__(*args, **kwargs)

        self.__colors = self.__interpret_colors(colors)
        if size is not None:
            self.__button_size = size
        else:
            self.__button_size = QSize(100, 20)

        layout = QtWidgets.QVBoxLayout()

        self.button_start = QtWidgets.QPushButton()
        self.button_stop = QtWidgets.QPushButton()
        self.button_standby = QtWidgets.QPushButton()

        self.__buttons = [self.button_start, self.button_stop, self.button_standby]
        self.__buttontext = ["START", "STOP", "STANDBY"]

        for button, text in zip(self.__buttons, self.__buttontext):
            button.setText(text)
            layout.addWidget(button)
            button.setStyleSheet(
                "background-color: " + self.__colors["background"].name() + ";"
                "border-color: " + self.__colors["foreground"].name() + ";"
                "font-size: 20pt;"
                "color: " + self.__colors["foreground"].name() + ";"
            )
            button.setFixedSize(self.__button_size)

        self.setLayout(layout)

    def __interpret_colors(self, colors):
        try:
            _, _ = colors["foreground"], colors["background"]
            return colors
        except TypeError:
            logging.warning("Color dict not set")
        except KeyError:
            logging.warning("missing key in color dict: %" % colors)
        return {
            "foreground": QtGui.QColor.fromRgb(255, 0, 0),
            "background": QtGui.QColor.fromRgb(0, 255, 0),
        }
