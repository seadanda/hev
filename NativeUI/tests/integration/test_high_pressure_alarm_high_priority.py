"""
- give NativeUI.get_updates() a fake payload of a high pressure alarm at high priority.
- that triggers NativeUI.set_alarms_db() which sets __alarms DB
- hev_alarms.updateAlarms() is run regularly to check for new alarms. When new alarms are added to NativeUI.__alarms hev_alarms.updateAlarms() triggers.
- hev_alarms.updateAlarms adds the alarm to the alarmDict, creates an alarm popup, and adds it to the alarm table displayed in the UI.
"""

# NativeUI.get_updates()
# NativeUI.set_alarms_db()
# __alarms DB Updated
# hev_alarms.updateAlarms()
# abstractAlarm

# TODO get a fake payload from the MCU side. Currently (8.4.21) not available as MCU and UI are not linked.

import json
from unittest.mock import patch
import os
import sys
from PySide2.QtWidgets import QApplication
import time
import _thread

current_path = os.path.abspath(os.getcwd())
root_path = os.path.abspath(current_path + "/NativeUI")
sys.path.append(root_path)

print(root_path)

from NativeUI import NativeUI
import hevclient

# TODO:
# - Sort Threading: In order to test the UI, the PyQT app needs to be running. This is controlled by app.exec_() (line 110), however when the app is running the main thread is locked out of firing off any other functions (i.e. test_high_pressure_alarm_high_priority()). Currently, the test_high_pressure_alarm_high_priority() test function runs in a secondary thread which doesn't interact with the app running in the main thread.
# - Assert that the __alarms DB is modified correctly (line 77-79)


def test_high_pressure_alarm_high_priority(NativeUI):
    """
    The intention of this test is to solve the risk with Risk ID: SW11.
    When excessive airway pressure is applied the microcontroller should send a High Pressure Alarm at a High Priority. This integration test tests from the point when that payload is fed into the UI. It will test that the payload will propgate through NativeUI app correctly and create a popup and add the alarm to the list of alarms.
    """
    myNativeUI = NativeUI

    # define vars
    popup_activated = False
    list_activated = False
    table_activated = False

    # define mock functions
    def mock_popup():
        nonlocal popup_activated
        print("popup here")
        popup_activated = True

    def mock_list():
        nonlocal list_activated
        list_activated = True

    def mock_table():
        nonlocal table_activated
        table_activated = True

    # replace update_alarms function calls with my own calls
    patch.object(myNativeUI.widgets.alarm_tab.popup, "addAlarm", new=mock_popup)
    patch.object(myNativeUI.widgets.alarm_tab.list, "addAlarm", new=mock_list)
    patch.object(
        myNativeUI.widgets.alarm_table_tab.table, "addAlarmRow", new=mock_table
    )

    # Give NativeUI.get_updates() a fake payload
    fake_alarm_json = "tests/integration/fixtures/sw11.json"
    fake_payload = json.load(open(fake_alarm_json))
    print(fake_payload)
    myNativeUI.get_updates(fake_payload)

    # Check __alarms is modified
    alarm_db = myNativeUI.get_db("alarms")
    print("\n***", alarm_db, "\n")

    # __define_connections calls alarm_widgets.tab_alarms.update_alarms every 16ms and starts when NativeUI is initialized.

    wait_time = 5
    count = 0
    while count < wait_time:
        print("waiting " + str(count + 1) + "s out of 5s")
        count = count + 1
        time.sleep(1)
        pass

    # (In Stubs) Capture newAbstractAlarm and query it for alarm code and priority set a flag if so.

    print("\nRunning tests \n")

    # After wait, check for flags set.
    assert popup_activated is True, "popup.addAlarm(newAbstractAlarm) not called."
    assert list_activated is True, "list.addAlarm(newAbstractAlarm) not called."
    assert table_activated is True, "table.addAlarm(newAbstractAlarm) not called."

    return


def main():
    hevclient.mmFileName = "tests/integration/fixtures/HEVClient_lastData.mmap"

    app = QApplication()
    myNativeUI = NativeUI()

    _thread.start_new_thread(sw11, (myNativeUI,))
    app.exec_()

    wait_time = 5
    count = 0
    while count < wait_time:
        print("waiting " + str(count + 1) + "s out of 5s")
        count = count + 1
        time.sleep(1)
        pass
    _thread.exit()
    sys.exit()

    return


if __name__ == "__main__":
    main()
