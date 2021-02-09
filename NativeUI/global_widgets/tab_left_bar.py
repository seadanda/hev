from global_widgets.tab_page_buttons import TabPageButtons
from global_widgets.tab_start_stop_buttons import TabStartStopStandbyButtons
from PySide2 import QtCore, QtGui, QtWidgets


class TabLeftBar(QtWidgets.QWidget):
    def __init__(self, *args, colors: dict = None, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout(self)
        self.tab_page_buttons = TabPageButtons(colors=colors)
        self.tab_start_stop_buttons = TabStartStopStandbyButtons()
        self.widgets = [self.tab_page_buttons, self.tab_start_stop_buttons]
        for widget in self.widgets:
            layout.addWidget(widget)
        self.setLayout(layout)
