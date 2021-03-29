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
from widget_library.switchable_stack_widget import SwitchableStackWidget

# from widget_library.page_stack_widget import PageStackWidget


class Layout:
    """
    Contains all of the layout logic for the UI.

    global_layout and layout_page_* (so far main, alarms, settings, mode) are the only
    methods that should reference specific widgets, everything else should have the
    widgets passed into them. This keeps all of the widget choices at the page level.
    """

    def __init__(self, NativeUI, widgets, *args, **kwargs):
        self.NativeUI = NativeUI
        self.widgets = widgets
        self.construct_page_widgets()

    def construct_page_widgets(self) -> int:
        """
        Build all of the main pages
        """
        self.widgets.add_widget(self.layout_page_main(), "main_page")
        self.widgets.add_widget(self.layout_page_alarms(), "alarms_page")
        self.widgets.add_widget(self.layout_page_settings(), "settings_page")
        self.widgets.add_widget(self.layout_page_modes(), "modes_page")

        return 0

    def global_layout(self):
        hlayout = QtWidgets.QHBoxLayout()
        vlayout = QtWidgets.QVBoxLayout()

        # Define the stack of pages (used by the page buttons to set the current page)
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

        # Populate the Left Bar
        hlayout.addWidget(
            self.layout_left_bar(
                [
                    self.widgets.page_buttons,
                    self.widgets.ventilator_start_stop_buttons_widget,
                ]
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
                    self.widgets.battery_display,
                ]
            )
        )

        vlayout.addLayout(hlayout)
        return vlayout

    def layout_page_main(self) -> QtWidgets.QWidget:
        page_main = QtWidgets.QWidget()
        page_main_layout = QtWidgets.QVBoxLayout()
        page_main_center_layout = QtWidgets.QHBoxLayout()
        page_main_bottom_layout = QtWidgets.QHBoxLayout()

        tab_main_normal = self.layout_tab_main_normal(
            [self.widgets.normal_plots, self.widgets.normal_measurements]
        )
        tab_main_detailed = self.layout_tab_main_detailed(
            [
                self.widgets.detailed_plots,
                self.widgets.detailed_measurements,
                self.widgets.circle_plots,
            ]
        )

        plot_stack = SwitchableStackWidget(
            self.NativeUI,
            [tab_main_normal, tab_main_detailed],
            [
                self.NativeUI.text["button_label_main_normal"],
                self.NativeUI.text["button_label_main_detailed"],
            ],
        )

        center_widgets = [plot_stack]
        bottom_widgets = [self.widgets.history_buttons, self.widgets.spin_buttons]

        for widget in center_widgets:
            page_main_center_layout.addWidget(widget)
        for widget in bottom_widgets:
            page_main_bottom_layout.addWidget(widget)

        page_main_layout.addLayout(page_main_center_layout)
        page_main_layout.addLayout(page_main_bottom_layout)
        page_main.setLayout(page_main_layout)
        return page_main

    def layout_page_alarms(self) -> QtWidgets.QWidget:
        """
        Layout for the alarms page.
        """
        page_alarms = SwitchableStackWidget(
            self.NativeUI,
            [self.widgets.alarmTab, self.widgets.clinicalTab],
            ["List of Alarms", "Clinical Limits"],
        )
        return page_alarms

    def layout_page_settings(self) -> QtWidgets.QWidget:
        """
        Layout for the settings page.
        """
        page_settings = SwitchableStackWidget(
            self.NativeUI,
            [self.widgets.settings_expert_tab, self.widgets.settings_chart_tab],
            ["Expert", "Charts"],
        )
        self.NativeUI.widgets.add_widget(page_settings, "setting_stack")
        return page_settings

    def layout_page_modes(self) -> QtWidgets.QWidget:
        page_modes = SwitchableStackWidget(
            self.NativeUI,
            [self.widgets.mode_settings_tab, self.widgets.mode_personal_tab],
            ["Mode Settings", "Personal Settings"],
        )
        return page_modes

    def layout_top_bar(self, widgets: list) -> QtWidgets.QWidget:
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

    def layout_left_bar(self, widgets: list) -> QtWidgets.QWidget:
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

    def layout_tab_main_normal(self, widgets: list) -> QtWidgets.QWidget:
        tab_main_normal = QtWidgets.QWidget()
        tab_main_normal_layout = QtWidgets.QHBoxLayout(tab_main_normal)
        for widget in widgets:
            tab_main_normal_layout.addWidget(widget)
        tab_main_normal.setLayout(tab_main_normal_layout)
        return tab_main_normal

    def layout_tab_main_detailed(self, widgets: list) -> QtWidgets.QWidget:
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
