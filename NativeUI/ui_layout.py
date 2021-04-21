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

from PySide2 import QtWidgets, QtCore
from PySide2.QtGui import QFont
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

        #self.startup_layout()


    def construct_page_widgets(self) -> int:
        """
        Build all of the main pages
        """
        self.widgets.add_widget(self.layout_page_main(), "main_page")
        self.widgets.add_widget(self.layout_page_alarms(), "alarms_page")
        self.widgets.add_widget(self.layout_page_settings(), "settings_page")
        self.widgets.add_widget(self.layout_page_modes(), "modes_page")

        return 0

    # def construct_startup_widgets(self) -> int:
    #     self.widgets.add_widget(
    #         self.__make_stack(
    #             [
    #
    #                 self.layout_mode_settings(),
    #                 self.layout_mode_personal(),self.layout_startup_main()
    #             ]
    #         ),
    #         "startup_stack",
    #     )
    #     self.widgets.startup_stack.show()

    def startup_layout(self):
        vlayout = QtWidgets.QVBoxLayout()
        with open('NativeUI/configs/mode_config.json') as json_file:
            modeDict = json.load(json_file)

        # Define the stack of pages (used by the page buttons to set the current page)
        self.widgets.add_widget(
            self.__make_stack(
                [
                    self.layout_startup_main(),
                    self.layout_mode_startup(modeDict["settings"], 'startup', modeDict['enableDict']['PC/AC'], False ),#self, settings, mode:str, enableList:list, buttons: bool)
                    self.layout_personal_startup(),

                ]
            ),
            "startup_stack",
        )
        self.widgets.startup_stack.setFont(self.NativeUI.text_font)
        vlayout.addWidget(self.widgets.startup_stack)
        hButtonLayout = QtWidgets.QHBoxLayout()
        hButtonLayout.addWidget(self.NativeUI.widgets.backButton)
        hButtonLayout.addWidget(self.NativeUI.widgets.skipButton)
        hButtonLayout.addWidget(self.NativeUI.widgets.nextButton)



        vlayout.addLayout(hButtonLayout)

        return vlayout


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
        alarm_tab_widgets = [self.widgets.alarm_list, self.widgets.acknowledge_button]

        alarm_table_tab_widgets = [self.widgets.alarm_table]

        page_alarms = SwitchableStackWidget(
            self.NativeUI,
            [self.layout_tab_alarm_list(alarm_tab_widgets), self.layout_tab_alarm_table(alarm_table_tab_widgets), self.widgets.clinical_tab],
            ["List of Alarms", "Alarm Table", "Clinical Limits"],
        )
        page_alarms.setFont(self.NativeUI.text_font)
        return page_alarms
        # page_alarms = SwitchableStackWidget(
        #     self.NativeUI,
        #     [self.widgets.alarm_tab, self.widgets.alarm_table_tab, self.widgets.clinical_tab],
        #     ["List of Alarms", "Alarm Table", "Clinical Limits"],
        # )
        # page_alarms.setFont(self.NativeUI.text_font)
        # return page_alarms

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
            [self.layout_settings_expert(), tab_charts],
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
            [self.layout_mode_settings(True), self.layout_mode_personal()],#self.widgets.mode_personal_tab],
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

        mode_pages = [] # enableDict may need to go elsewhere
        with open('NativeUI/configs/mode_config.json') as json_file:
            modeDict = json.load(json_file)

        enableDict = modeDict["enableDict"]
        #enableDict = {'PC/AC':[1, 0, 1, 1, 0, 1, 0, 1], 'PC/AC-PRVC':[1, 1, 0, 1, 0, 1, 1, 1], 'PC-PSV':[1, 1, 0, 1, 0, 1, 0, 1], 'CPAP':[1, 0, 1, 1, 0, 1, 0, 1]}
        #buttons = True
        for mode in self.NativeUI.modeList:
            mode_pages.append(self.layout_mode_tab(modeDict["settings"], mode, enableDict[mode], buttons))

        page_modes = SwitchableStackWidget(
            self.NativeUI,
            mode_pages,
            self.NativeUI.modeList,
        )
        page_modes.setFont(self.NativeUI.text_font)
        return page_modes

    def layout_mode_tab(self, settings, mode:str, enableList:list, buttons: bool) -> QtWidgets.QWidget:
        """
        Construct the layout for an individual mode setting tab
        """


        spinList = []
        for setting in settings:
            attrName = 'spin_' + mode + '_' + setting[2]
            spinList.append(self.NativeUI.widgets.get_widget(attrName))

        #spinList = [ self.NativeUI.widgets.get_widget(attrName) for attrName in dir(self.NativeUI.widgets) if ('spin_' + mode + '_') in attrName]
        # consider subclassing labelledspinbox to have modespinbox with attribute mode
        if len(spinList) != len(enableList):
            print('lengths do not match, error!')
            print(spinList)
            print(enableList)
        radioWidgets = ["Inhale Time", "IE Ratio"]
        buttonGroup = QtWidgets.QButtonGroup()

        vLayout = QtWidgets.QVBoxLayout()
        for widget, enableBool in zip(spinList,enableList):
            vLayout.addWidget(widget)

            if widget.label in radioWidgets:
                self.NativeUI.widgets.get_widget('radio_' + mode + '_' +widget.tag).setChecked(bool(enableBool))
                self.NativeUI.widgets.get_widget('spin_' + mode + '_' +widget.tag).insertWidget(self.NativeUI.widgets.get_widget('radio_' + mode + '_' +widget.tag), 1)
                self.NativeUI.widgets.get_widget('spin_' + mode + '_' + widget.tag).setEnabled(bool(enableBool))

        if buttons == True:
            hButtonLayout = QtWidgets.QHBoxLayout()
            hButtonLayout.addWidget(self.NativeUI.widgets.get_widget('ok_button_' + mode))
            hButtonLayout.addWidget(self.NativeUI.widgets.get_widget('ok_send_button_' + mode))
            hButtonLayout.addWidget(self.NativeUI.widgets.get_widget('cancel_button_' + mode))

            vLayout.addLayout(hButtonLayout)

        mode_tab = QtWidgets.QWidget()
        mode_tab.setLayout(vLayout)
        return mode_tab

    def layout_mode_startup(self, settings, mode:str, enableList:list, buttons: bool) -> QtWidgets.QWidget:
        """
        Construct the layout for an individual mode setting tab
        """


        spinList = []
        for setting in settings:
            attrName = 'spin_' + mode + '_' + setting[2]
            spinList.append(self.NativeUI.widgets.get_widget(attrName))

        #spinList = [ self.NativeUI.widgets.get_widget(attrName) for attrName in dir(self.NativeUI.widgets) if ('spin_' + mode + '_') in attrName]
        # consider subclassing labelledspinbox to have modespinbox with attribute mode
        if len(spinList) != len(enableList):
            print('lengths do not match, error!')
            print(spinList)
            print(enableList)
        radioWidgets = ["Inhale Time", "IE Ratio"]
        buttonGroup = QtWidgets.QButtonGroup()

        vLayout = QtWidgets.QVBoxLayout()
        for widget, enableBool in zip(spinList,enableList):
            vLayout.addWidget(widget)

            if widget.label in radioWidgets:
                self.NativeUI.widgets.get_widget('radio_' + mode + '_' +widget.tag).setChecked(bool(enableBool))
                self.NativeUI.widgets.get_widget('spin_' + mode + '_' +widget.tag).insertWidget(self.NativeUI.widgets.get_widget('radio_' + mode + '_' +widget.tag), 1)
                self.NativeUI.widgets.get_widget('spin_' + mode + '_' + widget.tag).setEnabled(bool(enableBool))

        if buttons == True:
            hButtonLayout = QtWidgets.QHBoxLayout()
            hButtonLayout.addWidget(self.NativeUI.widgets.get_widget('ok_button_' + mode))
            hButtonLayout.addWidget(self.NativeUI.widgets.get_widget('ok_send_button_' + mode))
            hButtonLayout.addWidget(self.NativeUI.widgets.get_widget('cancel_button_' + mode))

            vLayout.addLayout(hButtonLayout)

        mode_tab = QtWidgets.QWidget()
        mode_tab.setLayout(vLayout)
        return mode_tab

    def layout_personal_startup(self):
        with open('NativeUI/configs/personal_config.json') as json_file:
            personalDict = json.load(json_file)
        textBoxes = personalDict["textBoxes"]

        personalList = [self.NativeUI.widgets.get_widget(attrName) for attrName in dir(self.NativeUI.widgets) if
                        'startup_personal_edit' in attrName]
        # consider subclassing labelledspinbox to have modespinbox with attribute mode

        vLayout = QtWidgets.QVBoxLayout()
        for widget in personalList:
            vLayout.addWidget(widget)

        personal_tab = QtWidgets.QWidget()
        personal_tab.setLayout(vLayout)
        return personal_tab

    def layout_mode_personal(self):
        """
        Construct the layout for the personal settings page
        """
        with open('NativeUI/configs/personal_config.json') as json_file:
            personalDict = json.load(json_file)
        textBoxes = personalDict["textBoxes"]

        personalList = [self.NativeUI.widgets.get_widget(attrName) for attrName in dir(self.NativeUI.widgets) if 'personal_edit' in attrName]
        # consider subclassing labelledspinbox to have modespinbox with attribute mode

        vLayout = QtWidgets.QVBoxLayout()
        for widget in personalList:
            vLayout.addWidget(widget)

        hButtonLayout = QtWidgets.QHBoxLayout()
        hButtonLayout.addWidget(self.NativeUI.widgets.get_widget('ok_button_personal'))
        hButtonLayout.addWidget(self.NativeUI.widgets.get_widget('ok_send_button_personal'))
        hButtonLayout.addWidget(self.NativeUI.widgets.get_widget('cancel_button_personal'))

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
        with open('NativeUI/configs/expert_config.json') as json_file:
            controlDict = json.load(json_file)
        for key in controlDict.keys():
            titleLabel = self.NativeUI.widgets.get_widget('expert_label_' + key)
            titleLabel.setStyleSheet(
                "background-color:"
                + self.NativeUI.colors["page_background"].name()
                + ";"
                "color:" + self.NativeUI.colors["page_foreground"].name() + ";"
                "font-size: " + self.NativeUI.text_size + ";"
            )
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
                    self.NativeUI.widgets.get_widget('expert_spin_' + boxInfo[2]), i + 1 + int(j / 3), 2 * (j % 3), 1, 2
                )

            widg.setLayout(grid)

            vlayout.addWidget(widg)

            i = i + 1 + int(j / 3) + 1
        expert_tab = QtWidgets.QWidget()
        expert_tab.setLayout(vlayout)

        hButtonLayout = QtWidgets.QHBoxLayout()
        hButtonLayout.addWidget(self.NativeUI.widgets.get_widget('ok_button_expert'))
        hButtonLayout.addWidget(self.NativeUI.widgets.get_widget('ok_send_button_expert'))
        hButtonLayout.addWidget(self.NativeUI.widgets.get_widget('cancel_button_expert'))

        vlayout.addLayout(hButtonLayout)

        return expert_tab
