#! /usr/bin/env python3

import pytest
import sys
import json
from NativeUI import NativeUI
from PySide2.QtWidgets import QApplication
import numpy as np
import hevclient

hevclient.mmFileName = "NativeUI/tests/integration/fixtures/HEVClient_lastData.mmap"


@pytest.fixture(scope="session", autouse=True)
def widget():
    app = QApplication(sys.argv)
    widget = NativeUI()
    return widget


# Test default values of databases(no set method involved)
def test_must_return_if_raises_attribute_error_when_false_db_item_is_got_from_get_db(
    widget,
):
    with pytest.raises(AttributeError):
        widget.get_db("__false_db_item")


def test_must_return_correct_db_item_from_get_db_data(widget):
    assert widget.get_db("__data") == {} and widget.get_db("data") == {}


def test_must_return_correct_db_item_from_get_db_readback(widget):
    assert widget.get_db("__readback") == {} and widget.get_db("readback") == {}


def test_must_return_correct_db_item_from_get_db_cycle(widget):
    assert widget.get_db("__cycle") == {} and widget.get_db("cycle") == {}


def test_must_return_correct_db_item_from_get_db_battery(widget):
    assert widget.get_db("__battery") == {} and widget.get_db("battery") == {}


def test_must_return_correct_db_item_from_get_db_plots(widget):
    plot_history_length = 1000
    plot_dict = {
        "data": np.zeros((plot_history_length, 5)),
        "timestamp": list(el * (-1) for el in range(plot_history_length))[::-1],
        "pressure": list(0 for _ in range(plot_history_length)),
        "flow": list(0 for _ in range(plot_history_length)),
        "volume": list(0 for _ in range(plot_history_length)),
        "pressure_axis_range": [0, 20],
        "flow_axis_range": [-40, 80],
        "volume_axis_range": [0, 80],
    }
    assert (
        widget.get_db("__plots").keys() == plot_dict.keys()
        and widget.get_db("plots").keys() == plot_dict.keys()
    )


def test_must_return_correct_db_item_from_get_db_alarms(widget):
    assert widget.get_db("__alarms") == [] and widget.get_db("alarms") == []


def test_must_return_correct_db_item_from_get_db_targets(widget):
    assert widget.get_db("__targets") == {} and widget.get_db("targets") == {}


def test_must_return_correct_db_item_from_get_db_personal(widget):
    assert widget.get_db("__personal") == {} and widget.get_db("personal") == {}


# Test set methods with sample payloads
def test_must_return_0_for_set_data_db(widget):
    with open("/home/pi/hev/samples/dataSample.json", "r") as f:
        data_payload = json.load(f)
        assert widget.set_data_db(data_payload) == 0


def test_must_return_0_for_set_targets_db(widget):
    with open("/home/pi/hev/samples/targetSample.json", "r") as g:
        target_payload = json.load(g)
        assert widget.set_targets_db(target_payload) == 0


def test_must_return_0_for_set_readback_db(widget):
    with open("/home/pi/hev/samples/readbackSample.json", "r") as f:
        readback_payload = json.load(f)
        assert widget.set_readback_db(readback_payload) == 0


def test_must_return_0_for_set_cycle_db(widget):
    with open("/home/pi/hev/NativeUI/tests/cycleSample.json", "r") as f:
        cycle_payload = json.load(f)
        assert widget.set_cycle_db(cycle_payload) == 0


def test_must_return_0_for_set_battery_db(widget):
    with open("/home/pi/hev/samples/batterySample.json", "r") as f:
        battery_payload = json.load(f)
        assert widget.set_battery_db(battery_payload) == 0


def test_must_return_0_for_set_plots_db(widget):
    with open("/home/pi/hev/samples/dataSample.json", "r") as f:
        data_payload = json.load(f)
        assert widget.set_plots_db(data_payload) == 0


def test_must_return_error_if_not_data_is_sent_as_payload_for_set_plots_db(widget):
    with open("/home/pi/hev/samples/batterySample.json", "r") as f:
        battery_payload = json.load(f)
        with pytest.raises(KeyError):
            widget.set_plots_db(battery_payload)


def test_must_return_0_when__update_plot_ranges_correctly(widget):
    assert widget.__update_plot_ranges() == 0


def test_must_return_0_for_set_alarms_db(widget):
    with open("/home/pi/hev/samples/alarmSample.json", "r") as f:
        alarm_payload = json.load(f)
        assert widget.set_alarms_db(alarm_payload) == 0


def test_must_return_0_for_set_personal_db(widget):
    with open("/home/pi/hev/NativeUI/tests/personalSample.json", "r") as f:
        personal_payload = json.load(f)
        assert widget.set_personal_db(personal_payload) == 0


# Asyncio can handle event loops, but we need to add more interaction i think
# @pytest.mark.asyncio
# async def test_start_client(widget):
#    with pytest.raises(RuntimeError):
#        widget.start_client()


def test_get_updates_data_payload(widget):
    with open("/home/pi/hev/samples/dataSample.json", "r") as f:
        data_payload = json.load(f)
        widget.get_updates(data_payload)


def test_get_updates_wrong_payload(widget):
    fake_payload = {
        "types": "Fake",
        "pressure": 1200000.0,
        "flow": 777000.0,
        "volume": 1.0,
    }
    with pytest.raises(KeyError):
        widget.get_updates(fake_payload)


def test_must_return_0_when_q_send_cmd(widget):
    assert widget.q_send_cmd(str, str) == 0


def test_must_return_0_when_q_ack_alarm_when_out_conection(widget):
    with pytest.raises(ConnectionError):
        widget.q_ack_alarm(str)


def test_must_return_0_when_q_send_personal_when_out_conection(widget):
    with pytest.raises(ConnectionError):
        widget.q_send_personal(str)


def test_must_return_0_when__find_icons_directory(widget):
    assert widget.__find_icons() == "/home/pi/hev/hev-display/assets/png"
