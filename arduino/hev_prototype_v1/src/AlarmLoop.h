#ifndef ALARM_LOOP_H
#define ALARM_LOOP_H

#include <Arduino.h>
#include "common.h"
#include "CommsFormat.h"

class AlarmLoop
{

public:
    AlarmLoop();
    ~AlarmLoop();
    int doAlarm(alarm_format *af);

    alarm_thresholds& getThresholdsMin() { return _thresholds_min; }
    alarm_thresholds& getThresholdsMax() { return _thresholds_min; }
private:
    alarm_thresholds _thresholds_min;
    alarm_thresholds _thresholds_max;
    // BreathingLoop *_breathing_loop;
};

#endif
