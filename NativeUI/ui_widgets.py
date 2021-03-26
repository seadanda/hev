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

from PySide2.QtCore import QSize
from global_widgets.tab_modeswitch_button import TabModeswitchButton
from widget_library.history_buttons_widget import HistoryButtonsWidget
from widget_library.measurements_widget import (
    NormalMeasurementsBlockWidget,
    ExpertMeasurementsBloackWidget,
)
from widget_library.plot_widget import TimePlotsWidget, CirclePlotsWidget
from widget_library.spin_buttons_widget import SpinButtonsWidget
from widget_library.page_buttons_widget import PageButtonsWidget
from widget_library.personal_display_widget import PersonalDisplayWidget
from widget_library.battery_display_widget import BatteryDisplayWidget
from widget_library.ventilator_start_stop_buttons_widget import (
    VentilatorStartStopButtonsWidget,
)
from settings_widgets.tab_charts import TabChart
from settings_widgets.tab_expert import TabExpert
from mode_widgets.tab_modes import TabModes
from mode_widgets.tab_personal import TabPersonal
from alarm_widgets.tab_alarms import TabAlarm
from alarm_widgets.tab_clinical import TabClinical


class Widgets:
    def __init__(self, NativeUI, *args, **kwargs):
        """
        Creates and stores references to all of the widgets we use.

        Widgets are grouped by pages for convenience, however this class deliberately
        contains no layout logic.
        """
        self.NativeUI = NativeUI
        self.left_button_width = 150

        # Top bar widgets
        self.tab_modeswitch = TabModeswitchButton(NativeUI)
        self.battery_display = BatteryDisplayWidget(NativeUI)
        self.tab_personal = PersonalDisplayWidget(NativeUI)

        # Left Bar widgets
        self.page_buttons = PageButtonsWidget(
            self.NativeUI, size=QSize(self.left_button_width, self.left_button_width)
        )
        self.ventilator_start_stop_buttons_widget = VentilatorStartStopButtonsWidget(
            self.NativeUI,
            size=QSize(self.left_button_width, int(self.left_button_width / 3)),
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
        self.alarmTab = TabAlarm(NativeUI)
        self.clinicalTab = TabClinical(NativeUI)

        # Settings Page Widgets
        self.settings_expert_tab = TabExpert(NativeUI)
        self.settings_chart_tab = TabChart(NativeUI)

        # Modes Page Widgets
        self.mode_settings_tab = TabModes(NativeUI)
        self.mode_personal_tab = TabPersonal(NativeUI)

    def add_widget(self, widget, name) -> int:
        setattr(self, name, widget)
        return 0
