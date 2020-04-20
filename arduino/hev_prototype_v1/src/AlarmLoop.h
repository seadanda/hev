#ifndef ALARM_LOOP_H
#define ALARM_LOOP_H

#include <Arduino.h>
#include "CommsFormat.h"

class AlarmLoop
{

public:
    AlarmLoop();
    ~AlarmLoop();
    int doAlarm(alarm_format *af);
private:
    // BreathingLoop *_breathing_loop;
};

#endif