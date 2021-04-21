"""
measurement_handler.py
"""

from handler_library.handler import Handler
from PySide2.QtCore import Signal, QObject
import logging


class MeasurementHandler(Handler, QObject):
    """
    Subclass of the Handler class (handler.py) to handle cycle and readback data.

    Inherits from QObject to give us access to pyside2's signal class.
    """

    UpdateMeasurements = Signal(dict)

    def __init__(self):
        super().__init__()
        QObject.__init__(self)

    def active_payload(self) -> int:
        cycle_data = self.get_db()
        outdict = {}

        for key in [
            "plateau_pressure",
            "respiratory_rate",
            "fiO2_percent",
            "exhaled_tidal_volume",
            "exhaled_minute_volume",
            "peak_inspiratory_pressure",
            "mean_airway_pressure",
            "inhaled_tidal_volume",
            "inhaled_minute_volume",
            "peep",
            "inhale_exhale_ratio",
        ]:
            try:
                outdict[key] = cycle_data[key]
            except KeyError:
                logging.debug("Invalid key %s in measurement database", key)

        self.UpdateMeasurements.emit(outdict)
        return 0
