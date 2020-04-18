#ifndef BREATHING_LOOP_H
#define BREATHING_LOOP_H

// Main Breathing Controller.  Runs the FSM for breathing function
// @author Karol Hennessy <karol.hennessy@cern.ch>
// @author Antonio Fernandez Prieto <antonio.fernandez.prieto@cern.ch>

#include <Arduino.h>

class BreathingLoop
{

public:
    BreathingLoop();
    ~BreathingLoop();
    byte getLabCycleMode();
    byte getFsmState();
    void FSM_assignment();
    void FSM_breath_cycle();
    void doStart();
    void doStop();
    void doReset();
    bool getRunning();
    void updatePressures();

    // states
    enum BL_STATES : byte
    {
        IDLE,
        CALIBRATION,
        BUFF_PREFILL,
        BUFF_FILL,
        BUFF_LOADED,
        BUFF_PRE_INHALE,
        INHALE,
        PAUSE,
        EXHALE_FILL,
        EXHALE,
        STOP,
        BUFF_PURGE,
        BUFF_FLUSH
    };

//TODO: this should probably be common
    enum VENTILATION_MODES : byte
    {
        LAB_MODE_BREATHE = 0,
        LAB_MODE_PURGE = 1,
        LAB_MODE_FLUSH = 2
    };

private:
    uint64_t _fsm_time ;
    int      _timeout;
    byte     _ventilation_mode;
    byte     _bs_state;
    bool     _running;
    bool     _reset;
    int      _next_state;
};




#endif