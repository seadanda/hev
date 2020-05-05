#include "AlarmLoop.h"

AlarmLoop::AlarmLoop()
{
    // make sure starting value is between thresholds
    for (uint8_t alarm_num = 0; alarm_num < ALARM_CODES::ALARMS_COUNT; alarm_num++) {
        _alarms.values[alarm_num] = static_cast<uint32_t>((_alarms.thresholds_max[alarm_num] + _alarms.thresholds_min[alarm_num]) / 2);
    }
}

AlarmLoop::~AlarmLoop()
{;}

bool AlarmLoop::fireAlarm(alarm_format &result, int &alarm_num, uint32_t &tnow)
{
    if (_alarms.actives[alarm_num]) {

    }

    return false;
}

bool AlarmLoop::checkTresholds() {
    _triggered = false;
    for (uint8_t alarm_num = 0; alarm_num < ALARM_CODES::ALARMS_COUNT; alarm_num++) {
        _triggered |= _alarms.actives[alarm_num] = ( _alarms.values[alarm_num] < _alarms.thresholds_min[alarm_num]
                                                  || _alarms.values[alarm_num] > _alarms.thresholds_max[alarm_num]);
    }

    return _triggered;
}

void AlarmLoop::processAlarms() {
    if (checkTresholds()) {
        _av_controller.setStylesHigher(AV_STYLE::OSCIL);
//        _av_controller.setAVsHigher(AV_STYLE::OSCIL);
    } else {
        _av_controller.setStyles();
    }

    _av_controller.update();
}
