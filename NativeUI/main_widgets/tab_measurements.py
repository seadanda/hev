import logging

from PySide2 import QtCore, QtGui, QtWidgets


class TabMeasurements(QtWidgets.QWidget):
    """
    Block of widgets displaying various measurement parameters
    """

    def __init__(self, *args, **kwargs):
        super(TabMeasurements, self).__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout()

        self.P_plateau_widget = MeasurementWidget(
            "P_plateau [cmH2O]", "_cycle", "plateau_pressure"
        )
        self.RR_widget = MeasurementWidget("RR", "_readback", "inhale_exhale_ratio")
        self.FIO2_widget = MeasurementWidget("FIO2 [%]", "_cycle", "fiO2_percent")
        self.VTE_widget = MeasurementWidget(
            "VTE [mL]", "_cycle", "exhaled_tidal_volume"
        )
        self.MVE_widget = MeasurementWidget(
            "MVE [L/min]", "_cycle", "exhaled_minute_volume"
        )
        self.PEEP_widget = MeasurementWidget("PEEP [cmH2O]", "_readback", "peep")

        widget_list = [
            self.P_plateau_widget,
            self.RR_widget,
            self.FIO2_widget,
            self.VTE_widget,
            self.MVE_widget,
            self.PEEP_widget,
        ]

        label = QtWidgets.QLabel("Measurements")
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("color: grey; font-size: 15px")
        layout.addWidget(label)

        for widget in widget_list:
            layout.addWidget(widget)

        self.setLayout(layout)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(16)  # just faster than 60Hz
        for widget in widget_list:
            self.timer.timeout.connect(widget.update_value)
        self.timer.start()


class MeasurementWidget(QtWidgets.QWidget):
    """
    Non-interactive widget to display a single measurement along with its label.

    Parameters
    ----------
        label
        keydir
        key

    Optional Parameters
    -------------------
        width
        height

    Methods
    -------
        update_value() :
    """

    def __init__(
        self,
        label: str,
        keydir: str,
        key: str,
        width: int = 140,
        height: int = 60,
        *args,
        **kwargs
    ):
        super(MeasurementWidget, self).__init__(*args, **kwargs)

        self.__keydir = keydir
        self.__key = key
        min_height = 60

        # Layout and widgets
        layout = QtWidgets.QVBoxLayout()

        self.name_display = QtWidgets.QLabel(label)
        self.value_display = QtWidgets.QLabel()

        layout.addWidget(self.name_display)
        layout.addWidget(self.value_display)

        # Appearance
        height = max([min_height, height])
        topheight = 20
        self.name_display.setAlignment(QtCore.Qt.AlignCenter)
        self.name_display.setStyleSheet(
            "color: white; background-color: black; border-style: outset; border-width: 1px; border-color: black; border-radius: 5px"
        )
        self.name_display.setFixedSize(width, topheight)
        self.name_display.setFont(QtGui.QFont("SansSerif", 10))

        self.value_display.setAlignment(QtCore.Qt.AlignCenter)
        self.value_display.setStyleSheet(
            "color: black; background-color: lightblue; border-style: outset; border-width: 1px; border-color: black; border-radius: 5px"
        )
        self.value_display.setFixedSize(width, height - topheight)
        self.value_display.setFont(QtGui.QFont("SansSerif", 20))

        # Layout
        layout.setSpacing(0)
        self.setLayout(layout)

    def update_value(self):
        """
        Update the widget to display the current value
        """
        # Placeholder while in development - TODO: remove
        if self.__keydir is None:
            self.value_display.setText("-")
            return
        if self.__key is None:
            self.value_display.setText("-")
            return

        #
        try:
            data = vars(self.parent().parent().parent())[self.__keydir][self.__key]
        except TypeError:
            self.value_display.setText("-")
            return
        except KeyError:
            outstr = (
                "unrecognised database - key pair: "
                + str(self.__keydir)
                + " - "
                + str(self.__key)
            )
            logging.warning(outstr)
            self.value_display.setText("-")
            return

        self.value_display.setNum(data)
