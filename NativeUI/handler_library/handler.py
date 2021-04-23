"""
handler.py
"""

from threading import Lock


class PayloadHandler:
    """
    Base class for the data handlers.
    """

    def __init__(self, payload_types: list):
        for key in payload_types:
            if not isinstance(key, str):
                raise TypeError(
                    "payload types must be of type 'str', not %s", type(key)
                )
        self.__database = {}
        self.__lock = Lock()
        self.__payload_types = payload_types

    def set_db(self, payload: dict) -> int:
        """
        If the provided database is of the correct type, copy its contents to the database
        """
        if payload["type"] not in self.__payload_types:
            return 1

        with self.__lock:
            for key in payload[payload["type"]]:
                self.__database[key] = payload[payload["type"]][key]

        self.active_payload(payload)
        return 0

    def get_db(self) -> dict:
        """
        Return the content of the __database dictionary.
        """
        with self.__lock:
            return dict(self.__database)

    def active_payload(self, payload: dict):
        """
        Overridable function called after recieving new data. Passes in the full payload
        so that we have access to the full context of the information.
        """
        pass
