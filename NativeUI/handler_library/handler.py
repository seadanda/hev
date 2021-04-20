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
        data_changed = False
        with self.__lock:
            for key in payload:
                if self.__database[key] != payload[key]:
                    data_changed = True
                    self.__database[key] = payload[key]

        if data_changed:
            self.on_payload()
        return 0

    def get_db(self) -> dict:
        """
        Return the content of the __database dictionary.
        """
        with self.__lock:
            return self.__database

    def on_payload(self):
        """
        Overridable function called after recieving new data.
        """
        pass
