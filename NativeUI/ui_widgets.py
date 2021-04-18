"""
ui_widgets.py

Creates all of the widgets used in NativeUI and stores references to them as attributes
of a single object for ease of reference
"""

__author__ = "Benjamin Mummery"
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Benjamin Mummery"
__email__ = "benjamin.mummery@stfc.ac.uk"
__status__ = "Prototype"

from PySide2.QtWidgets import QWidget, QPushButton, QRadioButton, QButtonGroup, QLabel
from global_widgets.tab_modeswitch_button import TabModeswitchButton
from global_widgets.global_spinbox import labelledSpin
from global_widgets.global_send_popup import SetConfirmPopup
from widget_library.ok_cancel_buttons_widget import OkButtonWidget, CancelButtonWidget, OkSendButtonWidget
from widget_library.history_buttons_widget import HistoryButtonsWidget
from widget_library.measurements_widget import (
    NormalMeasurementsBlockWidget,
    ExpertMeasurementsBloackWidget,
)
from widget_library.battery_display_widget import BatteryDisplayWidget

# from widget_library.tab_charts import TabChart
from widget_library.chart_buttons_widget import ChartButtonsWidget

from widget_library.page_buttons_widget import PageButtonsWidget
from widget_library.personal_display_widget import PersonalDisplayWidget
from widget_library.plot_widget import (
    ChartsPlotWidget,
    CirclePlotsWidget,
    TimePlotsWidget,
)
from widget_library.spin_buttons_widget import SpinButtonsWidget
#from widget_library.tab_expert import TabExpert
from widget_library.ventilator_start_stop_buttons_widget import (
    VentilatorStartStopButtonsWidget,
)
from widget_library.line_edit_widget import LabelledLineEditWidget
from widget_library.expert_handler import ExpertHandler
from mode_widgets.personal_handler import PersonalHandler

#from widget_library.tab_expert import TabExpert
#from widget_library.tab_charts import TabChart

#from mode_widgets.tab_modes import TabModes
#from mode_widgets.tab_personal import TabPersonal
from mode_widgets.mode_handler import ModeHandler
from alarm_widgets.alarm_handler import AlarmHandler
from alarm_widgets.alarm_list import AlarmList
from alarm_widgets.alarm_popup import AlarmPopup
from alarm_widgets.alarm_table import AlarmTable
#from alarm_widgets.tab_alarm_table import TabAlarmTable
#from alarm_widgets.tab_clinical import TabClinical

import json
import os

