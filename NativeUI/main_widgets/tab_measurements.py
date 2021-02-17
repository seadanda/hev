import logging

from PySide2 import QtCore, QtGui, QtWidgets


class TabMeasurements(QtWidgets.QWidget):
    """
    Block of widgets displaying various measurement parameters
    """

    def __init__(self, NativeUI, *args, **kwargs):
        super(TabMeasurements, self).__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout()

        widget_list = [
            CycleMeasurementWidget(NativeUI, "P_plateau [cmH2O]", "plateau_pressure"),
            CycleMeasurementWidget(NativeUI, "RR", "respiratory_rate"),
            CycleMeasurementWidget(NativeUI, "FIO2 [%]", "fiO2_percent"),
            CycleMeasurementWidget(NativeUI, "VTE [mL]", "exhaled_tidal_volume"),
            CycleMeasurementWidget(NativeUI, "MVE [L/min]", "exhaled_minute_volume"),
            ReadbackMeasurementWidget(NativeUI, "PEEP [cmH2O]", "peep"),
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
        NativeUI,
        label: str,
        key: str,
        width: int = 140,
        height: int = 60,
        *args,
        **kwargs
    ):
        super(MeasurementWidget, self).__init__(*args, **kwargs)
        self.NativeUI = NativeUI

        self.key = key
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
        Placeholder function to be overwritten by subclasses
        """
        pass


class CycleMeasurementWidget(MeasurementWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_value(self):
        if self.key is None:
            self.value_display.setText("-")
            return 0
        try:
            self.value_display.setNum(self.NativeUI.get_data_db()[self.key])
        except KeyError:  # usually means that the db hasn't been populated yet
            self.value_display.setText("-")
            return 0
        return 0


class ReadbackMeasurementWidget(MeasurementWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_value(self):
        if self.key is None:
            self.value_display.setText("-")
            return 0
        try:
            self.value_display.setNum(self.NativeUI.get_readback_db()[self.key])
        except KeyError:  # usually means that the db hasn't been populated yet
            self.value_display.setText("-")
            return 0
        return 0
