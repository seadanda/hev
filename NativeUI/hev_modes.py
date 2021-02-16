from PySide2 import QtCore, QtGui, QtWidgets
from mode_widgets.tab_modes import TabModes
from mode_widgets.tab_personal import TabPersonal
from global_widgets.global_select_button import selectorButton
from global_widgets.template_main_pages import TemplateMainPages


class ModeView(TemplateMainPages):
    def __init__(self, *args, **kwargs):
        super(ModeView, self).__init__(*args, **kwargs)

        self.modeButton = selectorButton("Mode Settings")
        self.personalButton = selectorButton("Personal Settings")
        self.buttonWidgets = [self.modeButton, self.personalButton]

        self.modeTab = TabModes()
        self.personalTab = TabPersonal()
        self.tabsList = [self.modeTab, self.personalTab]

        self.buildPage(self.buttonWidgets, self.tabsList)
