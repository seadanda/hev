#!/usr/bin/env python3

"""
tab_measurements.py

Part of NativeUI. Defines the MeasurementWidget class to display current
parameters, and constructs the TabMeasurements widget to display the requisite
MeasurementWidgets.
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
            widget_list.append(
                MeasurementWidget(
                    NativeUI,
                    measurement[0],  # Label
                    measurement[2],  # Keydir
                    measurement[1],  # Key
                )
            )

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
        label (str): the measuremnt label as displayed to the user (can include html).
        keydir (str): the data dict in which the quantity to be displayed is stored.
        key (str): the key for the measurement as used in keydir

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
        keydir: str,
        key: str,
        width: int = 250,
        height: int = 120,
        *args,
        **kwargs
    ):
        super(MeasurementWidget, self).__init__(*args, **kwargs)

        labelheight = int(height / 3.0)

        self.NativeUI = NativeUI
        self.keydir = keydir
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
        # self.name_display.setFont(QtGui.QFont("SansSerif", 10))

        self.value_display.setAlignment(QtCore.Qt.AlignCenter)
        self.value_display.setStyleSheet(
            "color: black;"
            "background-color: " + self.NativeUI.colors["foreground"].name() + ";"
            "border: none;"
        )
        self.value_display.setFixedSize(width, height - labelheight)
        self.value_display.setFont(QtGui.QFont("SansSerif", 40))

        # Layout
        layout.setSpacing(0)
        self.setLayout(layout)
        self.setFixedSize(QtCore.QSize(width, height))

    def update_value(self):
        """
        Placeholder function to be overwritten by subclasses
        """
        if self.key is None:  # widget can be created without assigning a parameter
            self.value_display.setText("-")
            return 0

        data = self.NativeUI.get_db(self.keydir)
        if len(data) == 0:  # means that the db hasn't been populated yet
            self.value_display.setText("-")
            return 0

        self.value_display.setNum(self.NativeUI.get_db(self.keydir)[self.key])
        return 0


class TabMeasurements(Measurements_Block):
    """
    Widget to contain the measurements for the standard page. Essentially a
    wrapper for the Measurements_Block class that specifies the measurements
    and number of columns.
    """

    def __init__(self, NativeUI, *args, **kwargs):
        measurements = [
            ("P<sub>PLATEAU</sub> [cmH<sub>2</sub>O]", "plateau_pressure", "cycle"),
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
    """

    def __init__(self, NativeUI, *args, **kwargs):
        measurements = [
            ("FIO<sub>2</sub> [%]", "fiO2_percent", "cycle"),
            ("I:E", "inhale_exhale_ratio", "readback"),
            (
                "P<sub>PEAK</sub> [cmH<sub>2</sub>O]",
                "peak_inspiratory_pressure",
                "cycle",
            ),
            ("P<sub>PLATEAU</sub> [cmH<sub>2</sub>O]", "plateau_pressure", "cycle"),
            ("P<sub>MEAN</sub> [cmH<sub>2</sub>O]", "mean_airway_pressure", "cycle"),
            ("PEEP [cmH<sub>2</sub>O]", "peep", "readback"),
            ("VTI [mL]", "inhaled_tidal_volume", "cycle"),
            ("VTE [mL]", "exhaled_tidal_volume", "cycle"),
            ("MVI [L/min]", "inhaled_minute_volume", "cycle"),
            ("MVE [L/min]", "exhaled_minute_volume", "cycle"),
        ]

        super().__init__(
            NativeUI, *args, measurements=measurements, columns=2, **kwargs
        )
