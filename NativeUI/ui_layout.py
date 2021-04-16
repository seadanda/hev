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
from PySide2.QtGui import QFont
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

        # Define sizes
        self.top_bar_height = 75
        self.left_bar_width = 150
        self.main_page_bottom_bar_height = 150
        self.main_page_normal_measurements_width = 250
        self.main_page_detailed_measurement_width = (
            self.main_page_normal_measurements_width * 2
        )
        self.measurement_widget_size_ratio = 1 / 0.46

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
        self.widgets.plot_stack.setFont(self.NativeUI.text_font)

        # Populate the Left Bar
        hlayout.addWidget(
            self.layout_left_bar(
                [
                    self.widgets.page_buttons,
                    self.widgets.ventilator_start_stop_buttons_widget,
                ]
            )
        )
        self.widgets.page_buttons.set_size(self.left_bar_width, None)
        self.widgets.ventilator_start_stop_buttons_widget.set_size(
            self.left_bar_width, None
        )
        self.widgets.ventilator_start_stop_buttons_widget.setFont(
            self.NativeUI.text_font
        )

        # Add the page stack
        hlayout.addWidget(self.widgets.page_stack)

        # Populate the Top Bar
        vlayout.addWidget(
            self.layout_top_bar(
                [
                    self.widgets.tab_modeswitch,
                    self.widgets.personal_display,
                    self.widgets.localisation_button,
                    self.widgets.battery_display,
                ]
            )
        )
        self.widgets.battery_display.set_size(400, self.top_bar_height)
        self.widgets.personal_display.set_size(None, self.top_bar_height)
        self.widgets.battery_display.setFont(self.NativeUI.text_font)
        self.widgets.personal_display.setFont(self.NativeUI.text_font)

        vlayout.addLayout(hlayout)
        return vlayout

    def layout_page_main(self) -> QtWidgets.QWidget:
        """
        Define the page_main widget layout, populate it, and set the sizes of the
        various widgets contained.

        Setting size for subwidgets is done here so as to keep the layouts in
        layout_tab_main_normal and layout_tab_main_detailed abstracted.

        """
        # Create the normal view
        tab_main_normal = self.layout_tab_main_normal(
            [self.widgets.normal_plots, self.widgets.normal_measurements]
        )
        self.widgets.normal_measurements.set_size(  # Fix the size of the measurements
            self.main_page_normal_measurements_width,  # but allow plots to expand to
            None,  # fill the available space.
            widget_size_ratio=self.measurement_widget_size_ratio,
        )
        self.widgets.normal_measurements.set_label_font(self.NativeUI.text_font)
        self.widgets.normal_measurements.set_value_font(self.NativeUI.value_font)

        # Create the detailed view
        tab_main_detailed = self.layout_tab_main_detailed(
            [
                self.widgets.detailed_plots,
                self.widgets.detailed_measurements,
                self.widgets.circle_plots,
            ]
        )
        self.widgets.detailed_measurements.set_size(
            self.main_page_detailed_measurement_width,
            None,
            widget_size_ratio=self.measurement_widget_size_ratio,
        )
        self.widgets.detailed_measurements.set_label_font(self.NativeUI.text_font)
        self.widgets.detailed_measurements.set_value_font(self.NativeUI.value_font)

        # Put the normal and detailed views into a switchable stack
        self.widgets.add_widget(
            SwitchableStackWidget(
                self.NativeUI,
                [tab_main_normal, tab_main_detailed],
                [
                    self.NativeUI.text["button_label_main_normal"],
                    self.NativeUI.text["button_label_main_detailed"],
                ],
            ),
            "plot_stack",
        )

        # Create and populate the full page layout
        page_main = QtWidgets.QWidget()
        page_main_layout = QtWidgets.QVBoxLayout()
        page_main_center_layout = QtWidgets.QHBoxLayout()
        page_main_bottom_layout = QtWidgets.QHBoxLayout()

        center_widgets = [self.widgets.plot_stack]
        bottom_widgets = [self.widgets.history_buttons, self.widgets.spin_buttons]
        self.widgets.history_buttons.set_size(None, self.main_page_bottom_bar_height)
        self.widgets.history_buttons.setFont(self.NativeUI.text_font)
        # TODO spin_buttons sizes

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
            [
                self.widgets.alarm_tab,
                self.widgets.alarm_table_tab,
                self.widgets.clinical_tab,
            ],
            ["List of Alarms", "Alarm Table", "Clinical Limits"],
        )
        page_alarms.setFont(self.NativeUI.text_font)
        return page_alarms

    def layout_page_settings(self) -> QtWidgets.QWidget:
        """
        Layout for the settings page.
        """
        # Create the Charts tab
        tab_charts = self.layout_tab_charts(
            [self.widgets.charts_widget, self.widgets.chart_buttons_widget]
        )
        self.widgets.chart_buttons_widget.setFont(self.NativeUI.text_font)
        self.widgets.chart_buttons_widget.set_size(self.left_bar_width, None)

        # Create the stack
        page_settings = SwitchableStackWidget(
            self.NativeUI,
            [self.widgets.settings_expert_tab, tab_charts],
            ["Expert", "Charts"],
        )
        page_settings.setFont(self.NativeUI.text_font)
        self.widgets.add_widget(page_settings, "setting_stack")
        return page_settings

    def layout_page_modes(self) -> QtWidgets.QWidget:
        """
        Layout for the Modes page.
        """
        # self.widgets.add_widget(
        #     SwitchableStackWidget(
        #         self.NativeUI,
        #         [QtWidgets.QLabel("1"), QtWidgets.QLabel("2"), QtWidgets.QLabel("3"), QtWidgets.QLabel("4")],
        #         ["PC/AC", "PC/AC-PRVC", "PC-PSV", "CPAP"]
        #     ),
        #     "mode_settings_tab"
        # )

        modes_stack = SwitchableStackWidget(
            self.NativeUI,
            [self.widgets.mode_settings_tab, self.widgets.mode_personal_tab],
            ["Mode Settings", "Personal Settings"],
        )
        modes_stack.setFont(self.NativeUI.text_font)
        self.widgets.add_widget(modes_stack, "modes_stack")
        return modes_stack

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
        """
        Construct the layout for the 'normal' plots and measurements display.
        """
        tab_main_normal = QtWidgets.QWidget()
        tab_main_normal_layout = QtWidgets.QHBoxLayout(tab_main_normal)
        for widget in widgets:
            tab_main_normal_layout.addWidget(widget)
        tab_main_normal.setLayout(tab_main_normal_layout)
        return tab_main_normal

    def layout_tab_main_detailed(self, widgets: list) -> QtWidgets.QWidget:
        """
        Construct the layout for the 'detailed' plots and measurements display.
        """
        tab_main_detailed = QtWidgets.QWidget()
        tab_main_detailed_layout = QtWidgets.QHBoxLayout(tab_main_detailed)
        for widget in widgets:
            tab_main_detailed_layout.addWidget(widget)
        tab_main_detailed.setLayout(tab_main_detailed_layout)
        return tab_main_detailed

    def layout_tab_charts(self, widgets: list) -> QtWidgets.QWidget:
        tab_charts = QtWidgets.QWidget()
        tab_charts_layout = QtWidgets.QHBoxLayout(tab_charts)
        for widget in widgets:
            tab_charts_layout.addWidget(widget)
        tab_charts.setLayout(tab_charts_layout)
        return tab_charts

    def __make_stack(self, widgets):
        """
        Make a stack of widgets
        """
        stack = QtWidgets.QStackedWidget()
        for widget in widgets:
            stack.addWidget(widget)
        return stack
