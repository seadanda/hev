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
    uint8_t getFsmState();
    void FSM_assignment();
    void FSM_breathCycle();
    void doStart();
    void doStop();
    void doReset();
    void doStandby();
    bool getRunning();
    void updateReadings();
    void updateRawReadings();
    void updateCycleReadings();
    readings<float> getReadingAverages();
    readings<float> getRawReadings();
    float getRespiratoryRate();
    float getTargetRespiratoryRate();
    float getIERatio();
    void setIERatio();
    void updateFromTargets();
    void updateIE();
    float getPEEP();
    float getMinuteVolume();
    ValvesController * getValvesController();
    uint8_t getValveInhalePercent();
    uint8_t getValveExhalePercent();
    uint8_t valveAirInEnabled();
    uint8_t valveO2InEnabled();
    uint8_t valvePurgeEnabled();
    uint8_t inhaleTriggerEnabled();
    uint8_t exhaleTriggerEnabled();
    void    setVentilationMode(VENTILATION_MODE mode);
    VENTILATION_MODE getVentilationMode();

    float getFlow();
    float getVolume(); 
    float getAirwayPressure();
    pid_variables& getPIDVariables();
    target_variables &getTargetVariablesPC_AC();
    target_variables &getTargetVariablesPC_AC_PRVC();
    target_variables &getTargetVariablesPC_PSV();
    target_variables &getTargetVariablesCPAP();
    target_variables &getTargetVariablesTest();
    target_variables &getTargetVariablesCurrent();
    states_durations &getDurations();
    cycle_readings &getCycleReadings();

 

    // states
    enum BL_STATES : uint8_t {
            UNKNOWN         =  0,
            IDLE            =  1,
            CALIBRATION     =  2,
            BUFF_PREFILL    =  3,
            BUFF_FILL       =  4,
            BUFF_LOADED     =  5,
            BUFF_PRE_INHALE =  6,
            INHALE          =  7,
            PAUSE           =  8,
            EXHALE_FILL     =  9,
            EXHALE          = 10,
            STOP            = 11,
            BUFF_PURGE      = 12,
            BUFF_FLUSH      = 13,
            STANDBY         = 14
    };




private:
    pid_variables _pid; // Public variable to be able to change it via getPIDVariables
    uint32_t            _fsm_time ;
    uint32_t            _fsm_timeout;
    VENTILATION_MODE        _ventilation_mode;
    BL_STATES           _bl_state, _bl_laststate;

    uint32_t            _lasttime;
    bool                _running;
    bool                _reset;
    bool                _standby;

    ValvesController _valves_controller;

    // calibration
    void calibrate();
    void initCalib();
    uint32_t _calib_N;
    uint32_t _calib_time;
    uint32_t _calib_timeout;
    bool _calibrated;
    readings<float> _calib_sums;
    readings<float> _calib_avgs;

    // timeouts
    uint32_t calculateDurationExhale();
    //durations = 			 {calibration,	buff_purge, 	buff_flush,	buff_prefill, buff_fill, buff_loaded, buff_pre_inhale, inhale, pause, exhale_fill, exhale }
    states_durations _states_durations = {10000, 	600, 		600, 		100, 600, 0, 0, 1200, 10, 1600, 200};
    states_durations _measured_durations = {0,0,0,0,0,0,0,0,0,0,0};
    void measure_durations();
    // targets
    void initTargets();
    target_variables _targets_pcac; 
    target_variables _targets_pc_psv; 
    target_variables _targets_pcac_prvc; 
    target_variables _targets_cpap; 
    target_variables _targets_test; 
    target_variables* _targets_current; //note pointer
    // readings
    void resetReadingSums();
    readings<float> _readings_sums; // 32 bit due to possible analog read overflow
    readings<float> _readings_avgs;
    readings<float> _readings_raw;
    bool     _readings_reset;
    uint32_t _readings_N;
    uint32_t _readings_time;
    uint32_t _readings_timeout;
    uint32_t _readings_avgs_time;
    uint32_t _readings_avgs_timeout;
    uint32_t _readings_cycle_time;
    uint32_t _readings_cycle_timeout;
    uint32_t _tsig_time;
    uint32_t _tsig_timeout;
    void tsigReset();

 
    float _peep;

    // calculations
    cycle_readings _cycle_readings;
    bool _cycle_done;
    void updateTotalCycleDuration(uint16_t newtotal);
    uint16_t _total_cycle_duration[CYCLE_AVG_READINGS];
    uint16_t _inhale_cycle_duration[CYCLE_AVG_READINGS];
    uint16_t _exhale_cycle_duration[CYCLE_AVG_READINGS];


    float _flow;
    float _volume;
    float _airway_pressure;
    float _valve_inhale_PID_percentage;//from 0 to 1.
    float _volume_inhale;
    float _volume_exhale;
    float _volume_total;
    float _sum_airway_pressure;
    bool _mandatory_inhale;
    bool _mandatory_exhale;
    uint32_t _ap_readings_N;

    void doPID();

    // safety
    void safetyCheck();
    uint8_t _safe; 

    // PID vars

    //float _pid_integral;  // moved to pid_variable struct
    // triggers
    void runningAvgs();
    void inhaleTrigger();
    void exhaleTrigger();
    bool _apnea_event;
    float _running_flows[RUNNING_AVG_READINGS];
    float _running_avg_flow;
    uint8_t _running_index;
    uint8_t _cycle_index;
    // float _running_minute_volume[CYCLE_AVG_READINGS];
    float _running_inhale_minute_volume[CYCLE_AVG_READINGS];
    float _running_exhale_minute_volume[CYCLE_AVG_READINGS];
    float _running_minute_volume[CYCLE_AVG_READINGS];

    bool  _inhale_triggered;
    float _inhale_trigger_threshold;
    float _exhale_trigger_threshold;
    float _peak_flow;
    float _valley_flow;
    uint32_t _peak_flow_time;
    uint32_t _valley_flow_time;

    uint32_t _min_inhale_time;
    uint32_t _min_exhale_time;
    uint32_t _max_exhale_time;

};




#endif
