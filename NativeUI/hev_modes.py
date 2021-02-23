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
