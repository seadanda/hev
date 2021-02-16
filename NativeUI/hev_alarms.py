from alarm_widgets.tab_alarms import TabAlarm
from alarm_widgets.tab_clinical import TabClinical
from global_widgets.global_select_button import selectorButton
from global_widgets.template_main_pages import TemplateMainPages


class AlarmView(TemplateMainPages):
    def __init__(self, NativeUI, *args, **kwargs):
        super(AlarmView, self).__init__(*args, **kwargs)

        self.alarm_button = selectorButton("List of Alarms")
        self.clinical_button = selectorButton("Clinical Limits")
        self.tech_button = selectorButton("Technical Limits")

        self.button_widgets = [self.alarmButton, self.clinicalButton, self.techButton]

        self.alarm_tab = TabAlarm(NativeUI)
        self.clinical_tab = TabClinical(NativeUI)
        self.technical_tab = TabClinical(NativeUI)
        self.tabs_list = [self.alarm_tab, self.clinical_tab, self.technical_tab]
        self.buildPage(self.button_widgets, self.tabs_list)
