#!/usr/bin/env python3
import argparse
import logging
import sys

import numpy as np

# from alarm_widgets.tab_alarms import TabAlarm
from global_widgets.tab_top_bar import TabTopBar
from global_widgets.tab_left_bar import TabLeftBar
from hev_main import MainView
from hev_settings import SettingsView
from hev_alarms import AlarmView
from hev_modes import ModeView
from hevclient import HEVClient

from PySide2.QtCore import Signal, Slot
from PySide2.QtGui import QColor, QPalette
from PySide2.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s"
)


class NativeUI(HEVClient, QMainWindow):
    """Main application with client logic"""

    battery_signal = Signal(dict)

    def __init__(self, *args, **kwargs):
        super(NativeUI, self).__init__(*args, **kwargs)
        self.setWindowTitle("HEV NativeUI")
        self.setFixedSize(1920, 1080)

        self.colors = {
            "background": QColor.fromRgb(30, 30, 30),
            "foreground": QColor.fromRgb(200, 200, 200),
        }

        # bars
        self.topBar = TabTopBar()
        self.leftBar = TabLeftBar(self, colors=self.colors)

        # Views
        self.stack = QStackedWidget(self)
        self.main_view = MainView()
        self.stack.addWidget(self.main_view)
        self.settings_view = SettingsView()
        self.stack.addWidget(self.settings_view)
        self.alarms_view = AlarmView()
        self.stack.addWidget(self.alarms_view)
        self.modes_view = ModeView()
        self.stack.addWidget(self.modes_view)
        self.stack.setCurrentWidget(self.alarms_view)
        #        self.menu_bar = TabPageButtons()

        # Layout
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.leftBar)
        hlayout.addWidget(self.stack)

        vlayout = QVBoxLayout()
        vlayout.addWidget(self.topBar)
        vlayout.addLayout(hlayout)

        # Set Central
        self.centralWidget = QWidget(self)
        self.centralWidget.setLayout(vlayout)
        self.setCentralWidget(self.centralWidget)

        self.statusBar().showMessage("Waiting for data")
        self.statusBar().setStyleSheet("color: white")

        # database
        self.data = {}
        self.target = {}
        self.readback = {}
        self.cycle = {}
        self.battery = {}
        self.plots = np.zeros((500, 5))
        self.plots[:, 0] = np.arange(500)  # fill timestamp with 0-499
        self.alarms = []
        self.targets = "empty"

        # Appearance
        palette = self.palette()
        palette.setColor(QPalette.Window, self.colors["background"])
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # self.main_view.alarmHandler.show()

    def start_client(self):
        """runs in other thread - works as long as super goes last and nothing
        else is blocking. If something more than a one-shot process is needed
        then use async
        """
        # call for all the targets and personal details
        # when starting the web app so we always have some in the db
        self.send_cmd("GET_TARGETS", "PC_AC")
        self.send_cmd("GET_TARGETS", "PC_AC_PRVC")
        self.send_cmd("GET_TARGETS", "PC_PSV")
        self.send_cmd("GET_TARGETS", "TEST")
        self.send_cmd("GENERAL", "GET_PERSONAL")
        super().start_client()

    def get_updates(self, payload):
        """callback from the polling function, payload is data from socket """
        # Store data in dictionary of lists
        self.statusBar().showMessage(f"{payload}")
        # print(payload["type"])
        try:
            if payload["type"] == "DATA":
                self.data = payload["DATA"]
                self.ongoingAlarms = payload["alarms"]
                # remove first entry and append plot data to end
                self.plots = np.append(
                    np.delete(self.plots, 0, 0),
                    [
                        [
                            self.data["timestamp"],
                            self.data["pressure_patient"],
                            self.data["flow"],
                            self.data["volume"],
                            self.data["volume"],
                        ]
                    ],
                    axis=0,
                )
            if payload["type"] == "BATTERY":
                self.battery = payload["BATTERY"]
                self.battery_signal.emit(self.battery)
            if payload["type"] == "ALARM":
                self.alarms = payload["ALARM"]
            if payload["type"] == "TARGET":
                self.targets = payload["TARGET"]
            if payload["type"] == "READBACK":
                self.readback = payload["READBACK"]
                # print(self.readback)
            if payload["type"] == "PERSONAL":
                self.personal = payload["PERSONAL"]
                #  self.personal = self.data
                # print(self.targets)

                self.plots = np.append(
                    np.delete(self.plots, 0, 0),
                    [
                        [
                            self.data["timestamp"],
                            self.data["pressure_patient"],
                            self.data["flow"],
                            self.data["volume"],
                        ]
                    ],
                    axis=0,
                )
        except KeyError:
            logging.warning(f"Invalid payload: {payload}")

    @Slot(str, str, float)
    def q_send_cmd(self, cmdtype: str, cmd: str, param: float = None) -> None:
        """send command to hevserver via socket"""
        self.send_cmd(cmdtype=cmdtype, cmd=cmd, param=param)

    @Slot(str)
    def q_ack_alarm(self, alarm: str):
        """acknowledge an alarm in the hevserver"""
        self.ack_alarm(alarm=alarm)

    @Slot(str)
    def q_send_personal(self, personal: str):
        """send personal details to hevserver"""
        self.send_personal(personal=personal)


# from PySide2.QtQml import QQmlApplicationEngine

if __name__ == "__main__":
    # parse args and setup logging
    parser = argparse.ArgumentParser(
        description="Plotting script for the HEV lab setup"
    )
    parser.add_argument(
        "-d", "--debug", action="count", default=0, help="Show debug output"
    )

    args = parser.parse_args()
    if args.debug == 0:
        logging.getLogger().setLevel(logging.WARNING)
    elif args.debug == 1:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.DEBUG)

    # setup pyqtplot widget
    app = QApplication(sys.argv)
    # engine = QQmlApplicationEngine()
    # engine.load(QUrl('hev-display/assets/Cell.qml'))
    dep = NativeUI()

    dep.battery_signal.connect(dep.topBar.tab_battery.update_value)

    dep.show()
    app.exec_()
