from global_widgets.tab_battery import TabBattery
from global_widgets.tab_personal import TabPersonal
from global_widgets.tab_modeswitch_button import TabModeswitchButton
from PySide2 import QtCore, QtGui, QtWidgets


class TabTopBar(QtWidgets.QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QHBoxLayout(self)
        self.tab_modeswitch = TabModeswitchButton(NativeUI)
        self.tab_personal = TabPersonal(NativeUI)
        self.tab_battery = TabBattery(NativeUI)
        self.widgets = [self.tab_modeswitch, self.tab_personal, self.tab_battery]
        for widget in self.widgets:
            layout.addWidget(widget)
        self.setLayout(layout)
