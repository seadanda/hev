from PySide2 import QtWidgets, QtGui, QtCore
from global_widgets.template_set_values import TemplateSetValues


class TabPersonal(
    TemplateSetValues
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, *args, **kwargs):
        settingsList = [
            ["Name", "/min", "respiratory_rate"],
            ["Patient ID", "s", "inhale_time"],
            ["Age", "", "ie_ratio"],
            ["Sex", "", "inhale_trigger_threshold"],
            ["Weight", "", "exhale_trigger_threshold"],
            ["Height", "", "inspiratory_pressure"],
        ]
        super(TabPersonal, self).__init__(*args, **kwargs)
        self.addSpinSingleCol(settingsList)
        self.addButtons()
        self.finaliseLayout()


# class TabPersonal(
#     QtWidgets.QWidget
# ):  # chose QWidget over QDialog family because easier to modify
#     def __init__(self, *args, **kwargs):
#         super(TabPersonal, self).__init__(*args, **kwargs)


#         self.liveUpdating = True
#         settingsList = [
#             ["Name", "/min", "respiratory_rate"],
#             ["Patient ID", "s", "inhale_time"],
#             ["Age", "", "ie_ratio"],
#             ["Sex", "", "inhale_trigger_threshold"],
#             ["Weight", "", "exhale_trigger_threshold"],
#             ["Height", "", "inspiratory_pressure"]
#         ]
#         self.spinDict = {}
#         vOptionLayout = QtWidgets.QVBoxLayout()
#         for info in settingsList:
#             self.spinDict[info[0]] = simpleSpin(info)
#             vOptionLayout.addWidget(self.spinDict[info[0]])

#         hlayout = QtWidgets.QHBoxLayout()
#         self.okButton = QtWidgets.QPushButton()
#         self.okButton.setStyleSheet(
#             "height:50px; background-color:white; border-radius:4px;"
#         )
#         self.okButton.pressed.connect(self.okButtonPressed)
#         hlayout.addWidget(self.okButton)

#         self.cancelButton = QtWidgets.QPushButton()
#         self.cancelButton.setStyleSheet(
#             "height:50px; background-color:white; border-radius:4px;"
#         )
#         self.cancelButton.pressed.connect(self.cancelButtonPressed)
#         hlayout.addWidget(self.cancelButton)

#         vlayout = QtWidgets.QVBoxLayout()
#         vlayout.addLayout(vOptionLayout)
#         vlayout.addLayout(hlayout)
#         self.setLayout(vlayout)

#         self.timer = QtCore.QTimer()
#         self.timer.setInterval(160)  # just faster than 60Hz
#         self.timer.timeout.connect(self.update_settings_data)
#         self.timer.start()

#     def update_settings_data(self):
#         if self.liveUpdating:
#             for widget in self.spinDict:
#                 self.spinDict[widget].update_targets_value()

#     def okButtonPressed(self):
#         message = []
#         self.liveUpdating = True
#         for widget in self.spinDict:
#             #print(widget)
#             if self.spinDict[widget].manuallyUpdated:
#                 setVal = self.spinDict[widget].simpleSpin.value()
#                 #print('manually updated')
#                 print('set'  + widget + ' to ' + str(setVal) )
#                 self.spinDict[widget].manuallyUpdated = False

#     def cancelButtonPressed(self):
#         self.liveUpdating = True
