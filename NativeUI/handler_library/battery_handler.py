import logging
from handler_library.handler import PayloadHandler
from PySide2.QtCore import Signal, QObject


class BatteryHandler(PayloadHandler):
    """
    Subclass of the PayloadHandler class (handler.py) to handle alarm data.
    """

    UpdateBatteryDisplay = Signal(dict)

    def __init__(self, *args, **kwargs):
        super().__init__(["BATTERY"], *args, **kwargs)

    def active_payload(self, *args, **kwargs) -> int:
        """
        When battery information is set, interprets it to construct the battery status
        and emits the UpdateBatteryDisplay signal containing that status as a dict.
        """
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
            raise TypeError(
                "Battery Percentage (entry 'bat85' in the battery payload) is not 1 or 2."
            )
