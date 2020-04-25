#ifndef UI_LOOP_H
#define UI_LOOP_H

#include <Arduino.h>
#include "CommsFormat.h"
#include "BreathingLoop.h"
#include "AlarmLoop.h"
#include "common.h"

class UILoop
{

public:
    UILoop(BreathingLoop *bl, AlarmLoop *al);
    ~UILoop();
    int doCommand(cmd_format *cf);
private:
    void cmdGeneral(cmd_format *cf);
    void cmdSetDuration(cmd_format *cf);
    void cmdSetMode(cmd_format *cf);
    void cmdSetThresholdMin(cmd_format *cf);
    void cmdSetThresholdMax(cmd_format *cf);

    BreathingLoop *_breathing_loop;
    AlarmLoop     *_alarm_loop    ;
};

#endif
