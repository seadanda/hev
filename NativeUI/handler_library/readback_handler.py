"""
readback_handler.py
"""

from handler_library.handler import Handler
from PySide2.QtCore import Signal, QObject


class ReadbackHandler(Handler, QObject):
    """
    Subclass of the Handler class (handler.py) to handle readback data.

    Inherits from QObject to give us access to pyside2's signal class.
    """

    ReadbackSignal = Signal(dict)

    def __init__(self):
        super().__init__()
        QObject.__init__(self)

    def active_payload(self) -> int:
        cycle_data = self.get_db()
        outdict = {}

        for key in ["peep", "inhale_exhale_ratio"]:
            outdict[key] = cycle_data[key]

        self.ReadbackSignal.emit(outdict)
        return 0
