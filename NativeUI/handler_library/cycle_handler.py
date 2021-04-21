"""
cycle_handler.py
"""

from handler_library.handler import Handler
from PySide2.QtCore import Signal, QObject


class CycleHandler(Handler, QObject):
    """
    Subclass of the Handler class (handler.py) to handle cycle data.

    Inherits from QObject to give us access to pyside2's signal class.
    """

    CycleSignal = Signal(dict)

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
        ]:
            outdict[key] = cycle_data[key]

        self.CycleSignal.emit(outdict)
        return 0


class MeasurementsHandler(Handler, QObject):
    """
    Handler for measurements.
    TODO: decide if we want a different signal for each measurement widget?
    TODO: move to a separate file.
    """

    def __init__(self):
        super().__init__()
        QObject.__init__(self)
