#!/usr/bin/env python3

"""
tab_measurements.py

Part of NativeUI. Defines the MeasurementWidget class to display current
parameters, and constructs the TabMeasurements widget to display the requisite
MeasurementWidgets.

TODO: Create a second widget constructor that shows the widgets for the expert
plots page.
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Benjamin Mummery"
__email__ = "benjamin.mummery@stfc.ac.uk"
__status__ = "Development"

import logging

from PySide2 import QtCore, QtGui, QtWidgets


class Measurements_Block(QtWidgets.QWidget):
    """
    Block of widgets displaying various measurement parameters
    """

    def __init__(
        self, NativeUI, *args, measurements: list = None, columns: int = 1, **kwargs
    ):

        super(Measurements_Block, self).__init__(*args, **kwargs)

        # layout = QtWidgets.QVBoxLayout()
        layout = QtWidgets.QGridLayout(self)

        widget_list = []
        for measurement in measurements:
            if measurement[2] == "cycle":
                widget_list.append(
                    CycleMeasurementWidget(NativeUI, measurement[0], measurement[1])
                )
            elif measurement[2] == "readback":
                widget_list.append(
                    ReadbackMeasurementWidget(NativeUI, measurement[0], measurement[1])
                )
            else:
                raise AttributeError(
                    "measurement type %s is not a recognised parameter" % measurement[2]
                )

        # label = QtWidgets.QLabel("Measurements")
        # label.setAlignment(QtCore.Qt.AlignCenter)
        # label.setStyleSheet(
        #     "color: grey;"
        #     "font-size: " + NativeUI.text_size + ";"
        # )
        # layout.addWidget(label)

        # Compute max number of items per column
        max_col_length = int(len(widget_list) / (columns))
        if len(widget_list) % (columns) != 0:
            max_col_length += 1

        i_row = 0
        i_col = 0
        for widget in widget_list:
            layout.addWidget(widget, i_row, i_col)
            i_row += 1
            if i_row == max_col_length:
                i_row = 0
                i_col += 1

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
        width = 250
        height = 120
        labelheight = 35

        self.NativeUI = NativeUI
        self.key = key

        # Layout and widgets
        layout = QtWidgets.QVBoxLayout()

        self.name_display = QtWidgets.QLabel(label)
        self.value_display = QtWidgets.QLabel()

        layout.addWidget(self.name_display)
        layout.addWidget(self.value_display)

        # Appearance
        self.name_display.setAlignment(QtCore.Qt.AlignCenter)
        self.name_display.setStyleSheet(
            "color: " + self.NativeUI.colors["foreground"].name() + ";"
            "background-color:"
            + self.NativeUI.colors["background-enabled"].name()
            + ";"
            "border: none;"
            "font-size: " + NativeUI.text_size + ";"
        )
        self.name_display.setFixedSize(width, labelheight)
        self.name_display.setFont(QtGui.QFont("SansSerif", 10))

        self.value_display.setAlignment(QtCore.Qt.AlignCenter)
        self.value_display.setStyleSheet(
            "color: black;"
            "background-color: " + self.NativeUI.colors["foreground"].name() + ";"
            "border: none;"
        )
        self.value_display.setFixedSize(width, height - labelheight)
        self.value_display.setFont(QtGui.QFont("SansSerif", 20))

        # Layout
        layout.setSpacing(0)
        self.setLayout(layout)
        self.setFixedSize(QtCore.QSize(width, height))

    def update_value(self):
        """
        Placeholder function to be overwritten by subclasses
        """
        pass


class CycleMeasurementWidget(MeasurementWidget):
    """
    Widget to display a measurement in real time whose value is contained in
    Cycle payloads.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_value(self):
        if self.key is None:  # widget can be created without assigning a parameter
            self.value_display.setText("-")
            return 0

        data = self.NativeUI.get_cycle_db()
        if len(data) == 0:  # means that the db hasn't been populated yet
            self.value_display.setText("-")
            return 0

        self.value_display.setNum(self.NativeUI.get_cycle_db()[self.key])
        return 0


class ReadbackMeasurementWidget(MeasurementWidget):
    """
    Widget to display a measurement in real time whose value is contained in
    Readback payloads.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_value(self):
        if self.key is None:  # widget can be created without assigning a parameter
            self.value_display.setText("-")
            return 0

        data = self.NativeUI.get_readback_db()
        if len(data) == 0:  # means that the db hasn't been populated yet
            self.value_display.setText("-")
            return 0

        self.value_display.setNum(self.NativeUI.get_readback_db()[self.key])
        return 0


class TabMeasurements(Measurements_Block):
    """
    Widget to contain the measurements for the standard page. Essentially a
    wrapper for the Measurements_Block class that specifies the measurements
    and number of columns.
    """

    def __init__(self, NativeUI, *args, **kwargs):
        measurements = [
            ("P<sub>Plateau</sub> [cmH<sub>2</sub>O]", "plateau_pressure", "cycle"),
            ("RR", "respiratory_rate", "cycle"),
            ("FIO<sub>2</sub> [%]", "fiO2_percent", "cycle"),
            ("VTE [mL]", "exhaled_tidal_volume", "cycle"),
            ("MVE [<sup>L</sup>/<sub>min</sub>]", "exhaled_minute_volume", "cycle"),
            ("PEEP [cmH<sub>2</sub>O]", "peep", "readback"),
        ]

        super().__init__(
            NativeUI, *args, measurements=measurements, columns=1, **kwargs
        )


class TabExpertMeasurements(Measurements_Block):
    """
    Widget to contain the measurements for the standard page. Essentially a
    wrapper for the Measurements_Block class that specifies the measurements
    and number of columns.

    TODO: update the measurements list.
    """

    def __init__(self, NativeUI, *args, **kwargs):
        measurements = [
            ("P_plateau [cmH2O]", "plateau_pressure", "cycle"),
            ("RR", "respiratory_rate", "cycle"),
            ("FIO2 [%]", "fiO2_percent", "cycle"),
            ("VTE [mL]", "exhaled_tidal_volume", "cycle"),
            ("MVE [L/min]", "exhaled_minute_volume", "cycle"),
            ("PEEP [cmH2O]", "peep", "readback"),
        ]

        super().__init__(
            NativeUI, *args, measurements=measurements, columns=2, **kwargs
        )
