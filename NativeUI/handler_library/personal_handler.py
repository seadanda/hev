"""
personal_handler.py
"""

from handler_library.handler import PayloadHandler
from PySide2.QtCore import Signal


class PersonalHandler(PayloadHandler):
    """
    Subclass of the PayloadHandler class (handler.py) to handle personal data.

    Adds the UpdatePersonalDisplay signal designed to convey information to be displayed
    to the display widget.
    """

    UpdatePersonalDisplay = Signal(dict)

    def __init__(self, *args, **kwargs):
        super().__init__(["PERSONAL"], *args, **kwargs)

    def active_payload(self, *args, **kwargs) -> int:
        """
        When the personal data is updated, extract those parameters needed for display
        and emit the UpdatePersonalDisplay signal.
        """
        current_data = self.get_db()
        outdict = {}
        for key in ["name", "patient_id", "age", "sex", "height", "weight"]:
            outdict[key] = current_data[key]
        self.UpdatePersonalDisplay.emit(outdict)
        return 0
