#!/usr/bin/env python3

"""
measurements_widget.py

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
import math


class MeasurementsBlockWidget(QtWidgets.QWidget):
    """
    Block of widgets displaying various measurement parameters
    """

    def __init__(
        self, NativeUI, *args, measurements: list = None, columns: int = 1, **kwargs
    ):

        super().__init__(*args, **kwargs)
        self.__grid_columns = columns

        layout = QtWidgets.QGridLayout(self)

        # Create "Measurements" Title
        self.title_label = QtWidgets.QLabel(NativeUI.text["layout_label_measurements"])
        self.title_label.setStyleSheet(
            # "font-size:" + NativeUI.text_size + ";"
            "color:" + NativeUI.colors["page_foreground"].name() + ";"
            "background-color:" + NativeUI.colors["page_background"].name() + ";"
        )
        self.title_label.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        self.title_label.setAlignment(QtCore.Qt.AlignHCenter)

        # Create Muasurement widgets
        self.widget_list = []
        for measurement in measurements:
            if len(measurement) > 3:
                self.widget_list.append(
                    MeasurementWidget(
                        NativeUI,
                        measurement[0],  # Label
                        measurement[2],  # Keydir
                        measurement[1],  # Key
                        measurement[3],  # Format
                    )
                )
            else:
                self.widget_list.append(
                    MeasurementWidget(
                        NativeUI,
                        measurement[0],  # Label
                        measurement[2],  # Keydir
                        measurement[1],  # Key
                    )
                )

        # Compute max number of items per column
        self.__grid_rows = int(len(self.widget_list) / (self.__grid_columns))
        if len(self.widget_list) % (self.__grid_columns) != 0:
            self.__grid_rows += 1

        # Arrange layout widgets in rows and columns
        layout.addWidget(
            self.title_label,
            columnspan=self.__grid_columns,
            alignment=QtCore.Qt.AlignHCenter,
        )
        i_row_min = 1  # first row for measurement widgets below the label
        i_row = i_row_min
        i_col = 0
        for widget in self.widget_list:
            layout.addWidget(widget, i_row, i_col)
            i_row += 1
            if i_row == self.__grid_rows + i_row_min:
                i_row = i_row_min
                i_col += 1

        layout.setAlignment(QtCore.Qt.AlignHCenter)

        self.setLayout(layout)

    def set_size(
        self, x: int, y: int, spacing: int = 10, widget_size_ratio: float = 2.5
    ) -> int:
        """
        Set the size of the measurements block widget.

        Sizes are computed on the assumption that the ratio of width to height for
        individual measurement widgets is equal to widget_size_ratio.

        If both x and y are set, MeasurementsBlockWidget will have size x by y, and
        individual widgets will be size x/n_cols-spacing by MIN(y/n_rows,
        x/(n_cols*widget_size_ratio))-spacing.

        If x alone is set, individual widgets will have size x/n_cols-spacing by
        (x/n_cols)/widget_size_ratio-spacing. MeasurementsBlockWidget will have size x
        by ((x/n_cols)/widget_size_ratio)*n_rows (i.e. height expands to fit all of the
        widgets).

        If y alone is set, individual widgets will have size
        (y/n_rows)*widget_size_ratio-spacing by y/n_rows-spacing.
        MeasurementsBlockWidget will have size ((y/n_rows)*widget_size_ratio)*n_cols by
        y (e.r. width expands to fit all of the widgets).
        """

        if x is not None and y is not None:
            self.setFixedSize(x, y)
            self.title_label.setFixedWidth(x)
            x_widget = int(x / self.__grid_columns)
            y_widget = min(int(y / self.__grid_rows), int(x_widget / widget_size_ratio))
        elif x is not None and y is None:
            self.title_label.setFixedWidth(x)
            x_widget = int(x / self.__grid_columns)
            y_widget = int(x_widget / widget_size_ratio)
            self.setFixedSize(x, y_widget * self.__grid_rows)
        elif x is None and y is not None:
            y_widget = int(y / self.__grid_rows)
            x_widget = int(y_widget * widget_size_ratio)
            self.setFixedSize(x_widget * self.__grid_columns, y)
        else:
            raise ValueError("set_size called with no size information")

        for widget in self.widget_list:
            widget.set_size(x_widget - spacing, y_widget - spacing)
        return 0

    def set_label_font(self, font: QtGui.QFont) -> int:
        """
        Set the font of the title label and measurement names.
        """
        self.title_label.setFont(font)
        for widget in self.widget_list:
            widget.name_display.setFont(font)
        return 0

    def set_value_font(self, font: QtGui.QFont) -> int:
        """
        Set the font of the measurement value displays.
        """
        for widget in self.widget_list:
            widget.value_display.setFont(font)
        return 0

    @QtCore.Slot()
    def update_value(self) -> int:
        for widget in self.widget_list:
            widget.update_value()


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
        width (int): the width of the widget in pixels
        height (int): the height of the widget in pixels

    Methods
    -------
        update_value():
    """

    def __init__(
        self,
        NativeUI,
        label: str,
        keydir: str,
        key: str,
        format: str = "{:.1f}",
        *args,
        **kwargs
    ):
        super(MeasurementWidget, self).__init__(*args, **kwargs)

        self.NativeUI = NativeUI
        self.keydir = keydir
        self.key = key
        self.format = format

        # Layout and widgets
        layout = QtWidgets.QVBoxLayout()

        self.name_display = QtWidgets.QLabel(label)
        self.value_display = QtWidgets.QLabel()

        layout.addWidget(self.name_display)
        layout.addWidget(self.value_display)

        # Appearance
        self.name_display.setAlignment(QtCore.Qt.AlignCenter)
        self.name_display.setStyleSheet(
            "color: " + self.NativeUI.colors["label_foreground"].name() + ";"
            "background-color:" + self.NativeUI.colors["label_background"].name() + ";"
            "border: none;"
            # "font-size: " + NativeUI.text_size + ";"
        )

        self.value_display.setAlignment(QtCore.Qt.AlignCenter)
        self.value_display.setStyleSheet(
            "color: " + self.NativeUI.colors["label_background"].name() + ";"
            "background-color: " + self.NativeUI.colors["label_foreground"].name() + ";"
            "border: none;"
        )
        # self.value_display.setFont(QtGui.QFont("SansSerif", 40))

        # Layout
        layout.setSpacing(0)
        self.setLayout(layout)

    def update_value(self) -> int:
        """
        Poll the database in NativeUI and update the displayed value.
        """
        if self.key is None:  # widget can be created without assigning a parameter
            self.value_display.setText("-")
            return 0

        data = self.NativeUI.get_db(self.keydir)
        if len(data) == 0:  # means that the db hasn't been populated yet
            self.value_display.setText("-")
            return 0

        self.value_display.setText(
            self.__format_value(self.NativeUI.get_db(self.keydir)[self.key])
        )
        return 0

    def __format_value(self, number):
        if self.format is "ratio":
            n_digits = 1
            vals = number.as_integer_ratio()
            order_of_mag = math.floor(math.log(vals[0], 10))
            if order_of_mag > n_digits:
                vals = [
                    round(val / (10 ** (order_of_mag - (n_digits - 1)))) for val in vals
                ]

            return "{:.0f}:{:.0f}".format(*vals)
        return self.format.format(number)

    def set_size(self, x: int, y: int) -> int:
        self.setFixedSize(x, y)
        self.name_display.setFixedSize(x, int(y / 3))
        self.value_display.setFixedSize(x, int(2 * y / 3))
        return 0


class NormalMeasurementsBlockWidget(MeasurementsBlockWidget):
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
            (
                "MVE [<sup>L</sup>/<sub>min</sub>]",
                "exhaled_minute_volume",
                "cycle",
                "{:.0f}",
            ),
            ("PEEP [cmH<sub>2</sub>O]", "peep", "readback"),
        ]

        super().__init__(
            NativeUI, *args, measurements=measurements, columns=1, **kwargs
        )


class ExpertMeasurementsBloackWidget(MeasurementsBlockWidget):
    """
    Widget to contain the measurements for the standard page. Essentially a
    wrapper for the Measurements_Block class that specifies the measurements
    and number of columns.
    """

    def __init__(self, NativeUI, *args, **kwargs):
        measurements = [
            ("FIO<sub>2</sub> [%]", "fiO2_percent", "cycle"),
            ("I:E", "inhale_exhale_ratio", "readback", "ratio"),
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
            ("MVE [L/min]", "exhaled_minute_volume", "cycle", "{:.0f}"),
        ]

        super().__init__(
            NativeUI, *args, measurements=measurements, columns=2, **kwargs
        )
