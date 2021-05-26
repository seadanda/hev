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

from PySide2 import QtWidgets, QtCore, QtGui

# from PySide2.QtGui import QFont, QSizePolicy
from widget_library.switchable_stack_widget import SwitchableStackWidget
import json

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
        self.text_font = NativeUI.text_font
        self.screen_width = NativeUI.screen_width
        self.screen_height = NativeUI.screen_height

        # Define sizes
        # Global
        self.widget_spacing = max(
            [int(self.screen_height / 192), 5]
        )  # 10 for 1920x1080
        self.measurement_widget_size_ratio = 1 / 0.46
        self.top_bar_height = int(self.screen_height / 14.4)  # 75 for 1920x1080
        self.left_bar_width = int(self.screen_width / 12.8)  # 150 for 1920x1080

        # main page
        self.main_page_bottom_bar_height = int(
            self.screen_height / 7.2
        )  # 150 for 1920x1080
        self.main_page_normal_measurements_width = int(
            self.screen_width / 7.68
        )  # 250 for 1920x1080
        self.main_page_detailed_measurement_width = (
            self.main_page_normal_measurements_width * 2
        )

        self.construct_page_widgets()

        # Popups
        NativeUI.widgets.alarm_popup.setFont(self.NativeUI.text_font)

    def construct_page_widgets(self) -> int:
        """
        Build all of the main pages
        """
        self.widgets.add_widget(self.layout_page_main(), "main_page")
        self.widgets.add_widget(self.layout_page_alarms(), "alarms_page")
        self.widgets.add_widget(self.layout_page_settings(), "settings_page")
        self.widgets.add_widget(self.layout_page_modes(), "modes_page")

        return 0

    def startup_layout(self):
        v_layout = QtWidgets.QVBoxLayout()
        h_layout = QtWidgets.QHBoxLayout()
        h_button_layout = QtWidgets.QHBoxLayout()

        # Stack the data collection pages.
        self.widgets.add_widget(
            SwitchableStackWidget(
                self.NativeUI.colors,
                self.NativeUI.text,
                [
                    self.layout_mode_startup(),
                    self.layout_mode_personal("startup_", False),
                    self.layout_startup_confirmation(),
                ],
                [
                    "button_label_modes_mode",
                    "button_label_modes_personal",
                    "button_label_modes_summary",
                ],
            ),
            "startup_stack",
        )
        self.widgets.startup_stack.setFont(self.NativeUI.text_font)

        # Add buttons
        h_button_layout.addWidget(self.NativeUI.widgets.backButton)
        h_button_layout.addWidget(self.NativeUI.widgets.skipButton)
        h_button_layout.addWidget(self.NativeUI.widgets.nextButton)

        # Put the layouts together
        h_layout.addWidget(self.layout_startup_main())
        h_layout.addWidget(self.widgets.startup_stack)
        v_layout.addLayout(h_layout)
        v_layout.addLayout(h_button_layout)

        # Ensure that next and skip buttons are disabled by default.
        self.NativeUI.widgets.skipButton.setEnabled(False)
        self.NativeUI.widgets.nextButton.setEnabled(False)

        return v_layout

    def layout_startup_main(self):
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(self.widgets.calibration)
        vlayout.addWidget(self.widgets.leak_test)
        vlayout.addWidget(self.widgets.maintenance)
        widg = QtWidgets.QWidget()
        widg.setLayout(vlayout)
        return widg

    def global_layout(self):
        hlayout = QtWidgets.QHBoxLayout()
        vlayout = QtWidgets.QVBoxLayout()

        # Define Sizes
        f_mode = 0.25
        f_battery = 0.2
        f_localisation = 0.1
        f_personal = 1 - (f_mode + f_battery + f_localisation)

        mode_display_width = int(self.screen_width * f_mode)
        personal_display_width = int(self.screen_width * f_personal)
        localisation_display_width = int(self.screen_width * f_localisation)
        battery_display_width = int(self.screen_width * f_battery)

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
        self.widgets.page_buttons.set_size(
            self.left_bar_width, None, spacing=self.widget_spacing
        )
        self.widgets.ventilator_start_stop_buttons_widget.set_size(
            self.left_bar_width, None, spacing=self.widget_spacing
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

        self.widgets.tab_modeswitch.set_size(
            mode_display_width, self.top_bar_height, spacing=self.widget_spacing
        )
        # self.widgets.tab_modeswitch.setFont()
        self.widgets.personal_display.set_size(
            personal_display_width, self.top_bar_height, spacing=self.widget_spacing
        )
        self.widgets.personal_display.setFont(self.NativeUI.text_font)
        self.widgets.localisation_button.set_size(
            localisation_display_width, self.top_bar_height, spacing=self.widget_spacing
        )
        self.widgets.localisation_button.setFont(self.NativeUI.text_font)
        self.widgets.battery_display.set_size(
            battery_display_width, self.top_bar_height, spacing=self.widget_spacing
        )
        self.widgets.battery_display.setFont(self.NativeUI.text_font)

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
            spacing=self.widget_spacing,
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
                self.NativeUI.colors,
                self.NativeUI.text,
                [tab_main_normal, tab_main_detailed],
                ["button_label_main_normal", "button_label_main_detailed"],
            ),
            "plot_stack",
        )

        # Create and populate the full page layout
        page_main = QtWidgets.QWidget()
        page_main_layout = QtWidgets.QVBoxLayout()
        page_main_center_layout = QtWidgets.QHBoxLayout()
        page_main_bottom_layout = QtWidgets.QHBoxLayout()

        spin_buttons = self.layout_main_spin_buttons()
        center_widgets = [self.widgets.plot_stack]
        bottom_widgets = [self.widgets.history_buttons, spin_buttons]
        self.widgets.history_buttons.set_size(
            None, self.main_page_bottom_bar_height, spacing=self.widget_spacing
        )
        self.widgets.history_buttons.setFont(self.NativeUI.text_font)

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
        alarm_tab_widgets = [self.widgets.alarm_list, self.widgets.acknowledge_button]

        alarm_table_tab_widgets = [self.widgets.alarm_table]

        page_alarms = SwitchableStackWidget(
            self.NativeUI.colors,
            self.NativeUI.text,
            [
                self.layout_tab_alarm_list(alarm_tab_widgets),
                self.layout_tab_alarm_table(alarm_table_tab_widgets),
                self.layout_tab_clinical_limits(),
            ],
            [
                "button_label_alarms_list",
                "button_label_alarms_table",
                "button_label_alarms_clinical",
            ],
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
        self.widgets.chart_buttons_widget.set_size(
            self.left_bar_width, None, spacing=self.widget_spacing
        )

        # Create the system info tab
        sysinfo_widgets = [
            self.widgets.version_display_widget,
            self.widgets.maintenance_time_display_widget,
            self.widgets.update_time_display_widget,
        ]
        tab_info = self.layout_tab_info(sysinfo_widgets)
        for widget in sysinfo_widgets:
            widget.setFont(self.NativeUI.text_font)

        # Create the stack
        page_settings = SwitchableStackWidget(
            self.NativeUI.colors,
            self.NativeUI.text,
            [self.layout_settings_expert(), tab_charts, tab_info],
            [
                "button_label_settings_expert",
                "button_label_settings_charts",
                "button_label_settings_info",
            ],
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
            self.NativeUI.colors,
            self.NativeUI.text,
            [
                self.layout_mode_settings(True),
                self.layout_mode_personal("", True),
            ],  # self.widgets.mode_personal_tab],
            ["button_label_modes_mode", "button_label_modes_personal"],
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
        """
        Construct the layout for the charts page.
        """
        tab_charts = QtWidgets.QWidget()
        tab_charts_layout = QtWidgets.QHBoxLayout(tab_charts)
        for widget in widgets:
            tab_charts_layout.addWidget(widget)
        tab_charts.setLayout(tab_charts_layout)
        return tab_charts

    def layout_tab_info(self, widgets: list) -> QtWidgets.QWidget:
        """
        Construct the layout for the info page.
        """
        tab_info = QtWidgets.QWidget()
        tab_info_layout = QtWidgets.QVBoxLayout(tab_info)
        for widget in widgets:
            tab_info_layout.addWidget(widget)
        tab_info.setLayout(tab_info_layout)
        return tab_info

    def __make_stack(self, widgets):
        """
        Make a stack of widgets
        """
        stack = QtWidgets.QStackedWidget()
        for widget in widgets:
            stack.addWidget(widget)
        return stack

    def layout_tab_alarm_list(self, widgets: list) -> QtWidgets.QWidget:
        """
        Construct the layout for the 'normal' plots and measurements display.
        """
        tab_alarm_list = QtWidgets.QWidget()
        tab_alarm_list_layout = QtWidgets.QHBoxLayout(tab_alarm_list)
        for widget in widgets:
            tab_alarm_list_layout.addWidget(widget)
        tab_alarm_list.setLayout(tab_alarm_list_layout)
        return tab_alarm_list

    def layout_tab_alarm_table(self, widgets: list) -> QtWidgets.QWidget:
        """
        Construct the layout for the 'normal' plots and measurements display.
        """
        tab_alarm_table = QtWidgets.QWidget()
        tab_alarm_table_layout = QtWidgets.QHBoxLayout(tab_alarm_table)
        for widget in widgets:
            tab_alarm_table_layout.addWidget(widget)
        tab_alarm_table.setLayout(tab_alarm_table_layout)
        return tab_alarm_table

    def layout_mode_settings(self, buttons) -> QtWidgets.QWidget:
        """
        Construct the layout for the mode pages
        """
        mode_pages = []  # enableDict may need to go elsewhere
        with open("NativeUI/configs/mode_config.json") as json_file:
            modeDict = json.load(json_file)

        enableDict = modeDict["enableDict"]
        buttons = True
        for mode in self.NativeUI.modeList:
            mode_pages.append(
                self.layout_mode_tab(
                    modeDict["settings"], mode, "", enableDict[mode], buttons
                )
            )

        page_modes = SwitchableStackWidget(
            self.NativeUI.colors, self.NativeUI.text, mode_pages, self.NativeUI.modeList
        )
        self.widgets.add_widget(page_modes, "mode_settings_stack")

        page_modes.setFont(self.NativeUI.text_font)
        return page_modes

    def layout_mode_tab(
        self, settings, mode: str, startup: str, enableList: list, buttons: bool
    ) -> QtWidgets.QWidget:
        """
        Construct the layout for an individual mode setting tab
        """
        spinList = []
        for setting in settings:
            attrName = "spin_" + mode + startup + "_" + setting[2]
            spinList.append(self.NativeUI.widgets.get_widget(attrName))

        if len(spinList) != len(enableList):
            print("lengths do not match, error!")
            print(spinList)
            print(enableList)
        radioWidgets = ["Inhale Time", "IE Ratio"]

        vLayout = QtWidgets.QVBoxLayout()
        for widget, enableBool in zip(spinList, enableList):
            vLayout.addWidget(widget)

            if widget.label in radioWidgets:
                self.NativeUI.widgets.get_widget(
                    "radio_" + mode + startup + "_" + widget.tag
                ).setChecked(bool(enableBool))
                self.NativeUI.widgets.get_widget(
                    "spin_" + mode + startup + "_" + widget.tag
                ).insertWidget(
                    self.NativeUI.widgets.get_widget(
                        "radio_" + mode + startup + "_" + widget.tag
                    ),
                    1,
                )
                self.NativeUI.widgets.get_widget(
                    "spin_" + mode + startup + "_" + widget.tag
                ).setEnabled(bool(enableBool))

        if buttons == True:
            hButtonLayout = QtWidgets.QHBoxLayout()
            hButtonLayout.addWidget(
                self.NativeUI.widgets.get_widget("ok_button_" + mode)
            )
            hButtonLayout.addWidget(
                self.NativeUI.widgets.get_widget("ok_send_button_" + mode)
            )
            hButtonLayout.addWidget(
                self.NativeUI.widgets.get_widget("cancel_button_" + mode)
            )

            vLayout.addLayout(hButtonLayout)

        mode_tab = QtWidgets.QWidget()
        mode_tab.setLayout(vLayout)
        return mode_tab

    def layout_mode_startup(self) -> QtWidgets.QWidget:
        """
        Construct the layout for the mode pages
        """

        mode_pages = []  # enableDict may need to go elsewhere
        with open("NativeUI/configs/mode_config.json") as json_file:
            modeDict = json.load(json_file)

        enableDict = modeDict["enableDict"]
        for mode in self.NativeUI.modeList:
            mode_pages.append(
                self.layout_mode_tab(
                    modeDict["settings"], mode, "_startup", enableDict[mode], False
                )
            )

        mode_stack = SwitchableStackWidget(
            self.NativeUI.colors, self.NativeUI.text, mode_pages, self.NativeUI.modeList
        )
        mode_stack.setFont(self.NativeUI.text_font)
        self.widgets.add_widget(mode_stack, "mode_settings_stack_startup")

        hRadioLayout = QtWidgets.QHBoxLayout()
        for mode in self.NativeUI.modeList:
            hRadioLayout.addWidget(
                self.NativeUI.widgets.get_widget("startup_radio_" + mode)
            )

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addWidget(mode_stack)
        vlayout.addLayout(hRadioLayout)
        page_modes = QtWidgets.QWidget()
        page_modes.setLayout(vlayout)

        return page_modes

    def layout_mode_personal(self, startup: str, buttons: bool):
        """
        Construct the layout for the personal settings page
        """
        with open("NativeUI/configs/personal_config.json") as json_file:
            personalDict = json.load(json_file)
        textBoxes = personalDict["textBoxes"]

        personalList = []

        for setting in personalDict["settings"]:
            attrName = startup + "personal_edit_" + setting[2]
            if setting[0] in textBoxes:
                personalList.append(
                    self.NativeUI.widgets.get_widget("text_" + attrName)
                )
            else:
                personalList.append(
                    self.NativeUI.widgets.get_widget("spin_" + attrName)
                )

        vLayout = QtWidgets.QVBoxLayout()
        for widget in personalList:
            vLayout.addWidget(widget)

        if buttons:
            hButtonLayout = QtWidgets.QHBoxLayout()
            hButtonLayout.addWidget(
                self.NativeUI.widgets.get_widget("ok_button_personal")
            )
            hButtonLayout.addWidget(
                self.NativeUI.widgets.get_widget("ok_send_button_personal")
            )
            hButtonLayout.addWidget(
                self.NativeUI.widgets.get_widget("cancel_button_personal")
            )

            vLayout.addLayout(hButtonLayout)

        personal_tab = QtWidgets.QWidget()
        personal_tab.setLayout(vLayout)
        return personal_tab

    def layout_settings_expert(self):
        """
        Construct the layout for the expert settings page, reads controlDict.json to do so
        """
        vlayout = QtWidgets.QVBoxLayout()
        i = 0
        with open("NativeUI/configs/expert_config.json") as json_file:
            controlDict = json.load(json_file)
        for key in controlDict.keys():
            titleLabel = self.NativeUI.widgets.get_widget("expert_label_" + key)
            titleLabel.setStyleSheet(
                "background-color:"
                + self.NativeUI.colors["page_background"].name()
                + ";"
                "color:" + self.NativeUI.colors["page_foreground"].name() + ";"
            )
            titleLabel.setFont(self.text_font)
            titleLabel.setAlignment(QtCore.Qt.AlignCenter)
            vlayout.addWidget(titleLabel)

            grid = QtWidgets.QGridLayout()
            grid.setMargin(0)
            grid.setSpacing(0)
            widg = QtWidgets.QFrame()
            widg.setStyleSheet(
                "QFrame{"
                "    border: 2px solid"
                + self.NativeUI.colors["page_foreground"].name()
                + ";"
                "}"
                "QLabel{"
                "    border:none;"
                "} "
            )
            j = -1
            for boxInfo in controlDict[key]:
                j = j + 1
                grid.addWidget(
                    self.NativeUI.widgets.get_widget("expert_spin_" + boxInfo[2]),
                    i + 1 + int(j / 3),
                    2 * (j % 3),
                    1,
                    2,
                )

            widg.setLayout(grid)

            vlayout.addWidget(widg)

            i = i + 1 + int(j / 3) + 1
        expert_tab = QtWidgets.QWidget()
        expert_tab.setLayout(vlayout)

        hButtonLayout = QtWidgets.QHBoxLayout()
        hButtonLayout.addWidget(self.NativeUI.widgets.get_widget("ok_button_expert"))
        hButtonLayout.addWidget(
            self.NativeUI.widgets.get_widget("ok_send_button_expert")
        )
        hButtonLayout.addWidget(
            self.NativeUI.widgets.get_widget("cancel_button_expert")
        )

        vlayout.addLayout(hButtonLayout)

        passlock_stack = QtWidgets.QStackedWidget()
        passlock_stack.addWidget(self.NativeUI.widgets.expert_password_widget)
        passlock_stack.addWidget(expert_tab)
        # break this here
        return passlock_stack  # expert_tab

    def layout_main_spin_buttons(self) -> QtWidgets.QWidget:
        hlayout = QtWidgets.QHBoxLayout()
        with open("NativeUI/configs/mode_config.json") as json_file:
            modeDict = json.load(json_file)

        stack = self.NativeUI.widgets.main_mode_stack
        for setting in modeDict["settings"]:
            if setting[0] in modeDict["mainPageSettings"]:
                attrName = "CURRENT_" + setting[2]
                widg = self.NativeUI.widgets.get_widget(attrName)
                if setting[0] in modeDict["radioSettings"]:
                    stack.addWidget(widg)
                else:
                    hlayout.addWidget(widg)
        hlayout.addWidget(self.NativeUI.widgets.main_mode_stack)

        vbuttonLayout = QtWidgets.QVBoxLayout()
        okButton = self.NativeUI.widgets.get_widget("CURRENT_ok_button")
        okButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        vbuttonLayout.addWidget(okButton)

        cancelButton = self.NativeUI.widgets.get_widget("CURRENT_cancel_button")
        cancelButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        vbuttonLayout.addWidget(cancelButton)
        hlayout.addLayout(vbuttonLayout)

        combined_spin_buttons = QtWidgets.QWidget()
        combined_spin_buttons.setLayout(hlayout)

        x = self.screen_width - self.left_bar_width - self.main_page_bottom_bar_height
        y = self.main_page_bottom_bar_height
        spacing = self.widget_spacing

        combined_spin_buttons.setFixedSize(x, y)
        x_spin = int(x / hlayout.count() - spacing)
        y_spin = y - spacing

        for setting in modeDict["settings"]:
            if setting[0] in modeDict["mainPageSettings"]:
                attrName = "CURRENT_" + setting[2]
                self.NativeUI.widgets.get_widget(attrName).setFixedSize(x_spin, y_spin)
                self.NativeUI.widgets.get_widget(attrName).simpleSpin.setFixedSize(
                    x_spin, 0.7 * y_spin
                )
                self.NativeUI.widgets.get_widget(attrName).simpleSpin.setFont(
                    self.NativeUI.text_font
                )
                self.NativeUI.widgets.get_widget(attrName).label.setFont(
                    self.NativeUI.text_font
                )

        stack.setFixedSize(x_spin, y_spin)
        cancelButton.setFixedSize(x_spin, int(y_spin / 2) - spacing)
        okButton.setFixedSize(x_spin, int(y_spin / 2) - spacing)

        # spin_buttons.set_label_font(self.NativeUI.text_font)
        # spin_buttons.set_value_font(self.NativeUI.value_font

        return combined_spin_buttons

    def layout_tab_clinical_limits(self):
        with open("NativeUI/configs/clinical_config.json") as json_file:
            clinicalDict = json.load(json_file)

        vlayout = QtWidgets.QVBoxLayout()
        for setting in clinicalDict["settings"]:
            attrName = "clinical_spin_" + setting[0][2]
            hlayout = QtWidgets.QHBoxLayout()
            if len(setting) >= 2:
                hlayout.addWidget(self.NativeUI.widgets.get_widget(attrName + "_min"))
                if len(setting) == 3:
                    hlayout.addWidget(
                        self.NativeUI.widgets.get_widget(attrName + "_set")
                    )
                hlayout.addWidget(self.NativeUI.widgets.get_widget(attrName + "_max"))
            elif len(setting) == 1:
                hlayout.addWidget(self.NativeUI.widgets.get_widget(attrName + "_lim"))

            vlayout.addLayout(hlayout)

        hbuttonlayout = QtWidgets.QHBoxLayout()
        hbuttonlayout.addWidget(self.NativeUI.widgets.get_widget("clinical_ok_button"))
        hbuttonlayout.addWidget(
            self.NativeUI.widgets.get_widget("clinical_cancel_button")
        )
        vlayout.addLayout(hbuttonlayout)
        clinical_page = QtWidgets.QWidget()
        clinical_page.setLayout(vlayout)
        return clinical_page

    def layout_startup_confirmation(self):
        vlayout = QtWidgets.QVBoxLayout()
        i = 0
        for key, spinBox in self.NativeUI.widgets.get_widget(
            "startup_handler"
        ).spinDict.items():
            i = i + 1
            hlayout = QtWidgets.QHBoxLayout()
            nameLabel = QtWidgets.QLabel(key)
            valLabel = QtWidgets.QLabel(str(spinBox.get_value()))
            hlayout.addWidget(nameLabel)
            hlayout.addWidget(valLabel)
            vlayout.addLayout(hlayout)
            if i == 10:
                break

        widg = QtWidgets.QWidget()
        widg.setLayout(vlayout)
        return widg
