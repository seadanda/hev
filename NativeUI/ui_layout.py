#!/usr/bin/env python3

"""
ui_layout.py

Contains the layout logic used in NativeUI.
"""

__author__ = "Benjamin Mummery"
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Benjamin Mummery"
__email__ = "benjamin.mummery@stfc.ac.uk"
__status__ = "Prototype"

from PySide2 import QtWidgets
from PySide2.QtCore import QSize
from global_widgets.tab_battery import TabBattery
from global_widgets.tab_personal import TabPersonal
from global_widgets.tab_modeswitch_button import TabModeswitchButton
from global_widgets.tab_page_buttons import TabPageButtons
from global_widgets.tab_start_stop_buttons import TabStartStopStandbyButtons
from alarm_widgets.tab_alarms import TabAlarm
from alarm_widgets.tab_clinical import TabClinical
from widget_library.switchable_stack_widget import SwitchableStackWidget

# from hev_main import MainView
from hev_settings import SettingsView
from main_widgets.tab_measurements import TabMeasurements, TabExpertMeasurements
from main_widgets.tab_plots import TabPlots
from main_widgets.tab_spin_buttons import TabSpinButtons
from main_widgets.tab_measurements import TabMeasurements
from main_widgets.tab_plots import TabPlots, TabCirclePlots
from main_widgets.tab_spin_buttons import TabSpinButtons
from main_widgets.tab_history_buttons import TabHistoryButtons

# from main_widgets.tab_expert_plots import TabExpertPlots

# from hev_alarms import AlarmView
from hev_modes import ModeView


class Layout:
    def __init__(self, NativeUI, widgets, *args, **kwargs):
        self.NativeUI = NativeUI
        self.widgets = widgets
        self.construct_stack_widgets()

    def construct_stack_widgets(self):
        """
        Tabs within stacks require their own layouts. Construct the tabs according to their specified layouts and build the stacks.
        """
        self.widgets.add_widget(
            SwitchableStackWidget(
                self.NativeUI,
                [
                    self.layout_tab_main_normal(
                        [
                            self.widgets.tab_normal_plots,
                            self.widgets.tab_normal_measurements,
                        ]
                    ),
                    self.layout_tab_main_detailed(
                        [
                            self.widgets.tab_detailed_plots,
                            self.widgets.tab_detailed_measurements,
                            self.widgets.tab_circle_plots,
                        ]
                    ),
                ],
                ["Normal", "Detailed"],
            ),
            "plots_stack",
        )

        self.widgets.add_widget(
            self.layout_page_main(
                [self.widgets.plots_stack],  # Center widgets
                [
                    self.widgets.tab_history_buttons,  # Bottom widgets
                    self.widgets.tab_spin,
                ],
            ),
            "main_page",
        )

        self.widgets.add_widget(
            self.__make_stack(
                [
                    self.widgets.main_page,
                    self.widgets.settings_page,
                    self.widgets.alarms_page,
                    self.widgets.modes_page,
                ]
            ),
            "page_stack",
        )
        return 0

    def global_layout(self):
        hlayout = QtWidgets.QHBoxLayout()
        vlayout = QtWidgets.QVBoxLayout()

        # Populate the Left Bar
        hlayout.addWidget(
            self.layout_left_bar(
                [self.widgets.tab_page_buttons, self.widgets.tab_start_stop_buttons]
            )
        )

        # Add the page stack
        hlayout.addWidget(self.widgets.page_stack)

        # Populate the Top Bar
        vlayout.addWidget(
            self.layout_top_bar(
                [
                    self.widgets.tab_modeswitch,
                    self.widgets.tab_personal,
                    self.widgets.tab_battery,
                ]
            )
        )

        vlayout.addLayout(hlayout)
        return vlayout

    def layout_top_bar(self, widgets: list) -> int:
        """
        Construct the layout for the global top bar
        """
        assert len(widgets) > 0

        top_bar = QtWidgets.QWidget()
        top_bar_layout = QtWidgets.QHBoxLayout(top_bar)
        for widget in widgets:
            top_bar_layout.addWidget(widget)
        top_bar.setLayout(top_bar_layout)
        return top_bar

    def layout_left_bar(self, widgets: list):
        """
        Construct the layout for the global left bar
        """
        left_bar = QtWidgets.QWidget()
        left_bar_layout = QtWidgets.QVBoxLayout(left_bar)
        for widget in widgets:
            left_bar_layout.addWidget(widget)
        left_bar_layout.setSpacing(0)
        left_bar_layout.setContentsMargins(0, 0, 0, 0)
        left_bar.setLayout(left_bar_layout)
        return left_bar

    def layout_page_main(self, center_widgets: list, bottom_widgets: list):
        page_main = QtWidgets.QWidget()
        page_main_layout = QtWidgets.QVBoxLayout()
        page_main_center_layout = QtWidgets.QHBoxLayout()
        page_main_bottom_layout = QtWidgets.QHBoxLayout()

        for widget in center_widgets:
            page_main_center_layout.addWidget(widget)
        for widget in bottom_widgets:
            page_main_bottom_layout.addWidget(widget)

        page_main_layout.addLayout(page_main_center_layout)
        page_main_layout.addLayout(page_main_bottom_layout)
        page_main.setLayout(page_main_layout)
        return page_main

    def layout_tab_main_normal(self, widgets: list):
        tab_main_normal = QtWidgets.QWidget()
        tab_main_normal_layout = QtWidgets.QHBoxLayout(tab_main_normal)
        for widget in widgets:
            tab_main_normal_layout.addWidget(widget)
        tab_main_normal.setLayout(tab_main_normal_layout)
        return tab_main_normal

    def layout_tab_main_detailed(self, widgets: list):
        tab_main_detailed = QtWidgets.QWidget()
        tab_main_detailed_layout = QtWidgets.QHBoxLayout(tab_main_detailed)
        for widget in widgets:
            tab_main_detailed_layout.addWidget(widget)
        tab_main_detailed.setLayout(tab_main_detailed_layout)
        return tab_main_detailed

    def __make_stack(self, widgets):
        """
        Make a stack of widgets
        """
        stack = QtWidgets.QStackedWidget()
        for widget in widgets:
            stack.addWidget(widget)
        return stack


