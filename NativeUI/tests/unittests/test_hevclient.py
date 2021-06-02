"""
Create hevclient WITHOUT a hevserver running and assert expected hevclient state.
Make sure your PYTHONPATH var is set to the full path of '/<your_hev_root_dir>/hev/NativeUI'.
"""
import tempfile
import os
import time
import hevclient
from hevclient import HEVClient
import pytest


# Overwrite the mm file for OS agnostic testing
hevclient.mmFileName = tempfile.gettempdir() + os.path.sep + "HEVCLIENT_last_Data.mmap"


def setup_module():
    """pytest module setup"""
    _assert_posix()
    _assert_pythonpath()


def test_hev_client_expected_default_state(caplog):
    """Create the HEVClient in isolation without a hevserver running"""
    myhevclient = HEVClient()
    _hev_client_expected_state(myhevclient, caplog)


def test_hev_client_expected_log_error_on_command(caplog):
    """Create the HEVClient in isolation without a hevserver running"""
    myhevclient = HEVClient(False)
    myhevclient.send_cmd("CMD", "fake")
    _hev_client_expected_state(myhevclient, caplog)


def _hev_client_expected_state(myhevclient: HEVClient, caplog):
    assert myhevclient.get_values() is None  # probably should return empty dict
    assert len(myhevclient.get_alarms()) == 0
    assert myhevclient.get_updates(None) is None
    assert myhevclient.get_cycle() is None
    assert myhevclient.get_logmsg() is None
    time.sleep(1)  # wait for the async log to be written
    for record in caplog.records:
        assert record.levelname != "CRITICAL"
    assert (
        "[Errno" in caplog.text
    )  # confirm message 'is the microcontroller running?' is logged 
    # Can't specify an err code as these are different across devices


def _assert_posix():
    assert os.name == "posix"


def _assert_pythonpath():
    pythonpath_key = "$PYTHONPATH"
    pythonpath_val = os.path.expandvars(pythonpath_key)
    if pythonpath_val == pythonpath_key:
        pytest.fail(msg="Please set the $PYTHONPATH env var")
