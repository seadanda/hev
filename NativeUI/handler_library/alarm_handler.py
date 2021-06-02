"""
alarm_handler.py
"""

from handler_library.handler import PayloadHandler
from PySide2.QtCore import QObject


class AlarmHandler(PayloadHandler, QObject):
    """
    Subclass of the PayloadHandler class (handler.py) to handle alarm data.

    Inherits from QObject to give us access to pyside2's signal class.
    """

    def __init__(self):
        super().__init__()
        QObject.__init__(self)
