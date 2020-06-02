#include "AlarmLoop.h"

AlarmLoop::AlarmLoop()
{
    // make sure starting value is between thresholds
    for (uint8_t alarm_num = 0; alarm_num < ALARM_CODES::ALARMS_COUNT; alarm_num++) {
        _alarms.values[alarm_num] = (_alarms.thresholds_max[alarm_num] + _alarms.thresholds_min[alarm_num]) / 2;
    }

    setBatteryThresholds();
}

AlarmLoop::~AlarmLoop()
{;}

ALARM_TYPE AlarmLoop::checkThresholds() {
    _type = ALARM_TYPE::ALARM_TYPE_UNKNOWN;
    bool active = false;
    for (uint8_t alarm_num = 0; alarm_num < ALARM_CODES::ALARMS_COUNT; alarm_num++) {
        active |= _alarms.actives[alarm_num] = ( _alarms.values[alarm_num] < _alarms.thresholds_min[alarm_num]
                                              || _alarms.values[alarm_num] > _alarms.thresholds_max[alarm_num]);
        if (_alarms.actives[alarm_num] && _alarms.priorities[alarm_num] > _type) {
            _type = _alarms.priorities[alarm_num];
        }
    }

    return _type;
}

void AlarmLoop::fireAlarms() {
    switch (checkThresholds()) {
        case ALARM_TYPE::PRIORITY_LOW:
            _av_controller.setAVs(AV_STYLE::PERM_OFF, AV_STYLE::PERM_ON , AV_STYLE::PERM_OFF, AV_STYLE::OSCIL   );
            break;
        case ALARM_TYPE::PRIORITY_MEDIUM:
            _av_controller.setAVs(AV_STYLE::PERM_OFF, AV_STYLE::OSCIL   , AV_STYLE::PERM_OFF, AV_STYLE::OSCIL   );
            break;
        case ALARM_TYPE::PRIORITY_HIGH:
            _av_controller.setAVs(AV_STYLE::PERM_OFF, AV_STYLE::PERM_OFF, AV_STYLE::OSCIL   , AV_STYLE::OSCIL   );
            break;
        default:
            _av_controller.setAVs(AV_STYLE::PERM_ON , AV_STYLE::PERM_OFF, AV_STYLE::PERM_OFF, AV_STYLE::PERM_OFF);
            break;
    }

    _av_controller.update();
}

void AlarmLoop::updateValues(readings<float> fast_data) {
    _alarms.values[ALARM_CODES::CHECK_P_PATIENT] = static_cast<float>(fast_data.pressure_patient);
}

void AlarmLoop::setBatteryThresholds()
{

    // these are booleans
    // 0 = no alarm
    // 1 = alarm
    // => limits are -1 to 0.5

    setAlarm<float>(ALARM_CODES::AC_POWER_DISCONNECTION, _alarms.thresholds_min, -1.0);
    setAlarm<float>(ALARM_CODES::BATTERY_CHARGE,         _alarms.thresholds_min, -1.0);
    setAlarm<float>(ALARM_CODES::BATTERY_FAULT_SRVC,     _alarms.thresholds_min, -1.0);
    setAlarm<float>(ALARM_CODES::LOW_BATTERY,            _alarms.thresholds_min, -1.0);

    setAlarm<float>(ALARM_CODES::AC_POWER_DISCONNECTION, _alarms.thresholds_max, 0.5);
    setAlarm<float>(ALARM_CODES::BATTERY_CHARGE,         _alarms.thresholds_max, 0.5);
    setAlarm<float>(ALARM_CODES::BATTERY_FAULT_SRVC,     _alarms.thresholds_max, 0.5);
    setAlarm<float>(ALARM_CODES::LOW_BATTERY,            _alarms.thresholds_max, 0.5);
}