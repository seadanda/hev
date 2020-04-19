#ifndef BREATHING_LOOP_H
#define BREATHING_LOOP_H

// Main Breathing Controller.  Runs the FSM for breathing function
// @author Karol Hennessy <karol.hennessy@cern.ch>
// @author Antonio Fernandez Prieto <antonio.fernandez.prieto@cern.ch>
// @author Peter Svihra <peter.svihra@cern.ch>

#include <Arduino.h>
#include "common.h"
#include "ValvesController.h"

class BreathingLoop
{

public:
    BreathingLoop();
    ~BreathingLoop();
    uint8_t getVentilationMode();
    uint8_t getFsmState();
    void FSM_assignment();
    void FSM_breathCycle();
    void doStart();
    void doStop();
    void doReset();
    bool getRunning();
    void updateReadings();
    readings<uint16_t> getReadingAverages();
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
    uint32_t            _fsm_time ;
    uint32_t            _fsm_timeout;
    VENTILATION_MODES   _ventilation_mode;
    BL_STATES           _bl_state;
    bool                _running;
    bool                _reset;

    ValvesController _valves_controller;

    // calibration
    void calibrate();
    void initCalib();
    float getCalibrationOffset();
    uint32_t _calib_N;
    uint32_t _calib_time;
    uint32_t _calib_timeout;
    uint32_t _calib_sum_pressure; // 32 bit due to possible analog read overflow
    float _calib_avg_pressure;

    // timeouts
    uint32_t calculateTimeoutExhale();
    states_timeouts _states_timeouts = {10000, 600, 600, 100, 600, 100, 100, 1000, 500, 600, 400};

    // readings
    void resetReadingSums();
    readings<uint32_t> _readings_sums; // 32 bit due to possible analog read overflow
    readings<uint16_t> _readings_avgs;
    bool     _readings_reset;
    uint32_t _readings_N;
    uint32_t _readings_time;
    uint32_t _readings_timeout;
    uint32_t _readings_avgs_time;
    uint32_t _readings_avgs_timeout;
};




#endif
