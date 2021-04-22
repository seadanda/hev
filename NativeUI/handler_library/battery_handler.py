import logging
from handler_library.handler import Handler
from PySide2.QtCore import Signal, QObject

# TODO: initially we tried to have a check so that the handler only signals the display
# elements when something changeds. Problem: when the UI starts up it takes a few
# seconds for display elements to become active (may be an artefact of X11 forwarding?),
# so for something like the battery which doesn't change fast, the initial signal to the
# display is missed, and no further signal gets sent because nothing is changing.
# Current workaround is to trigger the ative_payload every time get_db completes. Could
# reinstate the check but add an override so every nth payload triggers the signal
# regardless of whether data has changed, or force some update frequency (c.f. plots)?


class BatteryHandler(Handler, QObject):
    UpdateBatteryDisplay = Signal(dict)

    def __init__(self):
        super().__init__()
        QObject.__init__(
            self
        )  # Give ourselves access to the QObject Signal functionality.

    def active_payload(self) -> int:
        new_status = {}
        battery_data = self.get_db()

        # Update new_status
        try:
            new_status["on_mains_power"] = bool(battery_data["ok"])
        except KeyError:
            logging.debug("Keyerror in battery payload: 'ok'")
        try:
            new_status["on_battery_power"] = bool(battery_data["bat"])
        except KeyError:
            logging.debug("Keyerror in battery payload: 'bat'")
        try:
            new_status["battery_percent"] = self.compute_battery_percent(battery_data)
        except KeyError:
            logging.debug("Keyerror in battery payload: 'bat85'")
        try:
            if bool(battery_data["prob_elec"]):
                new_status["electrical_problem"] = "ERROR ELEC."
            else:
                new_status["electrical_problem"] = None
        except KeyError:
            logging.debug("Keyerror in battery payload: 'prob_elec'")

        # Sanity checks
        if new_status["on_mains_power"] == new_status["on_battery_power"]:
            # If there is conflicting information w.r.t. power source, report a problem
            new_status["on_mains_power"] = False
            new_status["on_battery_power"] = False
            new_status["electrical_problem"] = "ERROR ELEC."

        self.UpdateBatteryDisplay.emit(new_status)
        return 0

    def compute_battery_percent(self, battery_data: dict) -> float:
        """
        Determine the current battery percentage from the information in battery_data.

        As of 17/03/21 battery payloads only contain enough information to
        determine if the battery is above or below 85% battery life.

        Unless provided with specific information to the contrary, assume that the
        battery is on 0% so that we should never overestimate how much remains.
        """

        if battery_data["bat85"] == 1:
            return 85.0
        elif battery_data["bat85"] == 0:
            return 0.0
        else:
            raise TypeError('Battery Percentage (entry \'bat85\' in the battery payload) is not 1 or 2.')
