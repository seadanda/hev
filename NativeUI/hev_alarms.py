# #!/usr/bin/env python3

# """
# hev_alarms.py
# """

# __author__ = ["Benjamin Mummery", "Tiago Sarmento"]
# __credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
# __license__ = "GPL"
# __version__ = "0.0.1"
# __maintainer__ = "Tiago Sarmento"
# __email__ = "tiago.sarmento@stfc.ac.uk"
# __status__ = "Prototype"

# from alarm_widgets.tab_alarms import TabAlarm
# from alarm_widgets.tab_clinical import TabClinical
# from global_widgets.global_select_button import selectorButton
# from global_widgets.template_main_pages import TemplateMainPages


# class AlarmView(TemplateMainPages):
#     """Subclasses TemplateMainPages to display alarms."""

#     def __init__(self, NativeUI, *args, **kwargs):
#         super(AlarmView, self).__init__(*args, **kwargs)

#         self.alarmButton = selectorButton(NativeUI, "List of Alarms")
#         self.clinicalButton = selectorButton(NativeUI, "Clinical Limits")
#         #self.techButton = selectorButton(NativeUI, "Technical Limits")

#         self.buttonWidgets = [self.alarmButton, self.clinicalButton]#, self.techButton]

#         self.alarmTab = TabAlarm(NativeUI)
#         self.clinicalTab = TabClinical(NativeUI)
#         #self.technicalTab = TabClinical(NativeUI)
#         self.tabsList = [self.alarmTab, self.clinicalTab]#, self.technicalTab]
#         self.buildPage(self.buttonWidgets, self.tabsList)
