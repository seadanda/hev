"""
Create hevclient WITH a hevserver running and assert expected hevclient state and function calls.
Make sure your PYTHONPATH var is set to the full path of '/<your_hev_root_dir>/hev/NativeUI'.
"""

import os
import tempfile
import time
import pytest
import hevclient
from hevclient import HEVClient


# Overwrite the mm file for OS agnostic testing
hevclient.mmFileName = tempfile.gettempdir() + os.path.sep + "HEVCLIENT_last_Data.mmap"


def set_up():
    """pytest module setup"""
    _assert_posix()
    _assert_pythonpath()


def test_hev_client_state(caplog):
    """Assert HEVClient state with background processes running (hevserver/Arduino)"""
    HEVClient(True)
    time.sleep(1)  # give enough time for het to log
    # confirm message 'is the microcontroller running?' is NOT logged using err code
    assert "[Errno 61]" not in caplog.text

    # TODO assert hevclient.method tests
    # myhevclient.send_cmd("CMD", "blah")


def _assert_posix():
    assert os.name == "posix"


def _assert_pythonpath():
    pythonpath_key = "$PYTHONPATH"
    pythonpath_val = os.path.expandvars(pythonpath_key)
    if pythonpath_val == pythonpath_key:
        pytest.fail(msg="Please set the $PYTHONPATH env var")
