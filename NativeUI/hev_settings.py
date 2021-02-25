import argparse
import logging
import sys

# from PySide2.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout
from hevclient import HEVClient

# from PySide2.QtCore import Slot
from PySide2 import QtCore, QtGui, QtWidgets
from settings_widgets.tab_charts import TabChart
from settings_widgets.tab_expert import TabExpert
from global_widgets.global_select_button import selectorButton
from global_widgets.template_main_pages import TemplateMainPages


class SettingsView(TemplateMainPages):
    def __init__(self, NativeUI, *args, **kwargs):
        super(SettingsView, self).__init__(*args, **kwargs)

        self.expertButton = selectorButton(NativeUI, "Expert")
        self.chartButton = selectorButton(NativeUI, "Charts")
        self.buttonWidgets = [self.expertButton, self.chartButton]

        self.expertTab = TabExpert(NativeUI)
        self.chartTab = TabChart(NativeUI)
        self.tabsList = [self.expertTab, self.chartTab]

        self.buildPage(self.buttonWidgets, self.tabsList)
