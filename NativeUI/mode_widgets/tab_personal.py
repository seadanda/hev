#!/usr/bin/env python3

"""
tab_personal.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Development"

from PySide2 import QtWidgets, QtGui, QtCore
import sys

sys.path.append("~/Documents/hev/NativeUI/")
from global_widgets.template_set_values import TemplateSetValues


class TabPersonal(TemplateSetValues):
    def __init__(self, *args, **kwargs):
        super(TabPersonal, self).__init__(*args, **kwargs)
        settingsList = [
            ["Name", "/min", "name", "SET_PERSONAL", "NAME"],
            ["Patient ID", "s", "patient_id", "SET_PERSONAL", "PATIENT_ID"],
            ["Age", "", "age", "SET_PERSONAL", "AGE"],
            ["Sex", "", "sex", "SET_PERSONAL", "SEX"],
            ["Weight", "", "weight", "SET_PERSONAL", "WEIGHT"],
            ["Height", "", "height", "SET_PERSONAL", "HEIGHT"],
        ]
        textBoxes = ["Name", "Patient ID", "Sex"]
        self.setPacketType("personal")
        self.addPersonalCol(settingsList, textBoxes)
        self.addButtons()
        self.finaliseLayout()


if __name__ == "__main__":
    # sys.path.append("../")
    app = QtWidgets.QApplication(sys.argv)
    widg = TabPersonal()
    widg.show()
    sys.exit(app.exec_())
