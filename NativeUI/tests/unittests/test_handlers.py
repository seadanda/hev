"""
Unit tests for the handler files.
"""

import json
import os
from unittest.mock import MagicMock, patch

from handler_library.handler import Handler
from handler_library.battery_handler import BatteryHandler


def test_handler():
    """
    Tests the default handler.
    Test for set_db and get_db to set the database from a given payload and compare the
    db imported from get_db.
    Test for if active_payload gets fired when set_db is called.
    """
    # Initalise the handler and import sample test json file
    handler = Handler(["TEST"])

    test_json_file_path = (
        os.environ["PYTHONPATH"].split(os.pathsep)[0]
        + "/tests/unittests/fixtures/testSample.json"
    )
    test_json = json.load(open(test_json_file_path))

    # Set the database for the imported json and get the database imported
    set_db_return = handler.set_db(test_json)
    db = handler.get_db()

    # Check if the input payload and output database are the same
    if test_json["TEST"] == db:
        payload_database_comparison = True
    else:
        payload_database_comparison = False

    # Mock active_payload to return true if it is called.
    handler.active_payload = MagicMock(return_value=True)

    # Check whether conditions have been met to pass test
    assert set_db_return == 0, "set_db does not return 0 for a valid payload"
    assert (
        handler.active_payload() is True
    ), "active_payload was not called when set_db was run."
    assert (
        payload_database_comparison is True
    ), "set_db does not set the inputted payload to the database."


def test_battery_handler():
    """
    Tests the battery_handler logic by giving active_payload a sample battery payload (NativeUI/tests/unittests/fixtures/batterySample.json) with a known output status (NativeUI/tests/unittests/fixtures/battery_status_output_sample.json).
    """
    # Initalise the battery handler and import sample battery json file
    batt_handler = BatteryHandler()

    batt_json_file_path = (
        os.environ["PYTHONPATH"].split(os.pathsep)[0]
        + "/tests/unittests/fixtures/batterySample.json"
    )
    batt_json = json.load(open(batt_json_file_path))

    # Set true/false variables
    UpdateBatteryDisplay_activated = False
    new_status_correctly_set = False
    batt_per_1_correctly_set = False
    batt_per_0_correctly_set = False

    # Compute battery percent payload information
    batt_per_1 = {"bat85": 1}
    batt_per_0 = {"bat85": 0}

    batt_handler.compute_battery_percent(batt_per_0)

    # Mock the get_db function to give the sample input json
    batt_handler.get_db = MagicMock(return_value=batt_json)

    # Mock function to replace UpdateBatteryDisplay which checks if the function has been called and whether the output status is correct.
    def mock_UpdateBatteryDisplay(new_status: dict):
        nonlocal UpdateBatteryDisplay_activated
        nonlocal new_status_correctly_set

        # Set activated variable to true to show that this function was called
        UpdateBatteryDisplay_activated = True

        # Check whether new_status is the expected output
        expected_status_file_path = (
            os.environ["PYTHONPATH"].split(os.pathsep)[0]
            + "/tests/unittests/fixtures/battery_status_output_sample.json"
        )
        expected_status = json.load(open(expected_status_file_path))

        if new_status == expected_status:
            new_status_correctly_set = True
        else:
            pass

    # Connect to active_payload signal
    batt_handler.UpdateBatteryDisplay.connect(mock_UpdateBatteryDisplay)
    # Run the battery handler logic
    batt_handler.active_payload()
    # Run the battery handler compute battery percent logic
    if batt_handler.compute_battery_percent(batt_per_1) == 85.0:
        batt_per_1_correctly_set = True

    if batt_handler.compute_battery_percent(batt_per_0) == 0.0:
        batt_per_0_correctly_set = True

    # Check whether conditions have been met to pass test
    assert (
        UpdateBatteryDisplay_activated is True
    ), "UpdateBatteryDisplay.emit(new_status) is not called."
    assert (
        new_status_correctly_set is True
    ), "Output of new_status does not match the expected output."
    assert (
        batt_per_1_correctly_set is True
    ), "compute_battery_percent does not return 85% when bat85 is set to 1."
    assert (
        batt_per_0_correctly_set is True
    ), "compute_battery_percent does not return 0% when bat85 is set to 0."
