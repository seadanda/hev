"""
Docstring # TODO
"""

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2.QtCore import QSize, Slot
from main_widgets.tab_measurements import TabMeasurements
from main_widgets.tab_plots import TabPlots
from main_widgets.tab_spin_buttons import TabSpinButtons
from main_widgets.tab_history_buttons import TabHistoryButtons
from main_widgets.tab_expert_plots import TabExpertPlots
from PySide2.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

# TODO move accessing plot data to this page so we only do it once.


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
        self.stack = QStackedWidget(self)
        self.tab_plots = TabPlots(NativeUI)
        self.tab_expert_plots = TabExpertPlots(NativeUI)
        self.tab_measurements = TabMeasurements(NativeUI)
        self.tab_spin = TabSpinButtons(NativeUI)
        self.tab_history_buttons = TabHistoryButtons(NativeUI)
        self.tab_normal_expert_buttons = TabNormalExpertButtons(NativeUI)

        # Bottom bar -
        bottom_layout.addWidget(self.tab_history_buttons)
        bottom_layout.addWidget(self.tab_spin)

        # center column - plots
        self.stack.addWidget(self.tab_plots)
        self.stack.addWidget(self.tab_expert_plots)
        center_vlayout.addWidget(self.tab_normal_expert_buttons)
        center_vlayout.addWidget(self.stack)
        center_vlayout.addLayout(bottom_layout)
        hlayout.addLayout(center_vlayout)

        # right column - measurements
        right_vlayout.addWidget(self.tab_measurements)
        hlayout.addLayout(right_vlayout)

        self.setLayout(hlayout)

        self.tab_normal_expert_buttons.normal_button.pressed.connect(
            self.switch_to_normal
        )
        self.tab_normal_expert_buttons.expert_button.pressed.connect(
            self.switch_to_expert
        )
        self.switch_to_normal()

        for button in self.tab_history_buttons.buttons:
            button.HistoryButtonPressed.connect(self.tab_plots.update_plot_time_range)
            button.HistoryButtonPressed.connect(
                self.tab_expert_plots.update_plot_time_range
            )

    @Slot()
    def switch_to_normal(self):
        """
        raise the normal plots view
        """
        self.stack.setCurrentWidget(self.tab_plots)
        for button in self.tab_normal_expert_buttons.buttons:
            button.setEnabled(True)
        self.tab_normal_expert_buttons.normal_button.setEnabled(False)

    @Slot()
    def switch_to_expert(self):
        """
        raise the detailed plots view
        """
        self.stack.setCurrentWidget(self.tab_expert_plots)
        for button in self.tab_normal_expert_buttons.buttons:
            button.setEnabled(True)
        self.tab_normal_expert_buttons.expert_button.setEnabled(False)


class TabNormalExpertButtons(QWidget):
    def __init__(self, NativeUI, *args, **kwargs):
        super().__init__(*args, **kwargs)
        font_size = 20
        button_size = QSize(150, 50)
        self.NativeUI = NativeUI
        layout = QHBoxLayout()
        self.normal_button = QPushButton("Normal")
        self.expert_button = QPushButton("Detailed")
        self.buttons = [
            self.normal_button,
            self.expert_button,
        ]
        layout.addWidget(self.normal_button)
        layout.addWidget(self.expert_button)
        # layout.setAlignment(self.normal_button, QtCore.Qt.AlignLeft)
        # layout.setAlignment(self.expert_button, QtCore.Qt.AlignLeft)
        self.setLayout(layout)

        for button in self.buttons:
            button.setStyleSheet(
                "QPushButton{"
                "color: " + NativeUI.colors["foreground"].name() + ";"
                "font-size: " + str(font_size) + "pt;"
                "background-color: " + NativeUI.colors["background"].name() + ";"
                "border-color: " + NativeUI.colors["background"].name() + ";"
                "}"
                "QPushButton:disabled{"
                "background-color: "
                + NativeUI.colors["background-disabled"].name()
                + ";"
                "}"
            )
            button.setFixedSize(button_size)
