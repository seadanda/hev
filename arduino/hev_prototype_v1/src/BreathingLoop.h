// © Copyright CERN, Riga Technical University and University of Liverpool 2020.
// All rights not expressly granted are reserved. 
// 
// This file is part of hev-sw.
// 
// hev-sw is free software: you can redistribute it and/or modify it under
// the terms of the GNU General Public Licence as published by the Free
// Software Foundation, either version 3 of the Licence, or (at your option)
// any later version.
// 
// hev-sw is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public Licence
// for more details.
// 
// You should have received a copy of the GNU General Public License along
// with hev-sw. If not, see <http://www.gnu.org/licenses/>.
// 
// The authors would like to acknowledge the much appreciated support
// of all those involved with the High Energy Ventilator project
// (https://hev.web.cern.ch/).


#ifndef BREATHING_LOOP_H
#define BREATHING_LOOP_H

// Main Breathing Controller.  Runs the FSM for breathing function
// @author Karol Hennessy <karol.hennessy@cern.ch>
// @author Antonio Fernandez Prieto <antonio.fernandez.prieto@cern.ch>
// @author Peter Svihra <peter.svihra@cern.ch>

#include <Arduino.h>
#include "common.h"
#include "ValvesController.h"
#include "LinearFitter.h"

#include "RingBuf.h"

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
    void updateCalculations();
    readings<float> getReadingAverages();
    readings<float> getRawReadings();
    calculations<float> getCalculations();
    // float getRespiratoryRate();
    float getTargetRespiratoryRate();
    float getIERatio();
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

    float calculateFlow(const uint32_t &current_time, const float &pressure_patient, const float &pressure_buffer, float volume_tube = 1600, float volume_buffer = 10000);
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
            PRE_CALIBRATION =  2,
            CALIBRATION     =  3,
            BUFF_PREFILL    =  4,
            BUFF_FILL       =  5,
            BUFF_PRE_INHALE =  6,
            INHALE          =  7,
            PAUSE           =  8,
            EXHALE          =  9,
            STOP            = 10,
            BUFF_PURGE      = 11,
            BUFF_FLUSH      = 12,
            STANDBY         = 13
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
    //durations = 			 {pre_calibration, calibration,	buff_purge, 	buff_flush,	buff_prefill, buff_fill, buff_pre_inhale, inhale, pause, exhale}
    states_durations _states_durations = {6000, 8000,	600, 		600, 		100, 600, 0, 1200, 10, 1800 };
    states_durations _measured_durations = {0,0,0,0,0,0,0,0,0};
    void measureDurations();
    void measurePEEP();

    void doO2ValveFrac(float desired_fiO2, float pressure_change);
    bool doExhalePurge();
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
    calculations<float> _calculations;
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
    uint32_t _calculations_time;
    uint32_t _calculations_timeout;
    void tsigReset();

 
    float _peep;

    // calculations
    cycle_readings _cycle_readings;
    bool _cycle_done;
    // void updateTotalCycleDuration(uint16_t newtotal);
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

    LinearFitter _flow_fitter = LinearFitter(300, 100);
    LinearFitter _pressure_buffer_fitter  = LinearFitter(100,0);
    LinearFitter _pressure_patient_fitter = LinearFitter(100,0);
    // triggers
    void runningAvgs();
    bool inhaleTrigger();
    bool exhaleTrigger();
    bool volumeTrigger();
    bool _apnea_event;
    float _running_flows[RUNNING_AVG_READINGS];
    float _running_avg_flow;
    uint8_t _running_index;
    uint8_t _cycle_index;
    // float _running_minute_volume[CYCLE_AVG_READINGS];
    float _running_inhale_minute_volume[CYCLE_AVG_READINGS];
    float _running_exhale_minute_volume[CYCLE_AVG_READINGS];
    float _running_minute_volume[CYCLE_AVG_READINGS];

    float _running_peep[RUNNING_AVG_READINGS];
    float _running_avg_peep;
    uint8_t _running_index_peep;

    bool  _inhale_triggered;
    float _peak_flow;
    float _valley_flow;
    uint32_t _peak_flow_time;
    uint32_t _valley_flow_time;

    uint32_t _min_inhale_time;
    uint32_t _min_exhale_time;
    uint32_t _max_exhale_time;

    float _o2_valve_frac;
    float _expected_fiO2;
    float _new_expected_fiO2;

};




#endif