class Widgets:
    def __init__(self, NativeUI, *args, **kwargs):
        """
        Creates and stores references to all of the widgets we use.

        Widgets are grouped by pages for convenience, however this class deliberately
        contains no layout logic.
        """
        # self.NativeUI = NativeUI

        # Top bar widgets
        self.tab_modeswitch = TabModeswitchButton(NativeUI)
        self.battery_display = BatteryDisplayWidget(NativeUI)
        self.personal_display = PersonalDisplayWidget(NativeUI)

        # Left Bar widgets
        self.page_buttons = PageButtonsWidget(NativeUI)
        self.ventilator_start_stop_buttons_widget = VentilatorStartStopButtonsWidget(
            NativeUI
        )

        # Main Page Widgets
        self.spin_buttons = SpinButtonsWidget(NativeUI)
        self.history_buttons = HistoryButtonsWidget(NativeUI)
        self.normal_plots = TimePlotsWidget(NativeUI)
        self.detailed_plots = TimePlotsWidget(NativeUI)
        self.normal_measurements = NormalMeasurementsBlockWidget(NativeUI)
        self.circle_plots = CirclePlotsWidget(NativeUI)
        self.detailed_measurements = ExpertMeasurementsBloackWidget(NativeUI)

        # Alarm Page Widgets
        self.alarm_handler = AlarmHandler(NativeUI)
        self.alarm_popup = AlarmPopup(NativeUI)
        self.alarm_list = AlarmList(NativeUI)
        self.acknowledge_button = QPushButton()

        #self.alarm_table_tab = TabAlarmTable(NativeUI)
        self.alarm_table = AlarmTable(NativeUI)
        self.clinical_tab = QWidget()#TabClinical(NativeUI)

        #### Mode settings tab: Mode (x4), Personal

        # Modes Page Widgets
        self.mode_confirm_popup = SetConfirmPopup(NativeUI)
        self.mode_handler = ModeHandler(NativeUI, self.mode_confirm_popup)

        modeSettingsList = [
            ["Respiratory Rate","/min","respiratory_rate","SET_TARGET_","RESPIRATORY_RATE",],
            ["Inhale Time", "s", "inhale_time", "SET_TARGET_", "INHALE_TIME"],
            ["IE Ratio", "", "ie_ratio", "SET_TARGET_", "IE_RATIO"],
            ["Inhale Trigger Sensitivity","","inhale_trigger_threshold","SET_TARGET_","INHALE_TRIGGER_THRESHOLD"],
            ["Exhale Trigger Sensitivity","","exhale_trigger_threshold","SET_TARGET_","EXHALE_TRIGGER_THRESHOLD"],
            ["Inhale Pressure","","inspiratory_pressure","SET_TARGET_","INSPIRATORY_PRESSURE"],
            ["Inhale Volume", "", "volume", "SET_TARGET_", "VOLUME"],
            ["Percentage O2", "", "fiO2_percent", "SET_TARGET_", "FIO2_PERCENT"],
        ]
        modes = NativeUI.modeList
        radioSettings = ['Inhale Time', 'IE Ratio']
        self.groupDict = {}
        for mode in modes:
            self.groupDict[mode] = QButtonGroup()
            for setting in modeSettingsList:
                attrName = mode + '_' + setting[2]
                targettedSetting =[ target.replace("SET_TARGET_", "SET_TARGET_" + mode.replace("/", "_").replace("-", "_")) for target in setting]
                self.add_handled_widget(labelledSpin(NativeUI,targettedSetting),'spin_' + attrName, self.mode_handler)

                if setting[0] in radioSettings:
                    radioButton = QRadioButton()
                    self.groupDict[mode].addButton(radioButton)
                    self.add_handled_widget(radioButton,'radio_' + attrName, self.mode_handler)

            self.add_handled_widget(OkButtonWidget(NativeUI),'ok_button_' + mode, self.mode_handler)
            self.add_handled_widget(OkSendButtonWidget(NativeUI),'ok_send_button_' + mode, self.mode_handler)
            self.add_handled_widget(CancelButtonWidget(NativeUI),'cancel_button_' + mode, self.mode_handler)


        # Personal tab widgets
        self.personal_confirm_popup = SetConfirmPopup(NativeUI)
        self.personal_handler = PersonalHandler(NativeUI, self.personal_confirm_popup)
        personalSettingsList = [
            ["Name", "/min", "name", "SET_PERSONAL", "NAME"],
            ["Patient ID", "s", "patient_id", "SET_PERSONAL", "PATIENT_ID"],
            ["Age", "", "age", "SET_PERSONAL", "AGE"],
            ["Sex", "", "sex", "SET_PERSONAL", "SEX"],
            ["Weight", "", "weight", "SET_PERSONAL", "WEIGHT"],
            ["Height", "", "height", "SET_PERSONAL", "HEIGHT"],
        ]
        textBoxes = ["Name", "Patient ID", "Sex"]
        for setting in personalSettingsList:
            attrName = 'personal_edit_' + setting[2]
            if setting[0] in textBoxes:
                self.add_handled_widget(LabelledLineEditWidget(NativeUI, setting), 'text_' + attrName, self.personal_handler)
            else:
                self.add_handled_widget(labelledSpin(NativeUI, setting), 'spin_' + attrName, self.personal_handler)

        self.add_handled_widget(OkButtonWidget(NativeUI), 'ok_button_personal', self.personal_handler)
        self.add_handled_widget(OkSendButtonWidget(NativeUI), 'ok_send_button_personal', self.personal_handler)
        self.add_handled_widget(CancelButtonWidget(NativeUI), 'cancel_button_personal', self.personal_handler)

        ##### Settings Tab: Expert and Charts tabs

        # Expert Tab
        self.expert_confirm_popup = SetConfirmPopup(NativeUI)
        self.expert_handler = ExpertHandler(NativeUI, self.expert_confirm_popup)
        print(os.listdir())
        with open('NativeUI/config/controlDict.json') as json_file:
            controlDict = json.load(json_file)

        for key in controlDict:

            self.add_widget(QLabel(key),'expert_label_' + key)
            for setting in controlDict[key]:
                attrName = 'expert_spin_' + setting[2]
                self.add_handled_widget(labelledSpin(NativeUI, setting), attrName, self.expert_handler)

        self.add_handled_widget(OkButtonWidget(NativeUI), 'ok_button_expert', self.expert_handler)
        self.add_handled_widget(OkSendButtonWidget(NativeUI), 'ok_send_button_expert', self.expert_handler)
        self.add_handled_widget(CancelButtonWidget(NativeUI), 'cancel_button_expert', self.expert_handler)

        # Chart Tab
        self.charts_widget = ChartsPlotWidget(colors=NativeUI.colors)
        self.chart_buttons_widget = ChartButtonsWidget(colors=NativeUI.colors)


    def add_widget(self, widget, name) -> int:
        setattr(self, name, widget)
        return 0

    def add_handled_widget(self, widget, name, handler) -> int:
        setattr(self, name, widget)
        handler.add_widget(widget, name)
        return 0

    def get_widget(self, name) -> QWidget:
        return getattr(self, name)
