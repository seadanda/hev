#ifndef UI_LOOP_H
#define UI_LOOP_H

#include <Arduino.h>
#include "CommsFormat.h"
#include "BreathingLoop.h"
#include "common.h"

class UILoop
{

public:
    UILoop(BreathingLoop *bl);
    ~UILoop();
    int doCommand(cmd_format *cf);
private:
    void cmdGeneral(cmd_format *cf);
    void cmdSetTimeout(cmd_format *cf);
    void cmdSetMode(cmd_format *cf);
    void cmdSetThresholdMin(cmd_format *cf);
    void cmdSetThresholdMax(cmd_format *cf);

    BreathingLoop *_breathing_loop;
};

#endif
