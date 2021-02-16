import logging
import argparse
import sys

# from PySide2.QtCore import Slot
from PySide2 import QtWidgets, QtGui, QtCore

# from PySide2.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout
from hevclient import HEVClient
from alarm_widgets.tab_alarms import TabAlarm
from alarm_widgets.tab_clinical import TabClinical
from global_widgets.global_select_button import selectorButton
from global_widgets.template_main_pages import TemplateMainPages


class AlarmView(TemplateMainPages):
    def __init__(self, *args, **kwargs):
        super(AlarmView, self).__init__(*args, **kwargs)

        self.alarmButton = selectorButton("List of Alarms")
        self.clinicalButton = selectorButton("Clinical Limits")
        self.techButton = selectorButton("Technical Limits")

        self.buttonWidgets = [self.alarmButton, self.clinicalButton, self.techButton]

        self.alarmTab = TabAlarm()
        self.clinicalTab = TabClinical()
        self.technicalTab = TabClinical()
        self.tabsList = [self.alarmTab, self.clinicalTab, self.technicalTab]
        self.buildPage(self.buttonWidgets, self.tabsList)
