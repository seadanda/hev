#!/usr/bin/env python3

"""
NativeUI.py

Command-line arguments:
-d, --debug      : set the level of debug output.Include once for INFO, twice for DEBUG
-w, --windowed   : run the user interface in windowed mode.
-r, --resolution : set the window size in pixels. E.g. -r 1920x1080
"""

__author__ = ["Benjamin Mummery", "Dónal Murray", "Tiago Sarmento"]
__credits__ = ["Benjamin Mummery", "Dónal Murray", "Tim Powell", "Tiago Sarmento"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Benjamin Mummery"
__email__ = "benjamin.mummery@stfc.ac.uk"
__status__ = "Prototype"

import argparse
import json
import logging
import os
import re
import sys
from threading import Lock

import git
from global_widgets.global_send_popup import confirmPopup
from global_widgets.global_spinbox import labelledSpin
from widget_library.ok_cancel_buttons_widget import (
    OkButtonWidget,
    OkSendButtonWidget,
    CancelButtonWidget,
)
from hevclient import HEVClient
from PySide2 import QtCore
from PySide2.QtCore import Signal, Slot
from PySide2.QtGui import QColor, QFont, QPalette
from ui_layout import Layout
from ui_widgets import Widgets
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QRadioButton, QDialog

# from handler_library.alarm_handler import AlarmHandler
from handler_library.battery_handler import BatteryHandler
from handler_library.data_handler import DataHandler
from handler_library.measurement_handler import MeasurementHandler
from handler_library.personal_handler import PersonalHandler

# from handler_library.readback_handler import ReadbackHandler


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s \n (%(pathname)s, %(lineno)s)",
)


