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