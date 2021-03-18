#!/usr/bin/env python3

"""
tab_clinical.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

from PySide2 import QtWidgets, QtGui, QtCore
from global_widgets.template_set_values import TemplateSetValues


class TabClinical(
    TemplateSetValues
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, *args, **kwargs):
        super(TabClinical, self).__init__(*args, **kwargs)
        self.liveUpdating = True
        clinicalList = [
            ["APNEA", "ms", ""],
            ["Check Pressure Patient", "ms", ""],
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
