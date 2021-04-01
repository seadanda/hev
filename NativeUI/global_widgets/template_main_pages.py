#!/usr/bin/env python3

"""
template_main_pages.py
"""

__author__ = ["Benjamin Mummery", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Tiago Sarmento"
__email__ = "tiago.sarmento@stfc.ac.uk"
__status__ = "Prototype"

from PySide2 import QtWidgets

# from global_widgets.global_send_popup import SetConfirmPopup


class TemplateMainPages(QtWidgets.QWidget):
    def buildPage(self, buttonList, tabList, *args, **kwargs):
        vlayout = QtWidgets.QVBoxLayout()
        hButtonLayout = QtWidgets.QHBoxLayout()

        self.stack = QtWidgets.QStackedWidget()
        for button, tab in zip(buttonList, tabList):
            hButtonLayout.addWidget(button)
            self.stack.addWidget(tab)
            button.pressed.connect(lambda i=button: self.setTab(i))

        self.setTab(buttonList[0])

        vlayout.addLayout(hButtonLayout)
        vlayout.addWidget(self.stack)
        self.setLayout(vlayout)

    def setTab(self, buttonWidg):
        for button, tab in zip(self.buttonWidgets, self.tabsList):
            if button == buttonWidg:
                button.setProperty("selected", "1")
                self.stack.setCurrentWidget(tab)
            else:
                button.setProperty("selected", "0")
            button.style().unpolish(button)
            button.style().polish(button)
