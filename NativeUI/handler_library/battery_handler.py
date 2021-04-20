from handler_library.handler import Handler
from PySide2.QtCore import Signal, QObject


class BatteryHandler(Handler, QObject):
    UpdateBatteryDisplay = Signal(dict)

    def __init__(self):
        super().__init__()
        QObject.__init__(
            self
        )  # Give ourselves access to the QObject Signal functionality.

    def on_payload(self):
        print("BatteryHandler.on_payload()")
        self.UpdateBatteryDisplay.emit(self.get_db())