class NativeUI(HEVClient, QMainWindow):
    """Main application with client logic"""

    # BatterySignal = Signal(dict)
    PlotSignal = Signal(dict)
    MeasurementSignal = Signal(dict, dict)

    def __init__(self, *args, **kwargs):
        super(NativeUI, self).__init__(*args, **kwargs)

        # Set up the handlers
        self.battery_handler = BatteryHandler()
        self.data_handler = DataHandler(plot_history_length=1000)
        self.measurement_handler = MeasurementHandler()
        self.personal_handler = PersonalHandler()

        config_path = self.__find_configs()

        # self.setFixedSize(1920, 1080)
        self.modeList = ["PC/AC", "PC/AC-PRVC", "PC-PSV", "CPAP"]
        self.currentMode = self.modeList[0]

        self.localisation_files = ["text_english.json", "text_portuguese.json"]
        self.localisation_files = [
            os.path.join(config_path, file) for file in self.localisation_files
        ]

        # Import settings from config files
        with open(os.path.join(config_path, "colors.json")) as infile:
            # colorblind friendly ref: https://i.stack.imgur.com/zX6EV.png
            self.colors = json.load(infile)

        with open(os.path.join(config_path, "text_english.json")) as infile:
            self.text = json.load(infile)

        # convert colours to a PySide2-readble form
        for key in self.colors:
            self.colors[key] = QColor.fromRgb(*self.colors[key])

        self.text_font = QFont("Sans Serif", 20)
        self.value_font = QFont("Sans Serif", 40)
        self.text_size = "20pt"  # TODO: remove in favour of self.text_font
        self.icons = {
            "button_main_page": "user-md-solid",
            "button_alarms_page": "exclamation-triangle-solid",
            "button_modes_page": "fan-solid",
            "button_settings_page": "sliders-h-solid",
        }
        self.iconext = "png"
        self.iconpath = self.__find_icons(self.iconext)
        for key in self.icons:
            self.icons[key] = os.path.join(
                self.iconpath, self.icons[key] + "." + self.iconext
            )

        # initialise databases TODO: remove these and use handlers instead.
        self.db_lock = Lock()
        self.__data = {}
        self.__readback = {}
        self.__cycle = {}
        self.__alarms = {}
        self.__targets = {}
        self.__personal = {}
        self.ongoingAlarms = {}
        self.__database_list = [
            "__data",
            "__readback",
            "__cycle",
            "__battery",
            "__plots",
            "__alarms",
            "__targets",
            "__personal",
        ]

        self.widgets = Widgets(self)  # Create all the widgets we'll need
        self.layouts = Layout(self, self.widgets)  #

        self.confirmPopup = confirmPopup(
            self, self
        )  # one is passed as an argument, the other becomes parent
        self.confirmPopup.show()

        # Set Central
        self.centralWidget = QWidget(self)
        self.centralWidget.setLayout(self.layouts.global_layout())
        self.setCentralWidget(self.centralWidget)

        self.statusBar().showMessage("Waiting for data")
        self.statusBar().setStyleSheet("color:" + self.colors["page_foreground"].name())

        # Appearance
        self.setWindowTitle(self.text["ui_window_title"])
        palette = self.palette()
        palette.setColor(QPalette.Window, self.colors["page_background"])
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.startupWidget = QDialog(self)
        self.startupWidget.setLayout(self.layouts.startup_layout())
        self.startupWidget.setPalette(palette)
        self.startupWidget.setAutoFillBackground(True)
        self.startupWidget.show()

        # Connect widgets
        self.__define_connections()

        # Update page buttons to match the shown view
        self.widgets.page_buttons.buttons[0].on_press()

    @Slot(str)
    def change_page(self, page_to_show: str) -> int:
        """
        Change the page shown in page_stack.
        """
        self.widgets.page_stack.setCurrentWidget(getattr(self.widgets, page_to_show))
        return 0

    def __define_connections(self) -> int:
        """
        Connect the signals and slots necessary for the UI to function.

        Connections defined here:

        battery_handler.UpdateBatteryDisplay -> battery_display.update_Status
            UpdateBatteryDisplay is emitted by the battery handler in response to a
            battery payload.

        personal_handler.UpdatePersonalDisplay -> personal_display.update_status
            UpdatePersonalDisplay is emitted by the personal handler in response to a
            change in the personal information.

        HistoryButtonPressed -> normal_plots, detailed_plots
            History buttons control the amount of time shown on the x axes of the
            value-time plots on the main page. HistoryButtonPressed is emitted by the
            history button when pressed.

        PageButtonPressed -> change_page
            Page buttons control which page is shown in the page_stack.
            PageButtonPressed is emitted by the page button when pressed.

        ToggleButtonPressed -> charts_widget.show_line
        ToggleButtonPressed -> charts_widget.hide_line
            Lines in the charts_widget are shown or hidden depending on whether the
            relevent toggle button is in the checked or unchecked state.
            ToggleButtonPressed is emitted by the toggle button when pressed.

        PlotSignal -> normal_plots, detailed_plots, charts_widget
            Data plotted in the normal, detailed, and charts plots is updated in
            response to PlotSignal. PlotSignal is emitted in __emit_plots_signal() which
            is triggered at timer.timeout.

        MeasurementSignal -> normal_measurements, detailed_measurements
            Data shown in the normal and detailed measurments widgets is updated in
            response to MeasurementSignal. MeasurementSignal is emitted in
            __emit_measurements_signal() which is triggered at timer.timeout.
        """

        # Startup connections
        self.widgets.calibration.button.pressed.connect(
            lambda i=self.widgets.calibration: self.widgets.startup_handler.handle_calibrationPress(
                i
            )
        )
        self.widgets.leak_test.button.pressed.connect(
            lambda i=self.widgets.leak_test: self.widgets.startup_handler.handle_calibrationPress(
                i
            )
        )
        self.widgets.maintenance.button.pressed.connect(
            lambda i=self.widgets.maintenance: self.widgets.startup_handler.handle_calibrationPress(
                i
            )
        )

        self.widgets.nextButton.pressed.connect(
            lambda i=self.widgets.startup_stack: self.widgets.startup_handler.handle_nextbutton(
                i
            )
        )
        self.widgets.skipButton.pressed.connect(
            lambda: self.widgets.startup_handler.handle_sendbutton()
        )

        self.widgets.backButton.pressed.connect(
            lambda i=self.widgets.startup_stack: self.widgets.startup_handler.handle_backbutton(
                i
            )
        )

        # Battery Display should update when we get battery info
        self.battery_handler.UpdateBatteryDisplay.connect(
            self.widgets.battery_display.update_status
        )

        # Personal Display should update when personal info is changed.
        self.personal_handler.UpdatePersonalDisplay.connect(
            self.widgets.personal_display.update_status
        )

        # Measurement Widgets should update when the data is changed.
        for widget in (
            self.widgets.normal_measurements.widget_list
            + self.widgets.detailed_measurements.widget_list
        ):
            self.measurement_handler.UpdateMeasurements.connect(widget.set_value)

        # When plot data is updated, plots should update
        for plot_widget in [
            self.widgets.normal_plots.update_plot_data,
            self.widgets.detailed_plots.update_plot_data,
            self.widgets.circle_plots.update_plot_data,
            self.widgets.charts_widget.update_plot_data,
        ]:
            self.data_handler.UpdatePlots.connect(plot_widget)

        # Plots should update when we press the history buttons
        for button in self.widgets.history_buttons.buttons:
            for widget in [self.widgets.normal_plots, self.widgets.detailed_plots]:
                button.HistoryButtonPressed.connect(widget.update_plot_time_range)

        # The shown page should change when we press the page buttons
        for button in self.widgets.page_buttons.buttons:
            button.PageButtonPressed.connect(self.change_page)

        ##### Mode:
        # When mode is switched from mode page, various other locations must respond
        self.widgets.mode_handler.modeSwitched.connect(
            lambda i: self.set_current_mode(i)
        )
        self.widgets.mode_handler.modeSwitched.connect(
            lambda i: self.widgets.tab_modeswitch.update_mode(i)
        )
        self.widgets.mode_handler.modeSwitched.connect(
            self.widgets.mode_handler.refresh_button_colour
        )

        # when mode is switched from modeSwitch button, other locations must respond
        self.widgets.tab_modeswitch.modeSwitched.connect(
            lambda i: self.set_current_mode(i)
        )
        self.widgets.tab_modeswitch.modeSwitched.connect(
            self.widgets.mode_handler.refresh_button_colour
        )

        # mode_handler should respond to manual spin box changes
        for key, spinWidget in self.widgets.mode_handler.spinDict.items():
            spinWidget.simpleSpin.manualChanged.connect(
                lambda i=key: self.widgets.mode_handler.handle_manual_change(i)
            )

        # mode_handler should respond to user selection of radio button
        for key, radioWidget in self.widgets.mode_handler.radioDict.items():
            radioWidget.toggled.connect(
                lambda i, j=key: self.widgets.mode_handler.handle_radio_toggled(i, j)
            )

        # mode_handler should respond to ok, send, or cancel presses
        for key, buttonWidget in self.widgets.mode_handler.buttonDict.items():
            if isinstance(buttonWidget, OkButtonWidget) or isinstance(
                buttonWidget, OkSendButtonWidget
            ):
                buttonWidget.pressed.connect(
                    lambda i=key: self.widgets.mode_handler.handle_okbutton_click(i)
                )
            elif isinstance(buttonWidget, CancelButtonWidget):
                mode = self.widgets.mode_handler.get_mode(key)
                buttonWidget.pressed.connect(
                    lambda i=mode: self.widgets.mode_handler.commandSent(i)
                )

        ##### Expert Settings:
        # Expert handler should respond to manual value changes
        for key, spinWidget in self.widgets.expert_handler.spinDict.items():
            spinWidget.simpleSpin.manualChanged.connect(
                lambda i=key: self.widgets.expert_handler.handle_manual_change(i)
            )

        # mode_handler should respond to ok, send, or cancel presses
        for key, buttonWidget in self.widgets.expert_handler.buttonDict.items():
            if isinstance(buttonWidget, OkButtonWidget) or isinstance(
                buttonWidget, OkSendButtonWidget
            ):
                buttonWidget.pressed.connect(
                    lambda i=key: self.widgets.expert_handler.handle_okbutton_click(i)
                )
            elif isinstance(buttonWidget, CancelButtonWidget):
                buttonWidget.pressed.connect(
                    lambda: self.widgets.expert_handler.commandSent()
                )

        # Lines displayed on the charts page should update when the corresponding
        # buttons are toggled.
        for button in self.widgets.chart_buttons_widget.buttons:
            button.ToggleButtonPressed.connect(self.widgets.charts_widget.show_line)
            button.ToggleButtonReleased.connect(self.widgets.charts_widget.hide_line)
            button.on_press()  # Ensure states of the plots match states of buttons.
            button.toggle()

        # Plot data and measurements should update on a timer
        self.timer = QtCore.QTimer()
        self.timer.setInterval(16)  # just faster than 60Hz
        self.timer.timeout.connect(self.__emit_measurements_signal)
        self.timer.timeout.connect(self.data_handler.send_update_plots_signal)
        self.timer.timeout.connect(self.widgets.alarm_handler.update_alarms)
        self.timer.timeout.connect(self.widgets.mode_handler.update_values)
        self.timer.timeout.connect(self.widgets.expert_handler.update_values)
        self.timer.start()

        # Localisation needs to update widgets
        self.widgets.localisation_button.SetLocalisation.connect(
            self.widgets.normal_measurements.localise_text
        )

        return 0

    def __emit_measurements_signal(self) -> int:
        """
        Get the current status of the 'cycle' and 'readback' dbs and emit the
        measurements_signal signal.
        """
        self.MeasurementSignal.emit(self.get_db("cycle"), self.get_db("readback"))
        return 0

    def __check_db_name(self, database_name: str) -> str:
        """
        Check that the specified name is an actual database in NativeUI.
        """
        # Add "__" to database_name if it isn't already present.
        if not database_name.startswith("__"):
            database_name = "__%s" % database_name

        # Check against self.__database_list to ensure that only explicitely permitted
        # attributes can be accessed by this method.
        if not database_name in self.__database_list:
            raise AttributeError(
                "%s is not a recognised database in NativeUI" % database_name
            )

        return database_name

    def set_current_mode(self, mode):
        print("setting native ui mode")
        print(mode)
        self.currentMode = mode

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

    def get_db(self, database_name: str):
        """
        Return the contents of the specified database dict, assuming that it is present
        in __database_list.
        """
        with self.db_lock:
            return getattr(
                self,
                "_%s%s" % (type(self).__name__, self.__check_db_name(database_name)),
            )
        raise RuntimeError("Could not acquire database")

    def __set_db(self, database_name: str, payload) -> int:
        """
        Set the contents of the specified database dict, assuming that it is present in
        __database_list. Uses lock to avoid race conditions.
        """
        temp = self.get_db(database_name)
        for key in payload:
            temp[key] = payload[key]
        with self.db_lock:
            setattr(
                self,
                "_%s%s" % (type(self).__name__, self.__check_db_name(database_name)),
                temp,
            )
        return 0

    def __start_client(self):
        """
        Poll the microcontroller for current settings information.

        runs in other thread - works as long as super goes last and nothing
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

    def get_updates(self, payload: dict) -> int:
        """callback from the polling function, payload is data from socket """
        self.statusBar().showMessage(f"{payload}")
        logging.debug("recieved payload of type %s", payload["type"])
        if payload["type"] == "DATA":
            self.data_handler.set_db(payload["DATA"])
            old = self.ongoingAlarms
            self.ongoingAlarms = payload["alarms"]
        elif payload["type"] == "BATTERY":
            self.battery_handler.set_db(payload["BATTERY"])
        elif payload["type"] == "ALARM":
            self.__set_db("alarms", payload["ALARM"])
        elif payload["type"] == "TARGET":
            self.__set_db("targets", payload["TARGET"])
        elif payload["type"] == "READBACK":
            self.measurement_handler.set_db(payload["READBACK"])
        elif payload["type"] == "PERSONAL":
            self.personal_handler.set_db(payload["PERSONAL"])
        elif payload["type"] == "CYCLE":
            self.measurement_handler.set_db(payload["CYCLE"])
        elif payload["type"] == "DEBUG":
            pass
        else:
            logging.warning("Invalid payload type: %s", payload["type"])
            logging.debug("Content of invalid payload:\n%s", payload)
        return 0

    @Slot(str, str, float)
    def q_send_cmd(self, cmdtype: str, cmd: str, param: float = None) -> int:
        """send command to hevserver via socket"""
        check = self.send_cmd(cmdtype=cmdtype, cmd=cmd, param=param)
        if check:
            self.confirmPopup.addConfirmation(cmdtype + "   " + cmd)
        return 0

    @Slot(str)
    def q_ack_alarm(self, alarm: str) -> int:
        """acknowledge an alarm in the hevserver"""
        logging.debug("To MCU: Acknowledging alarm: %s", alarm)
        self.ack_alarm(alarm=alarm)
        return 0

    @Slot(str)
    def q_send_personal(self, personal: str) -> int:
        """send personal details to hevserver"""
        logging.debug("to MCU: Settung personal data: %s", personal)
        self.send_personal(personal=personal)
        return 0

    def __find_icons(self, iconext: str) -> str:
        """
        Locate the icons directory and return its path.

        Assumes that the cwd is in a git repo, and that the path of the icons folder
        relative to the root of the repo is "hev-display/assets/png/".
        """
        # Find the root of the git repo
        rootdir = git.Repo(os.getcwd(), search_parent_directories=True).git.rev_parse(
            "--show-toplevel"
        )
        icondir = os.path.join(rootdir, "hev-display", "assets", iconext)
        if not os.path.isdir(icondir):
            raise FileNotFoundError("Could not find icon directory at %s" % icondir)

        return icondir

    def __find_configs(self) -> str:
        """
        Locate the config files directory and return its path.

        Assumes that the cwd is in a git repo, and that the path of the icons folder
        relative to the root of the repo is "NativeUI/configs".
        """
        # Find the root of the git repo
        rootdir = git.Repo(os.getcwd(), search_parent_directories=True).git.rev_parse(
            "--show-toplevel"
        )
        configdir = os.path.join(rootdir, "NativeUI", "configs")
        if not os.path.isdir(configdir):
            raise FileNotFoundError("Could not find icon directory at %s" % configdir)

        return configdir


# from PySide2.QtQml import QQmlApplicationEngine


def parse_command_line_arguments() -> argparse.Namespace:
    """
    Returns the parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Plotting script for the HEV lab setup"
    )
    parser.add_argument(
        "-d", "--debug", action="count", default=0, help="Show debug output"
    )
    parser.add_argument(
        "-w",
        "--windowed",
        action="store_true",
        default=False,
        help="Run the UI in wondowed mode",
    )
    parser.add_argument(
        "-r", "--resolution", action="store", dest="resolution", type=str
    )
    return parser.parse_args()


