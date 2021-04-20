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

    def set_db(self, payload: dict) -> int:
        """
        Set the content of the __database dictionary.
        """

        with self.__lock:
            for key in payload:
                self.__database[key] = payload[key]

        self.active_payload()
        return 0

    def get_db(self) -> dict:
        """
        Return the content of the __database dictionary.
        """
        with self.__lock:
            return dict(self.__database)

    def active_payload(self):
        """
        Overridable function called after recieving new data.
        """
        pass
