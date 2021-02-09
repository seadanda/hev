from PySide2 import QtWidgets, QtGui, QtCore
from settings_widgets.tab_expert import simpleSpin
from global_widgets.template_set_values import TemplateSetValues

class TabClinical(
    TemplateSetValues
):  # chose QWidget over QDialog family because easier to modify
    def __init__(self, *args, **kwargs):
        super(TabClinical, self).__init__(*args, **kwargs)
        self.liveUpdating = True
        self.modifications = []
        #self.spinDict = {}
        clinicalList = [
            ["APNEA", "ms", "duration_calibration"],
            ["Check Pressure Patient", "ms", "duration_buff_purge"],
            ["High FIO2", "ms", ""],
            ["High Pressure", "", ""],
            ["High Respiratory Rate", "", ""],
            ["High VTE", "", ""],
            ["Low VTE", "", ""],
            ["High VTI", "", ""],
            ["Low VTI", "", ""],
            ["Low FIO2", "", ""],
            ["Occlusion", "", ""],
            ["High PEEP", "", ""],
            ["Low PEEP", "", ""],
        ]
        self.addSpinDblCol(clinicalList)
        self.addButtons()
        self.finaliseLayout()


        # grid = QtWidgets.QGridLayout()
        # i = 0
        # for info in clinicalList:
        #     self.spinDict[info[0]] = simpleSpin(info)
        #     grid.addWidget(self.spinDict[info[0]], int(i / 2), i % 2)
        #     i = i + 1

        # hlayout = QtWidgets.QHBoxLayout()
        # self.okButton = QtWidgets.QPushButton()
        # self.okButton.setStyleSheet(
        #     "height:50px; background-color:white; border-radius:4px;"
        # )
        # # self.okButton.pressed.connect(self.okButtonPressed)
        # hlayout.addWidget(self.okButton)

        # self.cancelButton = QtWidgets.QPushButton()
        # self.cancelButton.setStyleSheet(
        #     "height:50px; background-color:white; border-radius:4px;"
        # )
        # # self.cancelButton.pressed.connect(self.cancelButtonPressed)
        # hlayout.addWidget(self.cancelButton)

        # vlayout = QtWidgets.QVBoxLayout()
        # vlayout.addLayout(grid)
        # vlayout.addLayout(hlayout)
        # self.setLayout(vlayout)
