#ifndef ALARM_LOOP_H
#define ALARM_LOOP_H

#include <Arduino.h>
#include "common.h"
#include "CommsFormat.h"
#include "AudioVisualController.h"

// general function to set alarm of any defined kind
template <typename T>
void setAlarm(ALARM_CODES alarm_code, T *alarms, T value) {
    alarms[alarm_code] = value;
}

class AlarmLoop {

public:
    AlarmLoop();
    ~AlarmLoop();

    void fireAlarms();
    void updateValues(readings<int16_t> fast_data);

    float *getValues       () { return _alarms.values        ; }
    float *getThresholdsMin() { return _alarms.thresholds_min; }
    float *getThresholdsMax() { return _alarms.thresholds_max; }

    uint32_t *getLastBroadcasts() { return _alarms.last_broadcasts; }

    ALARM_TYPE  getHighestType() { return _type; }
    ALARM_TYPE *getTypes()       { return _alarms.priorities; }
    bool       *getActives()     { return _alarms.actives; }

private:
    ALARM_TYPE checkTresholds();

private:
    AudioVisualController _av_controller;

    ALARM_TYPE _type = ALARM_TYPE::ALARM_TYPE_UNKNOWN;
    alarms _alarms;
};

#endif
