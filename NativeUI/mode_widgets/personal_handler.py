from global_widgets.global_spinbox import labelledSpin
from widget_library.ok_cancel_buttons_widget import OkButtonWidget, CancelButtonWidget, OkSendButtonWidget
#from global_widgets.global_send_popup import SetConfirmPopup
from widget_library.line_edit_widget import LabelledLineEditWidget
from handler_library.handler import PayloadHandler
from PySide2.QtCore import Signal
from PySide2 import QtWidgets, QtGui, QtCore

class PersonalHandler(PayloadHandler):  # chose QWidget over QDialog family because easier to modify

    UpdatePersonalDisplay = Signal(dict)

    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(['PERSONAL'], *args, **kwargs)
        self.NativeUI = NativeUI
        self.spinDict = {}
        self.buttonDict = {}
        self.textDict = {}

    def add_widget(self, widget, key: str):
        if isinstance(widget, labelledSpin):
            self.spinDict[key] = widget
        if isinstance(widget, LabelledLineEditWidget):
            self.textDict[key] = widget
        if isinstance(widget, OkButtonWidget) or isinstance(widget, CancelButtonWidget) or isinstance(widget, OkSendButtonWidget):
            self.buttonDict[key] = widget

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