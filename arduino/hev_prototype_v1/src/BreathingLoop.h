#ifndef BREATHING_LOOP_H
#define BREATHING_LOOP_H

// Main Breathing Controller.  Runs the FSM for breathing function
// @author Karol Hennessy <karol.hennessy@cern.ch>
// @author Antonio Fernandez Prieto <antonio.fernandez.prieto@cern.ch>
// @author Peter Svihra <peter.svihra@cern.ch>

#include <Arduino.h>
#include "ValvesController.h"
#include "common.h"

class BreathingLoop
{

public:
    BreathingLoop();
    ~BreathingLoop();
    uint8_t getLabCycleMode();
    uint8_t getFsmState();
    void FSM_assignment();
    void FSM_breathCycle();
    void doStart();
    void doStop();
    void doReset();
    bool getRunning();
    void updatePressures();
    ValvesController * getValvesController();

    states_timeouts &getTimeouts();

    // states
    enum BL_STATES : uint8_t {
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
    enum VENTILATION_MODES : uint8_t
    {
        LAB_MODE_BREATHE = 0,
        LAB_MODE_PURGE = 1,
        LAB_MODE_FLUSH = 2
    };

private:
    uint64_t _fsm_time ;
    uint32_t _fsm_timeout;
    uint8_t  _ventilation_mode;
    uint8_t  _bl_state;
    bool     _running;
    bool     _reset;
    uint8_t  _next_state;

    ValvesController _valves_controller;

    // calibration
    void calibrate();
    void initCalib();
    float getCalibrationOffset();    
    int _calib_N;
    uint32_t _calib_timeout;
    uint32_t _calib_time;
    int _calib_sum_pressure;
    float _calib_avg_pressure;

    // timeouts
    uint32_t calculateTimeoutExhale();
    states_timeouts _states_timeouts = {10000, 600, 600, 100, 600, 100, 100, 1000, 500, 600, 400};

    // values reading
    bool _reading;
    uint32_t _reading_time;
    uint32_t _reading_timeout;
};




#endif
