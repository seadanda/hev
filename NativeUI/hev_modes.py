#!/usr/bin/env python3

"""
hev_modes.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

from PySide2 import QtCore, QtGui, QtWidgets
from mode_widgets.tab_modes import TabModes
from mode_widgets.tab_personal import TabPersonal
from global_widgets.global_select_button import selectorButton
from global_widgets.template_main_pages import TemplateMainPages


class ModeView(TemplateMainPages):
    def __init__(self, NativeUI, *args, **kwargs):
        super(ModeView, self).__init__(*args, **kwargs)

        self.modeButton = selectorButton(NativeUI, "Mode Settings")
        self.personalButton = selectorButton(NativeUI, "Personal Settings")
        self.buttonWidgets = [self.modeButton, self.personalButton]

        self.modeTab = TabModes(NativeUI)
        self.personalTab = TabPersonal(NativeUI)
        self.tabsList = [self.modeTab, self.personalTab]

        self.buildPage(self.buttonWidgets, self.tabsList)
