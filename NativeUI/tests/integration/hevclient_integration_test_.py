import time

import pytest
import hevclient
import tempfile
from hevclient import HEVClient
import os
import signal
from pathlib import Path
from subprocess import Popen, TimeoutExpired

"""
Create hevclient WITH a hevserver running and assert expected hevclient state.
Make sure your PYTHONPATH var is set to the full path of '/<your_hev_root_dir>/hev/NativeUI'.
"""

# Overwrite the mm file for OS agnostic testing
hevclient.mmFileName = tempfile.gettempdir() + os.path.sep + 'HEVCLIENT_last_Data.mmap'


def test_hev_client():
    """Assert HEVClient state with backround ArduinoEmulator.py and hevserver.py running"""
    _assert_posix()
    _assert_pythonpath()
    process_group = None
    try:
        process_group = _run_setupscripts_log_err()
        print(process_group.pid)
        assert (process_group.pid > 0)
        # TODO assert no critical errs recorded in err_log file
        time.sleep(2) # give time for the scripts to complete
        # test what we need to do on HEVClient (won't work because we're in a different proc?)
        hevclient = HEVClient(True)
        # TODO assert no critical errs recorded in caplog
    finally:
        if process_group is not None:
            _kill_process_group(process_group.pid)


def _kill_process_group(pid: int):
    if pid is not None and pid > 0:
        try:
          os.killpg(os.getpgid(pid), signal.SIGTERM)
        except Exception as e:
            print(e)
            #pass

def _assert_posix():
    assert (os.name == 'posix')


def _assert_pythonpath():
    pythonpath_key = "$PYTHONPATH"
    pythonpath_val = os.path.expandvars(pythonpath_key)
    if pythonpath_val == pythonpath_key:
        pytest.fail(msg="Please set the $PYTHONPATH env var")


def _run_setupscripts_log_err():
    pythonpath_val = os.path.expandvars("$PYTHONPATH")
    myenv = {"PYTHONPATH": pythonpath_val}
    pypath = Path(pythonpath_val)
    proj_root_path = str(pypath.parent.absolute())

    # Run with preexec_fn=os.setid - is run after fork() but before exec() to get a sessionId for
    # killing child processes spawned off the shell (means that SIGTERMing the parent shell SIGTERMs children)
    process_group = Popen([
        """
        (. ./.hev_env/bin/activate ;
         ./raspberry-dataserver/ArduinoEmulator.py -f raspberry-dataserver/share/B6-20201207.dump ;
         sleep 1 ;
         ./NativeUI/tests/integration/stderr_scripts/run_hevclient.py
         ) 2>>err_log
        """ # 2>>err_log
    ],
        cwd=proj_root_path,
        shell=True,
        env=myenv,
        # stderr=subprocess.PIPE, stdout=subprocess.PIPE, # Don't use - overrides capfd
        preexec_fn=os.setsid)

    time.sleep(2)
    # stdout & stderr capture fails if timeout fires in communicate(timeout=).
    # Without timeout, communicate() blocks until the process completes successfully capturing out and err, but with
    # timeout, TimeoutExpired exception returns un-populated tuple.
    #with pytest.raises(TimeoutExpired):
    #     #captured_out, captured_err = process_group.communicate(timeout=3) # no captured out/err if timeout fires
    #      process_group.communicate(timeout=3)  # no captured out/err if timeout fires
    #     #Note, process is not killed if the timeout expires, so in order to cleanup properly, a well-behaved
    #     #application should kill the child process and finish communication. I'm using a process group for that to
    #     #ensure all spawned child processes are also killed (rather than just proc.kill())

    return process_group

# @pytest.mark.asyncio
# async def no_test_hev_client_start_required_background_processes(capfd, caplog):
#     """Assert HEVClient state with backround ArduinoEmulator.py and hevserver.py running"""
#     _assert_posix()
#     _assert_pythonpath()
#     process_group = await _run_arduino_asyncio()
#     await asyncio.sleep(3)  # wait few secs to ensure we capture enough stderr (if present)
#     out_err_capture = capfd.readouterr()
#     try:
#         for record in caplog.records:
#             assert record.levelname != "ERROR"
#
#         # assert(process_group.returncode == 0)
#         assert (process_group.pid > 0)
#         assert ('' == out_err_capture.err)
#
#         # print(out_err_capture.err)
#         # print(out_err_capture.out)
#     except Exception as e:
#         pytest.fail(e)
#     finally:
#         _kill_process_group(process_group.pid)


# async def _run_arduino_asyncio() -> asyncio.subprocess.Process:
#     """Run the pip env and Arduino emulator and return the Process as a process group"""
#     pythonpath_val = os.path.expandvars("$PYTHONPATH")
#     myenv = {"PYTHONPATH": pythonpath_val}
#     pypath = Path(pythonpath_val)
#     proj_root_path = str(pypath.parent.absolute())
#
#     process_group = await asyncio.create_subprocess_shell(
#         "source .hev_env/bin/activate"
#         + " && raspberry-dataserver/ArduinoEmulator.py -f raspberry-dataserver/share/B6-20201207.dump"
#         + " && NativeUI/tests/integration/stderr_scripts/run_hevclient.py",
#         cwd=proj_root_path,
#         shell=True,
#         env=myenv,
#         preexec_fn=os.setsid)
#
#     return process_group
