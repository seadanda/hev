#ifndef BREATHING_LOOP_H
#define BREATHING_LOOP_H

// Main Breathing Controller.  Runs the FSM for breathing function
// @author Karol Hennessy <karol.hennessy@cern.ch>
// @author Antonio Fernandez Prieto <antonio.fernandez.prieto@cern.ch>

#include <Arduino.h>
// #include "CommsCommon.h"
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
    void FSM_breath_cycle();
    void doStart();
    void doStop();
    void doReset();
    bool getRunning();
    void updateReadings();
    readings getReadingAverages();
    ValvesController * getValvesController();

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
    uint32_t _timeout;
    uint8_t  _ventilation_mode;
    uint8_t  _bs_state;
    bool     _running;
    bool     _reset;
    int      _next_state;

    ValvesController _valves_controller;

    // calibration
    void calibrate();
    void initCalib();
    float getCalibrationOffset();
    int _calib_N;
    int _calib_timeout;
    int _calib_sum_pressure;
    int _calib_time;
    float _calib_avg_pressure;

    // readings
    void resetReadingSums();
    readings _readings_sums;
    readings _readings_avgs;
    uint16_t _readings_N;
    int _readings_time;
    int _readings_timeout;
    int _readings_avgs_time;
    int _readings_avgs_timeout;
};




#endif
