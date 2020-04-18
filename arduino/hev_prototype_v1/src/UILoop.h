#ifndef UI_LOOP_H
#define UI_LOOP_H

#include <Arduino.h>
#include "commsFormat.h"
#include "BreathingLoop.h"

class UILoop
{

public:
    UILoop(BreathingLoop *bl);
    ~UILoop();
    int doCommand(cmdFormat *cf);
private:
    BreathingLoop *_breathing_loop;
};

#endif