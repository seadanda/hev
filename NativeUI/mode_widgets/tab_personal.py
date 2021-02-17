from PySide2 import QtWidgets, QtGui, QtCore
from global_widgets.template_set_values import TemplateSetValues


class TabPersonal(
    TemplateSetValues
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, *args, **kwargs):
        settingsList = [
            ["Name", "/min", "respiratory_rate"],
            ["Patient ID", "s", "inhale_time"],
            ["Age", "", "ie_ratio"],
            ["Sex", "", "inhale_trigger_threshold"],
            ["Weight", "", "exhale_trigger_threshold"],
            ["Height", "", "inspiratory_pressure"],
        ]
        super(TabPersonal, self).__init__(*args, **kwargs)
        self.addSpinSingleCol(settingsList)
        self.addButtons()
        self.finaliseLayout()
