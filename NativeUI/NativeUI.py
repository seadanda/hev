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
__version__ = "0.1.1"
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
from global_widgets.global_send_popup import confirmPopup, SetConfirmPopup
from widget_library.ok_cancel_buttons_widget import (
    OkButtonWidget,
    OkSendButtonWidget,
    CancelButtonWidget,
)
from hevclient import HEVClient
from PySide2.QtCore import Slot, QTimer, Qt
from PySide2.QtGui import QColor, QFont, QPalette
from ui_layout import Layout
from ui_widgets import Widgets
from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QDialog,
    QStackedWidget,
)

# from handler_library.alarm_handler import AlarmHandler
from handler_library.battery_handler import BatteryHandler
from handler_library.data_handler import DataHandler
from handler_library.measurement_handler import MeasurementHandler

# from handler_library.personal_handler import PersonalHandler
from widget_library.expert_handler import ExpertHandler
from mode_widgets.personal_handler import PersonalHandler
from mode_widgets.mode_handler import ModeHandler
from mode_widgets.clinical_handler import ClinicalHandler
from alarm_widgets.alarm_handler import AlarmHandler

# from handler_library.readback_handler import ReadbackHandler
from global_widgets.global_typeval_popup import TypeValuePopup, AbstractTypeValPopup
from widget_library.numpad_widget import NumberpadWidget, AlphapadWidget

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s \n (%(pathname)s, %(lineno)s)",
)