def set_logging_level(debug_level: int) -> int:
    """
    Set the level of logging output according to the value of debug_level:
    0 = Warning
    1 = Info
    2 = Debug
    """
    if debug_level == 0:
        logging.getLogger().setLevel(logging.WARNING)
    elif debug_level == 1:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.DEBUG)
    return 0


def interpret_resolution(input_string: str) -> list:
    """
    Convert a string to a pair of numbers specifying the window size.

    Given a string of the form "[int][*][int]" where [*] is and non-numerical character,
    returns a list [int, int]. If the provided string is None or cannot be interpreted,
    returns the default window size [1920, 1080].
    """
    default_size = [1920, 1080]
    if input_string is None:
        return default_size

    dimensions = [val for val in re.findall("\d*", input_string) if val != ""]
    if len(dimensions) != 2:
        logging.warning("Unsupported resolution argument: %s", input_string)
        return default_size

    try:
        dimensions = [int(val) for val in dimensions]
    except ValueError:
        logging.warning(
            "Resolution argument '%s' could not be interpreted as numerical values."
            "Values must be integer numbers of pixels on x and y respectively,"
            "e.g. 1920x1080.",
            input_string,
        )
        return default_size

    return dimensions


def set_window_size(window, resolution: str = None, windowed: bool = False) -> int:
    """
    Set the size and position of the window.

    By default the window will be borderless, 1920x1080 pixels, and positioned at 0,0.
    If the "windowed" argument is True, the window will be bordered. Uses
    interpret_resolution to extract size parameters from the "resolution" string. If the
    string cannot be interpreted, or the resolution argument is None, uses
    interpret_resolution's default size.
    """
    window_size = interpret_resolution(resolution)
    window.setFixedSize(*window_size)

    if not windowed:
        window.move(0, 0)
        window.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    return 0


if __name__ == "__main__":
    # parse args and setup logging
    command_line_args = parse_command_line_arguments()
    print(command_line_args)
    set_logging_level(command_line_args.debug)

    # setup pyqtplot widget
    app = QApplication(sys.argv)
    dep = NativeUI()
    set_window_size(
        dep,
        resolution=command_line_args.resolution,
        windowed=command_line_args.windowed,
    )

    dep.show()
    app.exec_()
