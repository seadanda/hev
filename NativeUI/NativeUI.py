#!/usr/bin/env python3
import logging
import argparse
import sys
import numpy as np
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QVBoxLayout
from hevclient import HEVClient
from hev_main import MainView

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

class NativeUI(HEVClient, QMainWindow):
    """Main application with client logic"""
    def __init__(self, *args, **kwargs):
        super(NativeUI, self).__init__(*args, **kwargs)
        self.setWindowTitle("HEV NativeUI")
        self.main_view = MainView()
        self.setCentralWidget(self.main_view)
        self.statusBar().showMessage("Waiting for data")
        self.data = {}
        self.target = {}
        self.readback = {}
        self.cycle = {}
        self.battery = {}
        self.plots = np.zeros((500, 4))
        self.plots[:, 0] = np.arange(500) # fill timestamp with 0-499

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
        try:
            if (payload["type"] == "DATA"):
                self.data = payload["DATA"]
                # remove first entry and append plot data to end
                self.plots = np.append(np.delete(self.plots, 0, 0), [[self.data["timestamp"], self.data["pressure_patient"], 0, 0]], axis=0)
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


if __name__ == "__main__":
    # parse args and setup logging
    parser = argparse.ArgumentParser(description='Plotting script for the HEV lab setup')
    parser.add_argument('-d', '--debug', action='count', default=0, help='Show debug output')

    args = parser.parse_args()
    if args.debug == 0:
        logging.getLogger().setLevel(logging.WARNING)
    elif args.debug == 1:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.DEBUG)

    # setup pyqtplot widget
    app = QApplication(sys.argv)
    dep = NativeUI()
    dep.show()
    app.exec_()