from PySide2 import QtWidgets, QtGui, QtCore
from global_widgets.template_set_values import TemplateSetValues


class TabClinical(
    TemplateSetValues
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, *args, **kwargs):
        super(TabClinical, self).__init__(*args, **kwargs)
        self.liveUpdating = True
        self.modifications = []
        # self.spinDict = {}
        clinicalList = [
            ["APNEA", "ms", "duration_calibration"],
            ["Check Pressure Patient", "ms", "duration_buff_purge"],
            ["High FIO2", "ms", ""],
            ["High Pressure_Low", " ", ""],
            ["High Respiratory Rate", " ", ""],
            ["High VTE", " ", ""],
            ["Low VTE", " ", ""],
            ["High VTI", " ", ""],
            ["Low VTI", " ", ""],
            ["Low FIO2", " ", ""],
            ["Occlusion_Low", " ", ""],
            ["High PEEP", " ", ""],
            ["Low PEEP", " ", ""],
        ]
        self.addSpinDblCol(clinicalList)
        self.addButtons()
        self.finaliseLayout()
