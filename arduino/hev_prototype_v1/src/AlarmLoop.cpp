#include "AlarmLoop.h"

AlarmLoop::AlarmLoop()
{
    // make sure starting value is between thresholds
    for (uint8_t alarm_num = 0; alarm_num < ALARM_CODES::ALARMS_COUNT; alarm_num++) {
        _alarms.values[alarm_num] = (_alarms.thresholds_max[alarm_num] + _alarms.thresholds_min[alarm_num]) / 2;
    }
}

AlarmLoop::~AlarmLoop()
{;}

ALARM_TYPE AlarmLoop::checkTresholds() {
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
    switch (checkTresholds()) {
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