# TODO: move to separate file
class Widgets:
    def __init__(self, NativeUI, *args, **kwargs):
        """
        Creates and stores references to all of the widgets we use.

        Widgets are grouped by layout for convenience, however this class deliberately contains no layout logic
        """
        self.NativeUI = NativeUI
        self.left_button_width = 150

        # Top bar widgets
        self.tab_modeswitch = TabModeswitchButton(NativeUI)
        self.tab_battery = TabBattery(NativeUI)
        self.tab_personal = TabPersonal(NativeUI)

        # Left Bar widgets
        self.tab_page_buttons = TabPageButtons(
            self.NativeUI, size=QSize(self.left_button_width, self.left_button_width)
        )
        self.tab_start_stop_buttons = TabStartStopStandbyButtons(
            self.NativeUI,
            size=QSize(self.left_button_width, int(self.left_button_width / 3)),
        )

        # Main Page Widgets
        # self.tab_expert_plots = TabExpertPlots(NativeUI)
        self.tab_spin = TabSpinButtons(NativeUI)
        self.tab_history_buttons = TabHistoryButtons(NativeUI)
        self.tab_normal_plots = TabPlots(NativeUI)
        self.tab_detailed_plots = TabPlots(NativeUI)
        self.tab_normal_measurements = TabMeasurements(NativeUI)
        self.tab_circle_plots = TabCirclePlots(NativeUI)
        self.tab_detailed_measurements = TabExpertMeasurements(NativeUI)

        # Alarm Page Widgets
        self.alarmTab = TabAlarm(NativeUI)
        self.clinicalTab = TabClinical(NativeUI)

        # Pages
        # self.main_page = MainView(self.NativeUI)
        self.settings_page = SettingsView(self.NativeUI)
        self.alarms_page = SwitchableStackWidget(
            self.NativeUI,
            [self.alarmTab, self.clinicalTab],
            ["List of Alarms", "Clinical Limits"],
        )

        # self.alarms_page = AlarmView(self.NativeUI)
        self.modes_page = ModeView(self.NativeUI)

        # Page Stack
        # self.page_stack =

    def add_widget(self, widget, name) -> int:
        setattr(self, name, widget)
        return 0
