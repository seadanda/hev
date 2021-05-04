# Tests Documentation

## Unit Tests

To run all unit tests in the `NativeUI/tests/unittests` dir on a Raspberry Pi or VM, run the following 
(adjust the full path to your NativeUI directory accordingly):

```bash
. .hev_env/bin/activate
export PYTHONPATH=/home/pi/hev/NativeUI
pytest NativeUI/tests/unittests
```

To run a single unit test file, set the environment as above and specify the test file:

```bash
pytest NativeUI/tests/unittests/test_hevclient.py
```

## Integration Tests

To run all integration tests, the Arduino emulator and hevserver processes first need to be running, and 
then run all integrations tests in the `NativeUI/tests/integration` dir:

```bash
. .hev_env/bin/activate
export PYTHONPATH=/home/pi/hev/NativeUI
./raspberry-dataserver/ArduinoEmulator.py -f raspberry-dataserver/share/B6-20201207.dump &
./raspberry-dataserver/hevserver.py --use-dump-data &
pytest NativeUI/tests/integration
```

### Coverage

To get pytest coverage run from the root of the repo:

```bash
pip install pytest-cov
pytest --cov=NativeUI NativeUI
```


## System Tests

### Template

Status is marked in the test title with:
* :x: for not started
* :large_orange_diamond: for WIP
* :white_check_mark: for completed

RiskID | Domain | Functional Area | Standard Reference | Assignee
------ | ------ | --------------- | ------------------ | --------
SW | Software-GUI | Alarms | ISO-XX | Tim Powell

#### Scenario: <EXAMPLE>

    GIVEN the <EVENT>
    WHEN the <CAUSE>
    THEN the <ACTION>

---

### Low Battery Alarm (10 minutes) :x:

RiskID | Domain | Functional Area | Standard Reference | Assignee
------ | ------ | --------------- | ------------------ | --------
SW8 | Software-GUI | Alarms | ISO80601-2-12:2020 | Tim Powell

#### Scenario: There is only 10 minutes of battery life left

    GIVEN the alarm payload comes in
    WHEN the alarm is about the battery
    THEN check if the low battery alarm signal is sent
    AND THEN the low battery alarm is displayed

---

### High Pressure Alarm to be HIGH Priority :large_orange_diamond:

RiskID | Domain | Functional Area | Standard Reference | Assignee
------ | ------ | --------------- | ------------------ | --------
SW11 | Software-GUI | Alarms | ISO80601-2-12:2020 | Tim Powell

#### Scenario: Excessive airway pressure applied

    GIVEN the alarm payload received
    WHEN the alarm_code: 7
    THEN the high priority alarm signal should be sent
    AND THEN alarm popup is triggered
    AND THEN alarm is added to alarm list