class NativeUI(HEVClient, QMainWindow):
    """
    Main application with client logic

    Subclassed HEVClient for client logic, and QMainWindow for display.

    Extends its base classes with the following methods:

    __define_connections - connects widget signals and slots to allow the UI to
    function. Called once during initialisation.

    __find icons - locate the directory containing icons used for UI buttons and
    displays. Called once during initialisation.

    __find_configs - locate the directory containing config files used by the UI. Called
    once during initialisation.

    set_current_mode - TODO: deprecated, remove.

    get_updates - Overrides the placeholder get_updates method of HEVClient. Passes
    payloads to handlers. Called whenever a new payload is read in.

    change_page (Slot) - switches the page shown in the page_stack. Called whent the
    page buttons are pressed or whenever a popup needs to show a specific page.

    q_send_cmd (Slot) - send a command to the MCU.

    q_ack_alarm (Slot) - acknowledge a recieved alarm.

    q_send_personal (Slot) - send personal information to the MCU.
    """

    def __init__(self, resolution: list, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set the resolution of the display window
        self.screen_width = resolution[0]
        self.screen_height = resolution[1]

        # Set up available modes
        self.modeList = ["PC/AC", "PC/AC-PRVC", "PC-PSV", "CPAP"]
        self.currentMode = self.modeList[0]

        # Import settings from config files.
        # Colorblind friendly ref: https://i.stack.imgur.com/zX6EV.png
        config_path = self.__find_configs()
        self.localisation_files = self.__find_localisation_files(config_path)
        with open(os.path.join(config_path, "colors.json")) as infile:
            self.colors = json.load(infile)
            for key in self.colors:
                self.colors[key] = QColor.fromRgb(*self.colors[key])
        with open(os.path.join(config_path, "text_english.json")) as infile:
            self.text = json.load(infile)

        # Set up fonts based on the screen resolution. text_font and value_font are 20
        # and 40px respectively for 1920*1080.
        self.text_font = QFont("Sans Serif", resolution[0] / 96)
        self.value_font = QFont("Sans Serif", 2 * resolution[0] / 96)

        # Import icons
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

        # Appearance settings
        palette = self.palette()
        palette.setColor(QPalette.Window, self.colors["page_background"])

        # Set up the handlers
        self.battery_handler = BatteryHandler()
        self.data_handler = DataHandler(plot_history_length=1000)
        self.measurement_handler = MeasurementHandler()
        self.personal_handler = PersonalHandler(self)
        self.mode_handler = ModeHandler(self)  # , self.mode_confirm_popup)
        self.expert_handler = ExpertHandler(self)
        self.clinical_handler = ClinicalHandler(self)
        self.alarm_handler = AlarmHandler(self)
        self.__payload_handlers = [
            self.battery_handler,
            self.data_handler,
            self.measurement_handler,
            self.personal_handler,
            self.mode_handler,
            self.expert_handler,
            self.clinical_handler,
            self.alarm_handler,
        ]
        self.messageCommandPopup = SetConfirmPopup(self)
        self.typeValPopupNum = AbstractTypeValPopup(self,'numeric')#TypeValuePopup(self, NumberpadWidget(self))
        self.typeValPopupAlpha = AbstractTypeValPopup(self,'alpha')#TypeValuePopup(self, AlphapadWidget(self))

        # Create all of the widgets and place them in the layout.
        self.widgets = Widgets(self)
        self.layouts = Layout(self, self.widgets)

        # Setup, main_display, and popups created in a stack so we can only show one at
        # a time.
        self.messageCommandPopup = SetConfirmPopup(self)
        self.confirmPopup = confirmPopup(self, self)
        self.confirmPopup.show()
        self.main_display = QWidget(self)
        self.main_display.setLayout(self.layouts.global_layout())
        self.startupWidget = QDialog(self)
        self.startupWidget.setLayout(self.layouts.startup_layout())
        self.startupWidget.setPalette(palette)
        self.startupWidget.setAutoFillBackground(True)

        self.display_stack = QStackedWidget(self)
        for widget in [
            self.typeValPopupNum,
            self.typeValPopupAlpha,
            self.messageCommandPopup,
            #self.confirmPopup,
            self.main_display,
            self.startupWidget,
        ]:
            self.display_stack.addWidget(widget)
        self.setCentralWidget(self.display_stack)

        # Set up status bar and window title (the title is only shown in windowed mode).
        self.statusBar().showMessage("Waiting for data")
        self.statusBar().setStyleSheet("color:" + self.colors["page_foreground"].name())
        self.setWindowTitle(self.text["ui_window_title"].format(version=__version__))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.widgets.version_display_widget.update_UI_version(__version__)
        self.widgets.version_display_widget.update_UI_hash(self.__get_hash())

        # Connect widgets
        self.__define_connections()

        # Update page buttons to match the shown view
        self.display_stack.setCurrentWidget(self.startupWidget)
        self.widgets.page_buttons.buttons[0].on_press()

    def __find_localisation_files(self, config_path: str) -> list:
        """
        List the availale localisation files.
        """
        files_list = [
            os.path.join(config_path, file)
            for file in ["text_english.json", "text_portuguese.json"]
        ]

        for file in files_list:
            assert os.path.isfile(file)

        return files_list

    def __get_hash(self) -> str:
        """
        Get the hash of the current commit.
        """
        repo = git.Repo(search_parent_directories=True)
        return repo.head.object.hexsha

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
        for key, radio in self.widgets.startup_handler.settingsRadioDict.items():
            radio.toggled.connect(
                lambda i, j=key: self.widgets.startup_handler.handle_settings_radiobutton(
                    i, j
                )
            )
        for radio in self.widgets.startup_handler.modeRadioDict.values():
            radio.toggled.connect(
                lambda i, j=radio: self.widgets.startup_handler.handle_mode_radiobutton(
                    i, j
                )
            )

        # TODO: command sending
        self.widgets.nextButton.pressed.connect(
            lambda: self.display_stack.setCurrentWidget(self.main_display)
        )
        self.widgets.skipButton.pressed.connect(
            lambda: self.display_stack.setCurrentWidget(self.main_display)
        )

        # self.widgets.skipButton.pressed.connect(
        #     self.widgets.startup_handler.handle_sendbutton
        # )
        # self.widgets.backButton.pressed.connect(
        #     lambda i=self.widgets.startup_stack: self.widgets.startup_handler.handle_backbutton(
        #         i
        #     )
        # )

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

        # Start button should raise the startup widget.
        self.widgets.ventilator_start_stop_buttons_widget.button_start.pressed.connect(
            lambda: self.display_stack.setCurrentWidget(self.startupWidget)
        )

        ##### Mode:
        # When mode is switched from mode page, various other locations must respond
        for widget in self.mode_handler.spinDict.values():
            self.mode_handler.UpdateModes.connect(widget.update_value)
            widget.simpleSpin.manualChanged.connect(
                lambda i=widget: self.clinical_handler.setpoint_changed(i)
            )
            widget.simpleSpin.manualChanged.connect(
                lambda i=widget: self.mode_handler.propagate_modevalchange(i)
            )

        for widget in self.mode_handler.mainSpinDict.values():
            self.mode_handler.UpdateModes.connect(widget.update_value)
            widget.simpleSpin.manualChanged.connect(
                lambda i=widget: self.clinical_handler.setpoint_changed(i)
            )
            widget.simpleSpin.manualChanged.connect(
                lambda i=widget: self.mode_handler.propagate_modevalchange(i)
            )
            # widget.simpleSpin.manualChanged.connect(lambda i=widget: self.mode_handler.mode_value(i))

        self.mode_handler.modeSwitched.connect(lambda i: self.set_current_mode(i))
        self.mode_handler.modeSwitched.connect(
            lambda i: self.widgets.tab_modeswitch.update_mode(i)
        )
        self.mode_handler.modeSwitched.connect(self.mode_handler.refresh_button_colour)

        # when mode is switched from modeSwitch button, other locations must respond
        self.widgets.tab_modeswitch.modeSwitched.connect(
            lambda i: self.set_current_mode(i)
        )
        self.widgets.tab_modeswitch.modeSwitched.connect(
            self.mode_handler.refresh_button_colour
        )

        # mode_handler should respond to manual spin box changes
        for key, spin_widget in self.mode_handler.spinDict.items():
            spin_widget.simpleSpin.manualChanged.connect(
                lambda i=key: self.mode_handler.handle_manual_change(i)
            )
            # if 'clinical' in key:
            #     spin_widget.simpleSpin.manualChanged.connect(
            #         lambda i=spin_widget, j=key: self.clinical_handler.setpoint_changed(i,j)
            #     )

        for key, spin_widget in self.mode_handler.mainSpinDict.items():
            spin_widget.simpleSpin.manualChanged.connect(
                lambda i=key: self.mode_handler.handle_manual_change(i)
            )
            spin_widget.simpleSpin.programmaticallyChanged.connect(
                lambda i=key: self.mode_handler.handle_manual_change(i)
            )

        # mode_handler should respond to user selection of radio button
        for key, radio_widget in self.mode_handler.radioDict.items():
            radio_widget.toggled.connect(
                lambda i, j=key: self.mode_handler.handle_radio_toggled(i, j)
            )

        # mode_handler should respond to ok, send, or cancel presses
        for key, button_widget in self.mode_handler.buttonDict.items():
            if isinstance(button_widget, (OkButtonWidget, OkSendButtonWidget)):
                button_widget.pressed.connect(
                    lambda i=key: self.mode_handler.handle_okbutton_click(i)
                )
            elif isinstance(button_widget, CancelButtonWidget):
                mode = self.mode_handler.get_mode(key)
                button_widget.pressed.connect(self.mode_handler.commandSent)

        for key, button_widget in self.mode_handler.mainButtonDict.items():
            if isinstance(button_widget, (OkButtonWidget)):
                button_widget.clicked.connect(
                    self.mode_handler.handle_mainokbutton_click
                )
            elif isinstance(button_widget, CancelButtonWidget):
                # mode = self.mode_handler.get_mode(key)
                button_widget.clicked.connect(self.mode_handler.commandSent)

        for key, spin_widget in self.clinical_handler.limSpinDict.items():
            spin_widget.simpleSpin.manualChanged.connect(
                lambda i=key: self.clinical_handler.handle_manual_change(i)
            )

        for key, spin_widget in self.clinical_handler.setSpinDict.items():
            spin_widget.simpleSpin.manualChanged.connect(
                lambda i=spin_widget: self.clinical_handler.setpoint_changed(i)
            )
            spin_widget.simpleSpin.manualChanged.connect(
                lambda i=key: self.clinical_handler.handle_manual_change(i)
            )
            spin_widget.simpleSpin.manualChanged.connect(
                lambda i=spin_widget: self.mode_handler.propagate_modevalchange(i)
            )

        for key, button_widget in self.clinical_handler.buttonDict.items():
            if isinstance(button_widget, (OkButtonWidget)):
                button_widget.clicked.connect(
                    self.clinical_handler.handle_okbutton_click
                )
            elif isinstance(button_widget, CancelButtonWidget):
                button_widget.clicked.connect(
                    self.clinical_handler.handle_cancelbutton_click
                )

        # for widget in (self.clinical_handler.setSpinDict.values()):
        #    self.clinical_handler.UpdateClinical.connect(widget.update_value)

        self.mode_handler.OpenPopup.connect(self.messageCommandPopup.populatePopup)
        self.mode_handler.OpenPopup.connect(
            lambda: self.display_stack.setCurrentWidget(self.messageCommandPopup)
        )
        self.messageCommandPopup.ModeSend.connect(self.mode_handler.sendCommands)

        self.expert_handler.OpenPopup.connect(self.messageCommandPopup.populatePopup)
        self.expert_handler.OpenPopup.connect(
            lambda: self.display_stack.setCurrentWidget(self.messageCommandPopup)
        )
        self.messageCommandPopup.ExpertSend.connect(self.expert_handler.sendCommands)

        self.clinical_handler.OpenPopup.connect(self.messageCommandPopup.populatePopup)
        self.messageCommandPopup.ClinicalSend.connect(
            self.clinical_handler.sendCommands
        )

        self.messageCommandPopup.cancelButton.pressed.connect(
            lambda: self.display_stack.setCurrentWidget(self.main_display)
        )
        self.messageCommandPopup.okButton.pressed.connect(
            lambda: self.display_stack.setCurrentWidget(self.main_display)
        )

        ##### Expert Settings:
        # Expert handler should respond to manual value changes
        for key, spin_widget in self.expert_handler.spinDict.items():
            spin_widget.simpleSpin.manualChanged.connect(
                lambda i=key: self.expert_handler.handle_manual_change(i)
            )

        # mode_handler should respond to ok, send, or cancel presses
        for key, button_widget in self.expert_handler.buttonDict.items():
            if isinstance(button_widget, OkButtonWidget) or isinstance(
                button_widget, OkSendButtonWidget
            ):
                button_widget.pressed.connect(
                    lambda i=key: self.expert_handler.handle_okbutton_click(i)
                )
            elif isinstance(button_widget, CancelButtonWidget):
                button_widget.pressed.connect(self.expert_handler.commandSent)

        for widget in self.expert_handler.spinDict.values():
            self.expert_handler.UpdateExpert.connect(widget.update_value)

        # Lines displayed on the charts page should update when the corresponding
        # buttons are toggled.
        for button in self.widgets.chart_buttons_widget.buttons:
            button.ToggleButtonPressed.connect(self.widgets.charts_widget.show_line)
            button.ToggleButtonReleased.connect(self.widgets.charts_widget.hide_line)
            button.on_press()  # Ensure states of the plots match states of buttons.
            button.toggle()

        # Plot data and measurements should update on a timer
        self.timer = QTimer()
        self.timer.setInterval(16)  # just faster than 60Hz
        self.timer.timeout.connect(self.data_handler.send_update_plots_signal)
        # self.timer.timeout.connect(self.widgets.alarm_handler.update_alarms)
        # self.timer.timeout.connect(self.mode_handler.update_values)
        # self.timer.timeout.connect(self.expert_handler.update_values)
        self.timer.start()

        # self.widgets.startup_handler.settingToggle.connect(self.widgets.spin_buttons.setStackWidget)
        # self.mode_handler.settingToggle.connect(self.widgets.spin_buttons.setStackWidget)

        self.alarm_handler.UpdateAlarm.connect(self.alarm_handler.handle_newAlarm)
        self.alarm_handler.NewAlarm.connect(self.widgets.alarm_popup.addAlarm)
        self.alarm_handler.NewAlarm.connect(self.widgets.alarm_list.addAlarm)
        self.alarm_handler.NewAlarm.connect(self.widgets.alarm_table.addAlarmRow)

        self.alarm_handler.RemoveAlarm.connect(self.widgets.alarm_popup.removeAlarm)
        self.alarm_handler.RemoveAlarm.connect(self.widgets.alarm_list.removeAlarm)

        # Localisation needs to update widgets
        self.widgets.localisation_button.SetLocalisation.connect(
            self.widgets.normal_measurements.localise_text
        )

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

    def set_current_mode(self, mode):
        """
        Set the current mode
        TODO: move to mode handler
        """
        print("setting native ui mode")
        print(mode)
        self.currentMode = mode

    def get_updates(self, payload: dict) -> int:
        """
        Callback from the polling function, payload is data from socket.

        Passes the payload to each of the handlers in self.__payload_handlers. If no
        handlers return 0, indicating that the payload is not dealt with by any handler,
        log a warning.
        """
        self.statusBar().showMessage(f"{payload}")
        logging.debug("recieved payload of type %s", payload["type"])

        payload_registered = False
        for handler in self.__payload_handlers:
            if handler.set_db(payload) == 0:
                payload_registered = True
        if not payload_registered:
            logging.warning("Handlers: Invalid payload type: %s", payload["type"])
            logging.debug("Content of invalid payload:\n%s", payload)

        return 0

    @Slot(str)
    def change_page(self, page_to_show: str) -> int:
        """
        Change the page shown in page_stack.
        """
        self.widgets.page_stack.setCurrentWidget(getattr(self.widgets, page_to_show))
        return 0

    @Slot(str, str, float)
    def q_send_cmd(self, cmdtype: str, cmd: str, param: float = None) -> int:
        """
        Send command to hevserver via socket.
        """
        logging.debug("to MCU: cmd: %s", cmd)
        check = self.send_cmd(cmdtype=cmdtype, cmd=cmd, param=param)
        if check:
            print('confirmed this command ' + cmdtype + '   ' + cmd)
            self.confirmPopup.addConfirmation(cmdtype + "   " + cmd)
            print('added popup')
            return 0
        else:
            print('failed this command ' + cmdtype + '   ' + cmd)
            return 1

    @Slot(str)
    def q_ack_alarm(self, alarm: str) -> int:
        """
        Acknowledge an alarm in the hevserver
        """
        logging.debug("To MCU: Acknowledging alarm: %s", alarm)
        self.ack_alarm(alarm=alarm)
        return 0

    @Slot(str)
    def q_send_personal(self, personal: str) -> int:
        """
        Send personal details to the hevserver.
        """
        logging.debug("to MCU: Setting personal data: %s", personal)
        self.send_personal(personal=personal)
        return 0


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
        window.setWindowFlags(Qt.FramelessWindowHint)
    return 0


if __name__ == "__main__":
    # parse args and setup logging
    command_line_args = parse_command_line_arguments()
    print(command_line_args)
    set_logging_level(command_line_args.debug)

    # setup pyqtplot widget
    app = QApplication(sys.argv)
    dep = NativeUI(interpret_resolution(command_line_args.resolution))
    set_window_size(
        dep,
        resolution=command_line_args.resolution,
        windowed=command_line_args.windowed,
    )

    dep.show()
    app.exec_()
