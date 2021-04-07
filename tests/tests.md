# Tests Documentation

# Unit Tests

TODO
# Integration Tests
## Template

Status is marked in the test title with:
* :x: for not started
* :large_orange_diamond: for WIP
* :white_check_mark: for completed

RiskID | Domain | Functional Area | Standard Reference | Assignee
------ | ------ | --------------- | ------------------ | --------
SW | Software-GUI | Alarms | ISO-XX | Tim Powell

### Scenario: <EXAMPLE>

    GIVEN the <EVENT>
    WHEN the <CAUSE>
    THEN the <ACTION>

---

## Low Battery Alarm (10 minutes) :x:

RiskID | Domain | Functional Area | Standard Reference | Assignee
------ | ------ | --------------- | ------------------ | --------
SW8 | Software-GUI | Alarms | ISO80601-2-12:2020 | Tim Powell

### Scenario: There is only 10 minutes of battery life left

    GIVEN the alarm payload comes in
    WHEN the alarm is about the battery
    THEN check if the low battery alarm signal is sent
    AND THEN the low battery alarm is displayed

---

## High Pressure Alarm to be HIGH Priority :large_orange_diamond:

RiskID | Domain | Functional Area | Standard Reference | Assignee
------ | ------ | --------------- | ------------------ | --------
SW11 | Software-GUI | Alarms | ISO80601-2-12:2020 | Tim Powell

### Scenario: Excessive airway pressure applied

    GIVEN the alarm payload received
    WHEN the alarm_code: 7
    THEN the high priority alarm signal should be sent
    AND THEN alarm popup is triggered
    AND THEN alarm is added to alarm list
