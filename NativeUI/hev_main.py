"""
Docstring
"""

from main_widgets.tab_measurements import TabMeasurements
from main_widgets.tab_plots import TabPlots
from main_widgets.tab_spin_buttons import TabSpinButtons
from main_widgets.tab_history_buttons import TabHistoryButtons
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget


class MainView(QWidget):
    """
    Docstring [TODO]
    """

    def __init__(self, NativeUI, *args, **kwargs):
        super(MainView, self).__init__(*args, **kwargs)

        hlayout = QHBoxLayout()

        center_vlayout = QVBoxLayout()
        right_vlayout = QVBoxLayout()
        bottom_layout = QHBoxLayout()

        # Set up the widget tabs
        self.tab_plots = TabPlots(NativeUI)
        self.tab_measurements = TabMeasurements(NativeUI)
        self.tab_spin = TabSpinButtons(NativeUI)
        self.tab_history_buttons = TabHistoryButtons(NativeUI)

        bottom_layout.addWidget(self.tab_history_buttons)
        bottom_layout.addWidget(self.tab_spin)

        # center column - plots
        center_vlayout.addWidget(self.tab_plots)
        center_vlayout.addLayout(bottom_layout)
        hlayout.addLayout(center_vlayout)

        # right column - measurements
        right_vlayout.addWidget(self.tab_measurements)
        hlayout.addLayout(right_vlayout)

        self.setLayout(hlayout)

        for button in self.tab_history_buttons.buttons:
            button.HistoryButtonPressed.connect(self.tab_plots.update_plot_time_range)
