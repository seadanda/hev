#ifndef ALARM_LOOP_H
#define ALARM_LOOP_H

#include <Arduino.h>
#include "commsFormat.h"

class AlarmLoop
{

public:
    AlarmLoop();
    ~AlarmLoop();
    int doAlarm(alarmFormat *af);
private:
    // BreathingLoop *_breathing_loop;
};

#endif