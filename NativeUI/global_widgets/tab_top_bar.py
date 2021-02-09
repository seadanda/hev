from global_widgets.tab_battery import TabBattery
from global_widgets.tab_personal import TabPersonal
from PySide2 import QtCore, QtGui, QtWidgets


class TabTopBar(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QHBoxLayout(self)
        self.tab_personal = TabPersonal()
        self.tab_battery = TabBattery()
        self.widgets = [self.tab_personal, self.tab_battery]
        for widget in self.widgets:
            layout.addWidget(widget)
        self.setLayout(layout)
