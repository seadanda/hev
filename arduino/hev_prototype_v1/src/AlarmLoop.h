#ifndef ALARM_LOOP_H
#define ALARM_LOOP_H

#include <Arduino.h>
#include "common.h"
#include "CommsFormat.h"
#include "AudioVisualController.h"

class AlarmLoop {

public:
    AlarmLoop();
    ~AlarmLoop();

    void fireAlarms();
    void updateValues(readings<float> fast_data);

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
