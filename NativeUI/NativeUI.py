#!/usr/bin/env python3

"""
NativeUI.py
"""

__author__ = ["Benjamin Mummery", "Dónal Murray", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Benjamin Mummery"
__email__ = "benjamin.mummery@stfc.ac.uk"
__status__ = "Prototype"

import argparse
import logging
import sys
import os
from PySide2 import QtCore
from PySide2 import QtGui

import numpy as np

# from alarm_widgets.tab_alarms import TabAlarm
from global_widgets.tab_top_bar import TabTopBar
from global_widgets.tab_left_bar import TabLeftBar
from global_widgets.global_sendconfirm_popup import confirmPopup
from hev_main import MainView
from hev_settings import SettingsView
from hev_alarms import AlarmView
from hev_modes import ModeView
from hevclient import HEVClient

from threading import Lock

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

    battery_signal = Signal()

    def __init__(self, *args, **kwargs):
        super(NativeUI, self).__init__(*args, **kwargs)
        self.setWindowTitle("HEV NativeUI")

        PID_I_plot_scale = 3

        self.colors = {  # colorblind friendly ref: https://i.stack.imgur.com/zX6EV.png
            "background": QColor.fromRgb(30, 30, 30),
            "foreground": QColor.fromRgb(200, 200, 200),
            "background-enabled": QColor.fromRgb(50, 50, 50),
            "background-disabled": QColor.fromRgb(15, 15, 15),
            "foreground-disabled": QColor.fromRgb(100, 100, 100),
            "pressure_plot": QColor.fromRgb(0, 114, 178),
            "volume_plot": QColor.fromRgb(0, 158, 115),
            "flow_plot": QColor.fromRgb(240, 228, 66),
            "pressure_flow_plot": QColor.fromRgb(230, 159, 0),
            "flow_volume_plot": QColor.fromRgb(204, 121, 167),
            "volume_pressure_plot": QColor.fromRgb(86, 180, 233),
        }
        self.text_size = "20pt"
        self.text = {
            "plot_axis_label_pressure": "Pressure [cmH<sub>2</sub>O]",
            "plot_axis_label_flow": "Flow [L/min]",
            "plot_axis_label_volume": "Volume [mL/10<sup>"
            + str(PID_I_plot_scale)
            + "</sup>]",
            "plot_axis_label_time": "Time [s]",
            "plot_line_label_pressure": "Airway Pressure",
            "plot_line_label_flow": "Flow",
            "plot_line_label_volume": "Volume",
            "plot_line_label_pressure_flow": "Airway Pressure - Flow",
            "plot_line_label_flow_volume": "Flow - Volume",
            "plot_line_label_volume_pressure": "Volume - Airway Pressure",
        }
        self.iconpath = self.__find_icons()

        # initialise databases
        plot_history_length = 500
        self.db_lock = Lock()
        self.__data = {}
        self.__readback = {}
        self.__cycle = {}
        self.__battery = {}
        self.__plots = {
            "data": np.zeros((plot_history_length, 5)),
            "timestamp": list(el * (-1) for el in range(plot_history_length))[::-1],
            "pressure": list(0 for _ in range(plot_history_length)),
            "flow": list(0 for _ in range(plot_history_length)),
            "volume": list(0 for _ in range(plot_history_length)),
            "PID_I_scale": PID_I_plot_scale,
            "pressure_axis_range": [0, 20],
            "flow_axis_range": [-40, 80],
            "volume_axis_range": [0, 80],
        }
        self.__plots["data"][:, 0] = np.arange(500)  # fill timestamp with 0-499
        self.__alarms = []
        self.__targets = {}
        self.__personal = {}
        self.ongoingAlarms = {}

        # bars
        self.topBar = TabTopBar(self)
        self.leftBar = TabLeftBar(self)

        # Views
        self.stack = QStackedWidget(self)
        self.main_view = MainView(self)
        self.stack.addWidget(self.main_view)
        self.settings_view = SettingsView(self)
        self.stack.addWidget(self.settings_view)
        self.alarms_view = AlarmView(self)
        self.stack.addWidget(self.alarms_view)
        self.modes_view = ModeView(self)
        self.stack.addWidget(self.modes_view)

        self.confirmPopup = confirmPopup(
            self, self
        )  # one is passed as an argument, the other becomes parent
        self.confirmPopup.show()

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

        # Appearance
        palette = self.palette()
        palette.setColor(QPalette.Window, self.colors["background"])
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Update page buttons to match the shown view
        self.leftBar.tab_page_buttons.mainview_pressed()

        # self.main_view.alarmHandler.show()

    def get_data_db(self):
        """
        Return the contents of the __data database. Uses lock to avoid race
        conditions.
        """
        with self.db_lock:
            temp = self.__data
        return temp

    def get_targets_db(self):
        """
        Return the contents of the __target database. Uses lock to avoid race
        conditions.
        """

        with self.db_lock:
            temp = self.__targets
        return temp

    def get_readback_db(self):
        """
        Return the contents of the __readback database. Uses lock to avoid race
        conditions.
        """
        with self.db_lock:
            temp = self.__readback
        return temp

    def get_cycle_db(self):
        """
        Return the contents of the __cycle database. Uses lock to avoid race
        conditions.
        """
        with self.db_lock:
            temp = self.__cycle
        return temp

    def get_battery_db(self):
        """
        Return the contents of the __battery database. Uses lock to avoid race
        conditions.
        """
        with self.db_lock:
            temp = self.__battery
        return temp

    def get_plots_db(self):
        """
        Return the contents of the __plots database. Uses lock to avoid race
        conditions.
        """
        with self.db_lock:
            temp = self.__plots
        return temp

    def get_alarms_db(self):
        """
        Return the contents of the __alarms database. Uses lock to avoid race
        conditions.
        """
        with self.db_lock:
            temp = self.__alarms
        return temp

    def get_personal_db(self):
        """
        Return the contents of the __personal database. Uses lock to avoid race
        conditions.
        """
        with self.db_lock:
            temp = self.__personal
        return temp

    def set_data_db(self, payload):
        """
        Set the contents of the __data database. Uses lock to avoid race
        conditions.
        """
        logging.debug("setting data db")
        with self.db_lock:
            for key in payload:
                self.__data[key] = payload[key]
        return 0

    def set_targets_db(self, payload):
        """
        Set the contents of the __targets database. Uses lock to avoid race
        conditions.
        """
        logging.debug("setting targets db")
        with self.db_lock:
            for key in payload:
                self.__targets[key] = payload[key]
        return 0

    def set_readback_db(self, payload):
        """
        Set the contents of the __readback database. Uses lock to avoid race
        conditions.
        """
        logging.debug("setting readback db")
        with self.db_lock:
            for key in payload:
                self.__readback[key] = payload[key]
        return 0

    def set_cycle_db(self, payload):
        """
        Set the contents of the __cycle database. Uses lock to avoid race
        conditions.
        """
        logging.debug("setting cycle db")
        with self.db_lock:
            for key in payload:
                self.__cycle[key] = payload[key]
        # print(self.__cycle)
        return 0

    def set_battery_db(self, payload):
        """
        Set the contents of the __battery database. Uses lock to avoid race
        conditions.
        """
        logging.debug("setting battery db")
        with self.db_lock:
            for key in payload:
                self.__battery[key] = payload[key]
        return 0

    def set_plots_db(self, payload):
        """
        Set the contents of the __plots database. Uses lock to avoid race
        conditions.
        TODO: why are there 2 volumes? Is this necessary for something?
        """
        logging.debug("setting plots db")
        with self.db_lock:
            self.__plots["data"] = np.append(
                np.delete(self.__plots["data"], 0, 0),
                [
                    [
                        payload["timestamp"],
                        payload["pressure_patient"],
                        payload["flow"],
                        payload["volume"],
                        payload["volume"],
                    ]
                ],
                axis=0,
            )

            # subtract latest timestamp and scale to seconds
            self.__plots["timestamp"] = np.true_divide(
                np.subtract(self.__plots["data"][:, 0], self.__plots["data"][-1, 0]),
                1000,
            )

            self.__plots["pressure"] = self.__plots["data"][:, 1]
            self.__plots["flow"] = self.__plots["data"][:, 2]
            self.__plots["volume"] = [
                v / (10 ** self.__plots["PID_I_scale"])
                for v in self.__plots["data"][:, 3]
            ]

            self.__update_plot_ranges()
        return 0

    def __update_plot_ranges(self):
        values = ["pressure", "flow", "volume"]
        for value in values:
            range = "%s_axis_range" % value
            self.__plots[range] = [
                min(self.__plots[range][0], min(self.__plots[value])),
                max(self.__plots[range][1], max(self.__plots[value])),
            ]
        return 0

    def set_alarms_db(self, payload):
        """
        Set the contents of the __alarms database. Uses lock to avoid race
        conditions.
        """
        logging.debug("setting alarms db")
        with self.db_lock:
            self.__alarms = payload
        return 0

    def set_personal_db(self, payload):
        """
        Set the contents of the __personal database. Uses lock to avoid race
        conditions.
        """
        logging.debug("setting personal db")
        with self.db_lock:
            for key in payload:
                self.__personal[key] = payload[key]
        return 0

    def start_client(self):
        """runs in other thread - works as long as super goes last and nothing
        else is blocking. If something more than a one-shot process is needed
        then use async
        """
        logging.debug("start_client")
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
        self.statusBar().showMessage(f"{payload}")
        logging.debug("revieved payload of type %s" % payload["type"])
        try:
            if payload["type"] == "DATA":
                self.set_data_db(payload["DATA"])
                self.set_plots_db(payload["DATA"])
                self.ongoingAlarms = payload["alarms"]
            if payload["type"] == "BATTERY":
                self.set_battery_db(payload["BATTERY"])
                self.battery_signal.emit()
            if payload["type"] == "ALARM":
                self.set_alarms_db(payload["ALARM"])
            if payload["type"] == "TARGET":
                self.set_targets_db(payload["TARGET"])
            if payload["type"] == "READBACK":
                self.set_readback_db(payload["READBACK"])
            if payload["type"] == "PERSONAL":
                self.set_personal_db(payload["PERSONAL"])

            if payload["type"] == "CYCLE":
                self.set_cycle_db(payload["CYCLE"])
        except KeyError:
            logging.warning(f"Invalid payload: {payload}")

    @Slot(str, str, float)
    def q_send_cmd(self, cmdtype: str, cmd: str, param: float = None) -> None:
        """send command to hevserver via socket"""
        check = self.send_cmd(cmdtype=cmdtype, cmd=cmd, param=param)
        if check:
            self.confirmPopup.addConfirmation(cmdtype + "   " + cmd)

    @Slot(str)
    def q_ack_alarm(self, alarm: str):
        """acknowledge an alarm in the hevserver"""
        self.ack_alarm(alarm=alarm)

    @Slot(str)
    def q_send_personal(self, personal: str):
        """send personal details to hevserver"""
        self.send_personal(personal=personal)

    def __find_icons(self):
        """
        Locate the icons firectory and return its path.
        """
        iconext = "png"
        initial_path = os.path.join("hev-display/assets/", iconext)
        # assume we're in the root directory
        temp_path = os.path.join(os.getcwd(), initial_path)
        if os.path.isdir(temp_path):
            return temp_path

        # assume we're one folder deep in the root directory
        temp_path = os.path.join("..", temp_path)
        if os.path.isdir(temp_path):
            return temp_path

        walk = os.walk(os.path.join(os.getcwd(), ".."))
        for w in walk:
            if "svg" in w[1]:
                temp_path = os.path.join(os.path.normpath(w[0]), iconext)
                return temp_path

        raise Exception(FileNotFoundError, "could not locate %s icon files" % iconext)


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
    if args.debug == 0:
        dep.setFixedSize(1920, 1080)
        dep.setGeometry(0, 0, 1920, 1080)
        dep.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    elif args.debug > 0:
        rescale = 1
        dep.setGeometry(0, 0, rescale * 1920, rescale * 1080)

    dep.battery_signal.connect(dep.topBar.tab_battery.update_value)

    dep.show()
    app.exec_()
