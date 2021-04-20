"""
handler.py
"""

from threading import Lock


class Handler:
    """
    Base class for the data handlers.
    """

    def __init__(self):
        self.__database = {}
        self.__lock = Lock()

    def set_db(self, payload: dict):
        """
        Set the content of the __database dictionary.
        """
        with self.__lock:
            for key in payload:
                self.__database[key] = payload[key]
        self.on_payload()
        return 0

    def on_payload(self):
        """
        Overridable function called after recieving new data.
        """
        pass
