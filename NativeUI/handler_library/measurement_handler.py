"""
measurement_handler.py
"""

from handler_library.handler import PayloadHandler
from PySide2.QtCore import Signal
import logging


class MeasurementHandler(PayloadHandler):
    """
    Subclass of the PayloadHandler class (handler.py) to handle cycle and readback data.
    """

    UpdateMeasurements = Signal(dict)

    def __init__(self, *args, **kwargs):
        super().__init__(["CYCLE", "READBACK"], *args, **kwargs)

    def active_payload(self, *args, **kwargs) -> int:
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
