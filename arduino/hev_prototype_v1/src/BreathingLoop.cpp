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


#include "BreathingLoop.h"
#include "common.h"
/*
The Idea of this code is to unfold the FSM in two: one to assign the transitions and the second one to program the states.
*/

BreathingLoop::BreathingLoop()
{
    uint32_t tnow = static_cast<uint32_t>(millis());
    _calib_time = tnow;
    _fsm_time = tnow;
    _fsm_timeout = 1000;
    _tsig_time = tnow;
    _tsig_timeout = 100;
    _calculations_time = tnow;
    _calculations_timeout = 10;

    _ventilation_mode = VENTILATION_MODE::PC_AC;
    _bl_state = BL_STATES::IDLE;
    _bl_laststate = BL_STATES::IDLE;
    
    _fill_state = FILL_STATES::VALVES_CLOSED;
    _fill_laststate = FILL_STATES::VALVES_CLOSED;

    _running = false;
    _reset = false;
    _standby = false;
    _safe  = true;

    _peep = 5.0;

    initCalib();
    resetReadingSums();

    _flow = 0;
    _volume = 0;
    _airway_pressure = 0;
    _mandatory_inhale = false;
    _mandatory_exhale = false;

    _pid.Kp = 0.001; // proportional factor
    _pid.Ki = 0.0005;   // integral factor
    _pid.Kd = 0.001;   // derivative factor
    _pid.pid_gain = 2;
    _pid.max_patient_pressure = 45; 

    _pid.integral   = 0.;
    _pid.derivative = 0.;

    _pid.process_pressure = 0.;// Variable used to build the target pressure profile
    _pid.target_pressure = 0.;// Variable used to build the target pressure profile
    _pid.target_final_pressure = 10.; // Final pressure after the inhale pressure ramp up
    _pid.nsteps = 3; // Final pressure after the inhale pressure ramp up

    for(int i=0; i<RUNNING_AVG_READINGS; i++){
        _running_flows[i] = 0.0;
        _running_peep[i] = 0.0;
    }

    _total_cycle_duration[0] = 
                       _states_durations.buff_pre_inhale
                       +_states_durations.inhale
                       +_states_durations.pause
                       +_states_durations.exhale;
    _inhale_cycle_duration[0] = _states_durations.buff_pre_inhale
                       +_states_durations.inhale
                       +_states_durations.pause;
    _exhale_cycle_duration[0] = _states_durations.exhale;

    for (int i = 1; i < CYCLE_AVG_READINGS; i++)
    {
        _total_cycle_duration[i] = _total_cycle_duration[0];
        _inhale_cycle_duration[i] = _inhale_cycle_duration[0];
        _exhale_cycle_duration[i] = _exhale_cycle_duration[0];
    }

    _sum_airway_pressure = 0;
    _ap_readings_N = 0;

    _running_index = 0;
    _running_index_peep = 0;

    _cycle_index = 0;

    _min_inhale_time = 150;
    _min_exhale_time = 800;
    _max_exhale_time = 10000;  // for mandatory cycle - changed to 30s for the sponteneous breath testing


    initTargets();
    setVentilationMode(_ventilation_mode);

    _o2_valve_frac = 0;
    _expected_fiO2 = 0.21;
    _new_expected_fiO2 = 0.21;
    _o2_frac_pressure = 0.;
    _fiO2_est = 0.21;
    _time_valve_closure = millis();
}

void BreathingLoop::initTargets()
{

    _targets_pcac.respiratory_rate = 15.0;
    _targets_pcac.ie_ratio = 0.5;
    _targets_pcac.ie_selected = false;
    _targets_pcac.inspiratory_pressure = 17;
    _targets_pcac.volume = 400;
    _targets_pcac.inhale_time= 1000;
    _targets_pcac.peep = 5;
    _targets_pcac.fiO2_percent = 21;

    _targets_pcac.inhale_trigger_threshold     = 5;   // abs flow ? unit / 
    _targets_pcac.exhale_trigger_threshold     = 0.25;  // 25% of the peak flow

    _targets_pcac.buffer_lower_pressure = 285.0;
    _targets_pcac.buffer_upper_pressure = 300.0;
    // _targets_pcac.pid_gain = 1;  // not yet doing anything

    // copy all from PCAC
    _targets_pcac_prvc = _targets_pcac;
    _targets_pc_psv = _targets_pcac;
    _targets_cpap = _targets_pcac;
    _targets_test = _targets_pcac;

    _targets_pcac.inhale_trigger_enable = true; 
    _targets_pcac.exhale_trigger_enable = false; 
    _targets_pcac.volume_trigger_enable = false; 
    _targets_pcac_prvc.inhale_trigger_enable = true; 
    _targets_pcac_prvc.exhale_trigger_enable = false; 
    _targets_pcac_prvc.volume_trigger_enable = true; 
    _targets_pc_psv.inhale_trigger_enable = true; 
    _targets_pc_psv.exhale_trigger_enable = true; 
    _targets_pc_psv.volume_trigger_enable = false; 
    _targets_cpap.inhale_trigger_enable = true; 
    _targets_cpap.exhale_trigger_enable = true; 
    _targets_cpap.volume_trigger_enable = false; 
    _targets_test.inhale_trigger_enable = true; 
    _targets_test.exhale_trigger_enable = true; 
    _targets_test.volume_trigger_enable = false; 
    // "current" mode is set by ventilation mode

    // set modes for readback
    _targets_pcac.mode = VENTILATION_MODE::PC_AC;
    _targets_pcac_prvc.mode = VENTILATION_MODE::PC_AC_PRVC;
    _targets_pc_psv.mode = VENTILATION_MODE::PC_PSV;
    _targets_cpap.mode = VENTILATION_MODE::CPAP;
    _targets_test.mode = VENTILATION_MODE::TEST;

}

BreathingLoop::~BreathingLoop()
{
;
}

uint8_t BreathingLoop::getBreatheFSMState()
{
    return static_cast<uint8_t>(_bl_state);
}

uint8_t BreathingLoop::getFillFSMState()
{
    return static_cast<uint8_t>(_fill_state);
}


void BreathingLoop::updateReadings()
{
    // calc pressure every 1ms
    // create averages every 10ms
    uint32_t tnow = static_cast<uint32_t>(millis());
    if (tnow - _readings_time >= _readings_timeout) {
        _readings_time = tnow;
        _readings_N++;

        _readings_sums.timestamp                = tnow;
#ifdef CHIP_ESP32
        _readings_sums.pressure_air_supply      += static_cast<float>(analogRead(pin_pressure_air_supply)    );
        _readings_sums.pressure_o2_supply       += static_cast<float>(analogRead(pin_pressure_o2_supply)     );
#endif
        _readings_sums.pressure_air_regulated   += static_cast<float>(analogRead(pin_pressure_air_regulated) );
        _readings_sums.pressure_buffer          += static_cast<float>(analogRead(pin_pressure_buffer)        );
        _readings_sums.pressure_inhale          += static_cast<float>(analogRead(pin_pressure_inhale)        );
        _readings_sums.pressure_patient         += static_cast<float>(analogRead(pin_pressure_patient)       );
        _readings_sums.temperature_buffer       += static_cast<float>(analogRead(pin_temperature_buffer)     );
        _readings_sums.pressure_o2_regulated    += static_cast<float>(analogRead(pin_pressure_o2_regulated)  );
        _readings_sums.pressure_diff_patient    += static_cast<float>(analogRead(pin_pressure_diff_patient)  );
        _readings_sums.o2_percent               += static_cast<float>(analogRead(pin_o2_sensor)              );
 

    }

    // to make sure the readings correspond only to the same fsm mode
    if (_readings_reset) {
        resetReadingSums();
    } else if (tnow - _readings_avgs_time >= _readings_avgs_timeout) {
        _readings_avgs.timestamp                = static_cast<uint32_t>(_readings_sums.timestamp);
        _readings_avgs.pressure_air_supply      = adcToMillibarFloat((_readings_sums.pressure_air_supply      / _readings_N));
        _readings_avgs.pressure_air_regulated   = adcToMillibarFloat((_readings_sums.pressure_air_regulated   / _readings_N));
        _readings_avgs.pressure_buffer          = adcToMillibarFloat((_readings_sums.pressure_buffer          / _readings_N), _calib_avgs.pressure_buffer       );
        _readings_avgs.pressure_inhale          = adcToMillibarFloat((_readings_sums.pressure_inhale          / _readings_N), _calib_avgs.pressure_inhale       );
        _readings_avgs.pressure_patient         = adcToMillibarFloat((_readings_sums.pressure_patient         / _readings_N), _calib_avgs.pressure_patient      );
        _readings_avgs.temperature_buffer       = adcToMillibarFloat((_readings_sums.temperature_buffer       / _readings_N), _calib_avgs.temperature_buffer    );
#ifdef HEV_FULL_SYSTEM                                         
        _readings_avgs.pressure_o2_supply       = adcToMillibarFloat((_readings_sums.pressure_o2_supply       / _readings_N));
        _readings_avgs.pressure_o2_regulated    = adcToMillibarFloat((_readings_sums.pressure_o2_regulated    / _readings_N));
        _readings_avgs.pressure_diff_patient    = adcToMillibarDPFloat((_readings_sums.pressure_diff_patient  / _readings_N),_calib_avgs.pressure_diff_patient) ;
        _readings_avgs.o2_percent               = adcToO2PercentFloat((_readings_sums.o2_percent              / _readings_N));
        //_readings_avgs.o2_percent               =  adcToO2PercentFloat(static_cast<float>(analogRead(pin_o2_sensor)));
#endif

	_pid.process_pressure = _readings_avgs.pressure_inhale; // Update the process pressure independent of the system state


        // add Oscar code here:
        if (getBreatheFSMState() == BL_STATES::INHALE){
                //TODO

                doPID();

                _valves_controller.setPIDoutput(_pid.valve_duty_cycle);
                _valves_controller.setBreatheValves(VALVE_STATE::PID, VALVE_STATE::FULLY_CLOSED);
        }
        runningAvgs();

        //_flow = _readings_avgs.pressure_diff_patient;

        _pid.previous_process_pressure = adcToMillibarFloat((_readings_sums.pressure_inhale / _readings_N), _calib_avgs.pressure_inhale);

        resetReadingSums();
        updateFromTargets();
        // logging to cross check fio2 with TestChest
        // logMsg(String(_targets_current->fiO2_percent)+","+String( _readings_avgs.o2_percent)+","+String(_fiO2_est * 100.f));
    }
}

void BreathingLoop::updateRawReadings()
{
    // calc pressure every 1ms
    // create averages every 10ms
    uint32_t tnow = static_cast<uint32_t>(millis());

    // to make sure the readings correspond only to the same fsm mode
    if (tnow - _readings_avgs_time >= _readings_avgs_timeout) {
        _readings_raw.timestamp                = static_cast<uint32_t>(_readings_sums.timestamp);
#ifdef CHIP_ESP32
        _readings_raw.pressure_air_supply      =analogRead(pin_pressure_air_supply)    ;
        _readings_raw.pressure_o2_supply       =analogRead(pin_pressure_o2_supply)     ;
#endif
        _readings_raw.pressure_air_regulated   =analogRead(pin_pressure_air_regulated) ;
        _readings_raw.pressure_buffer          =analogRead(pin_pressure_buffer)        ;
        _readings_raw.pressure_inhale          =analogRead(pin_pressure_inhale)        ;
        _readings_raw.pressure_patient         =analogRead(pin_pressure_patient)       ;
        _readings_raw.temperature_buffer       =analogRead(pin_temperature_buffer)     ;
        _readings_raw.pressure_o2_regulated    =analogRead(pin_pressure_o2_regulated)  ;
        _readings_raw.pressure_diff_patient    =analogRead(pin_pressure_diff_patient)  ;
        _readings_raw.o2_percent               =analogRead(pin_o2_sensor            )  ;
    }

}

void BreathingLoop::updateCycleReadings()
{

    if (_bl_state == BL_STATES::BUFF_PRE_INHALE){
        if(_cycle_done == false){
            uint32_t tnow = static_cast<uint32_t>(millis());
            ledcWrite(pwm_chan_debug, uint8_t(_fiO2_est*122));

            _cycle_index = (_cycle_index == CYCLE_AVG_READINGS-1 ) ? 0 : _cycle_index+1;

            _cycle_readings.timestamp = tnow;
            _cycle_readings.fiO2_percent =_readings_avgs.o2_percent;// 
            _running_inhale_minute_volume[_cycle_index] = _volume_inhale ;
            _running_exhale_minute_volume[_cycle_index] = _volume_exhale ;
            _total_cycle_duration[_cycle_index] = (
                       _measured_durations.buff_pre_inhale
                       +_measured_durations.inhale
                       +_measured_durations.pause
                       +_measured_durations.exhale );

            float mv_sum = 0, mvi_sum = 0, mve_sum = 0;
            uint16_t tot_sum = 0;
            // uint16_t inh_sum, exh_sum  = 0;
            for(int i=0 ; i<CYCLE_AVG_READINGS; i++){
                mv_sum += _running_inhale_minute_volume[i] + _running_exhale_minute_volume[i];
                mvi_sum += _running_inhale_minute_volume[i];
                mve_sum += _running_exhale_minute_volume[i];
                tot_sum += _total_cycle_duration[i];
                // inh_sum += _inhale_cycle_duration[i];
                // exh_sum += _exhale_cycle_duration[i];
            }
            _airway_pressure =  _ap_readings_N == 0 ? 0 : _sum_airway_pressure / _ap_readings_N;

            _cycle_readings.respiratory_rate = 60000.0/(tot_sum/CYCLE_AVG_READINGS);
            _cycle_readings.minute_volume = 60*mv_sum/tot_sum;
            _cycle_readings.inhaled_minute_volume = 60*mvi_sum/tot_sum;  //(60 = 60000/1000 L/min rather than mL/min)
            _cycle_readings.exhaled_minute_volume = 60*mve_sum/tot_sum;
            _cycle_readings.tidal_volume = mv_sum/CYCLE_AVG_READINGS;
            _cycle_readings.inhaled_tidal_volume = mvi_sum/CYCLE_AVG_READINGS;
            _cycle_readings.exhaled_tidal_volume = mve_sum/CYCLE_AVG_READINGS;
            _cycle_readings.lung_compliance = _cycle_readings.tidal_volume / (_cycle_readings.peak_inspiratory_pressure -_peep);
            _cycle_readings.static_compliance = _cycle_readings.tidal_volume / (_cycle_readings.plateau_pressure - _peep);
            _cycle_readings.mean_airway_pressure =  _airway_pressure;
            _cycle_readings.inhalation_pressure  =  _airway_pressure;
            _cycle_readings.apnea_index += (_apnea_event == true) ? 1 : 0;
            _cycle_readings.apnea_time = 
                       _measured_durations.buff_pre_inhale
                       +_measured_durations.inhale
                       +_measured_durations.pause
                       +_max_exhale_time;  // apnea time = time from breath start to maximum time allow for breath
            _cycle_readings.mandatory_breath = _mandatory_inhale & _mandatory_exhale;

            _sum_airway_pressure = 0;
            _ap_readings_N = 0;
            _volume_inhale = 0;
            _volume_exhale = 0;
	    _volume = 0;

            //reset
            _cycle_done = true;
        }
/*    } else if ((_bl_state == BL_STATES::IDLE ) || (_bl_state == BL_STATES::CALIBRATION ) || (_bl_state == BL_STATES::STOP) ){
            _sum_airway_pressure = 0;
            _ap_readings_N = 0;
            _volume_inhale = 0;
            _volume_exhale = 0;
            _volume = 0;*/
    } else {
        _cycle_done = false;  // restart cycle
    }

}

void BreathingLoop::updateCalculations() {
    uint32_t tnow = static_cast<uint32_t>(millis());

    if (tnow - _calculations_time >= _calculations_timeout) {
    _calculations.flow              = getFlow(); // TODO: can be run every 1 ms instead of every arduino cycle
    _calculations.flow_calc         = calculateFlow(_readings_avgs.timestamp, _readings_avgs.pressure_patient, _readings_avgs.pressure_buffer);
    _calculations.volume            = getVolume();
    _calculations_time = tnow;
    }
    _calculations.pressure_airway   = getAirwayPressure();
}

void BreathingLoop::setVentilationMode(VENTILATION_MODE mode)
{
    _ventilation_mode = mode;
    switch(_ventilation_mode){

        case VENTILATION_MODE::PC_AC :
            _targets_pcac.inhale_trigger_enable = true; 
            _targets_pcac.exhale_trigger_enable = false; 
            _targets_pcac.volume_trigger_enable = false; 
            _targets_current = &_targets_pcac;
        break;
        case VENTILATION_MODE::PC_AC_PRVC :
            _targets_pcac_prvc.inhale_trigger_enable = true; 
            _targets_pcac_prvc.exhale_trigger_enable = false; 
            _targets_pcac_prvc.volume_trigger_enable = true; 
            _targets_current = &_targets_pcac_prvc;
        break;
        case VENTILATION_MODE::PC_PSV :
            _targets_pc_psv.inhale_trigger_enable = true; 
            _targets_pc_psv.exhale_trigger_enable = true; 
            _targets_pc_psv.volume_trigger_enable = false; 
            _targets_current = &_targets_pc_psv;
        break;
        case VENTILATION_MODE::CPAP :
            _targets_cpap.inhale_trigger_enable = true; 
            _targets_cpap.exhale_trigger_enable = true; 
            _targets_cpap.volume_trigger_enable = false; 
            _targets_current = &_targets_cpap;
        break;
        case VENTILATION_MODE::TEST:
        // in test mode you can set the triggers on / off
            _targets_current = &_targets_test;
        break;
        default : 
        break;

    }
}

VENTILATION_MODE BreathingLoop::getVentilationMode() { return _ventilation_mode; }
readings<float> BreathingLoop::getReadingAverages() { return _readings_avgs; }
readings<float> BreathingLoop::getRawReadings() { return _readings_raw; }

calculations<float> BreathingLoop::getCalculations() { return _calculations; }

float BreathingLoop::getPEEP()
{
    return _peep;
}

float BreathingLoop::getMinuteVolume(){

    return 0;
}

void BreathingLoop::resetReadingSums()
{
    _readings_reset = false;

    uint32_t tnow = static_cast<uint32_t>(millis());
    _readings_time = tnow;
    _readings_avgs_time = tnow;
    _readings_timeout = 1; //ms
    _readings_avgs_timeout = 10; //ms
    _readings_N = 0;
    
    _readings_sums.timestamp                = 0;
    _readings_sums.pressure_air_supply      = 0;
    _readings_sums.pressure_air_regulated   = 0;
    _readings_sums.pressure_buffer          = 0;
    _readings_sums.pressure_inhale          = 0;
    _readings_sums.pressure_patient         = 0;
    _readings_sums.temperature_buffer       = 0;
    _readings_sums.pressure_o2_supply       = 0;
    _readings_sums.pressure_o2_regulated    = 0;
    _readings_sums.pressure_diff_patient    = 0;
    _readings_sums.o2_percent               = 0;
}

//This is used to assign the transitions of the fsm
void BreathingLoop::assignBreatheFSM() {
    uint32_t tnow = static_cast<uint32_t>(millis());
    if (tnow - _fsm_time >= _fsm_timeout) {
        BL_STATES next_state;
        switch (_bl_state)
        {
        case BL_STATES::IDLE:
            if (_running == true) {
                // FSM_time = millis();
                next_state = BL_STATES::PRE_CALIBRATION;
            } else {
                next_state = BL_STATES::IDLE;
            }
            _reset = false;
            break;
        case BL_STATES::PRE_CALIBRATION:
            next_state = BL_STATES::CALIBRATION;
            break;
        case BL_STATES::CALIBRATION:
            next_state = BL_STATES::BUFF_PREFILL;
            break;
        case BL_STATES::BUFF_PREFILL:
            next_state = BL_STATES::BUFF_FILL;
            break;
        case BL_STATES::BUFF_FILL:
            next_state = BL_STATES::EXHALE;  // start with exhale
            break;
        case BL_STATES::BUFF_PRE_INHALE:
            next_state = BL_STATES::INHALE;
            break;
        case BL_STATES::INHALE:
            next_state = BL_STATES::PAUSE;
            break;
        case BL_STATES::PAUSE:
	    next_state = BL_STATES::EXHALE;
            break;
        case BL_STATES::EXHALE:
            if (_running == false) {
                next_state = BL_STATES::STOP;
            } else if (_standby == true) {
                next_state = BL_STATES::STANDBY;
            } else if (_ventilation_mode == VENTILATION_MODE::FLUSH){
                next_state = BL_STATES::BUFF_FLUSH;
            } else if (_ventilation_mode == VENTILATION_MODE::PURGE){
                next_state = BL_STATES::BUFF_PURGE;
            } else {
                next_state = BL_STATES::BUFF_PRE_INHALE;
            }
        case BL_STATES::STANDBY:
            if (_running == false) {
                next_state = BL_STATES::STOP;
            } else if (_standby == true) {
                next_state = BL_STATES::STANDBY;
            } else {
                next_state = BL_STATES::BUFF_PRE_INHALE;
            }
            break;

        case BL_STATES::BUFF_PURGE:
            if (_reset == true ){
                next_state = BL_STATES::IDLE;
            } else if (_safe == false ){
                next_state = BL_STATES::BUFF_PURGE;
            } else if (_running == false) {
                next_state = BL_STATES::IDLE;
            } else {
                next_state = BL_STATES::BUFF_PREFILL;
            }
            break;
        case BL_STATES::BUFF_FLUSH:
            next_state = BL_STATES::IDLE;
            break;
        case BL_STATES::STOP:
            if (_reset == true or _running == true) {
                next_state = BL_STATES::IDLE;
            } else {
                next_state = BL_STATES::STOP;
            }
            break;
        default:
            next_state = _bl_state;
        }
        _bl_state = next_state;
        _fsm_time = tnow;
        // set flag to discard readings due to the mode change
        _readings_reset = true;
    }
    // safety check
    if (tnow - _fsm_time >= 10) {
        if (_safe == false){
            _bl_state = BL_STATES::BUFF_PURGE;
            // TODO RAISE ALARM
            _fsm_timeout = 0;
        }
    }
}

void BreathingLoop::doBreatheFSM()
{
    //bool en1 = _valves_controller.getValveParams().exhale_trigger_enable;
    //bool en2 = _valves_controller.getValveParams().inhale_trigger_enable;
    bool mand_ex = false;
    bool mand_vol = false;

    // float o2_frac_pressure = _o2_valve_frac * _targets_current->buffer_upper_pressure;

    // basic cycle for testing hardware
    switch (_bl_state) {
        case BL_STATES::IDLE:
            
            if (_running == true) {
                // FSM_time = millis();
            } else {
                _fsm_timeout = 1000;
            }
#ifdef EXHALE_VALVE_PROPORTIONAL	    
	    // proportional valve normally closed
            _valves_controller.setBreatheValves(VALVE_STATE::FULLY_CLOSED, VALVE_STATE::FULLY_CLOSED);
#else
	    // digital valve normally open
            _valves_controller.setBreatheValves(VALVE_STATE::FULLY_CLOSED, VALVE_STATE::OPEN);
#endif
            initCalib();
            break;
        case BL_STATES::PRE_CALIBRATION : 
            _valves_controller.setBreatheValves(VALVE_STATE::CLOSED, VALVE_STATE::OPEN);
            _fsm_timeout = _states_durations.pre_calibration;
            break;
        case BL_STATES::CALIBRATION : 
            _valves_controller.setBreatheValves(VALVE_STATE::OPEN, VALVE_STATE::OPEN);
            calibrate();
            _fsm_timeout = _states_durations.calibration;
            break;
        case BL_STATES::BUFF_PREFILL:
            // TODO - exhale settable; timeout expert settable
            _calibrated = true;
            _valves_controller.setBreatheValves(VALVE_STATE::CLOSED, VALVE_STATE::OPEN);
            _fsm_timeout = _states_durations.buff_prefill;
            break;
        case BL_STATES::BUFF_FILL:
            // TODO - exhale settable; timeout settable
            _valves_controller.setBreatheValves(VALVE_STATE::CLOSED, VALVE_STATE::OPEN);
            _fsm_timeout = _states_durations.buff_fill;
            break;
        case BL_STATES::BUFF_PRE_INHALE:
            // TODO spontaneous trigger can be enabled
            // - can be triggered by : 
                // P_inhale ; 
                // P_diff_patient //=flow
                // P_patient and p_diff_patient
                // P_patient or p_diff_patient
                // with thresholds on each
            _valves_controller.setBreatheValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
            switch (_ventilation_mode)
            {
                case FLUSH:
                    _fsm_timeout = 100;
                    
                    break;
                case PURGE:
                    _fsm_timeout =500;
                    
                    break;
                default:
                    _fsm_timeout = _states_durations.buff_pre_inhale;
            }

	    _pid.integral = 0.;//Resets the integral of the Inhale Valve PID before the inhale cycle starts 
	    _pid.target_pressure = 0.; // Resets the target pressure for the PID target profile 
	    _pid.derivative = 0.; // Resets the derivative for Inhale PID
	    _pid.istep = 0;

            _peep = _running_avg_peep;
        
            break;
        case BL_STATES::INHALE:
            // The inhale valve will be opened in the updateReadings function (PID)
            _fsm_timeout = _states_durations.inhale;

            _inhale_triggered = false; // reset inhale trigger
            _valley_flow = 100000;  // reset valley after exhale
            _valley_flow_time = millis();  // reset valley after exhale
            
            mand_ex = exhaleTrigger();
	    // mand_vol = volumeTrigger();  // disable for now
            _mandatory_exhale = mand_ex ; // & mand_vol;
            break;
        case BL_STATES::PAUSE:
            _valves_controller.setBreatheValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
            _fsm_timeout = _states_durations.pause;
            _valley_flow = 100000;  // reset valley after exhale
            _valley_flow_time = millis();  // reset valley after exhale

            _states_durations.exhale = calculateDurationExhale();
            // doO2ValveFrac(_targets_current->fiO2_percent, _targets_current->buffer_upper_pressure);  
            break;
        case BL_STATES::EXHALE:
            _peak_flow = -100000;  // reset peak after inhale
            _peak_flow_time = millis();  
            _fsm_timeout = _states_durations.exhale;

            _expected_fiO2 = _new_expected_fiO2;
            _valves_controller.setBreatheValves(VALVE_STATE::CLOSED, VALVE_STATE::OPEN);

            measurePEEP();
            digitalWrite(pin_led_red, LOW);
            _mandatory_inhale = inhaleTrigger();
            _pressure_buffer_fitter.resetCalculation(_peak_flow_time);
            _pressure_patient_fitter.resetCalculation(_peak_flow_time);
            break;
        case BL_STATES::STANDBY:
            _valves_controller.setBreatheValves(VALVE_STATE::CLOSED, VALVE_STATE::OPEN);
            _fsm_timeout = 1000;
            break;
        case BL_STATES::BUFF_PURGE:
            _valves_controller.setBreatheValves(VALVE_STATE::CLOSED, VALVE_STATE::OPEN);
            _fsm_timeout = _states_durations.buff_purge;
            break;
        case BL_STATES::BUFF_FLUSH:
            _valves_controller.setBreatheValves(VALVE_STATE::FULLY_OPEN, VALVE_STATE::OPEN);
            _fsm_timeout = _states_durations.buff_flush;
            break;
        case BL_STATES::STOP: 
            // TODO : require a reset command to go back to idle
            _valves_controller.setBreatheValves(VALVE_STATE::FULLY_CLOSED, VALVE_STATE::OPEN);
            _fsm_timeout = 1000;
            break;
        default:
            // TODO - shouldn't get here: raise alarm
            break;
    }
    safetyCheck();
    assignFillFSM();
    measureDurations();
}

void BreathingLoop::assignFillFSM()
{
    switch(_bl_state){
        case BL_STATES::EXHALE:
            if (_bl_laststate != BL_STATES::EXHALE){
                _fill_state = determineFillMode();
		logMsg("Fill state: " + String(_fill_state));
	    }
            break;
        case BL_STATES::BUFF_FILL:
            _fill_state = FILL_STATES::AIR_FILL;
            break;
        case BL_STATES::PRE_CALIBRATION:
            _fill_state = FILL_STATES::PURGE;
            break;
        case BL_STATES::CALIBRATION:
            _fill_state = FILL_STATES::PURGE;
            break;
        case BL_STATES::BUFF_PURGE:
            _fill_state = FILL_STATES::PURGE;
            break;
        default:
            _fill_state = FILL_STATES::VALVES_CLOSED;
    }
}

void BreathingLoop::doFillFSM()
{
    switch (_fill_state) {
        case FILL_STATES::VALVES_CLOSED:
            _valves_controller.setFillValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
            break;
        case FILL_STATES::AIR_FILL:
            // The second condition is probably not needed, since if it is true _bl_state would already have changed. TODO if it is the case
            if((_readings_avgs.pressure_buffer >= _targets_current->buffer_upper_pressure) || (millis() - _fsm_time >= (_fsm_timeout - 10))){
                    _valves_controller.setFillValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
                } else if(_readings_avgs.pressure_buffer < _targets_current->buffer_lower_pressure){
                    // fill AIR
                    _valves_controller.setFillValves(VALVE_STATE::OPEN, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
                }
            break;
        case FILL_STATES::PURGE:
            //purge
	    _valves_controller.setFillValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::OPEN);
            break;
        case FILL_STATES::INCREASE_O2:
            if(_readings_avgs.pressure_buffer >= _targets_current->buffer_upper_pressure){
                _valves_controller.setFillValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
            } else if(_readings_avgs.pressure_buffer < _targets_current->buffer_lower_pressure){
                if ((_readings_avgs.pressure_buffer > _p_to_purge) && (millis() - _t_start_purge < _t_max_purge)){
                    // purge
                    _valves_controller.setFillValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::OPEN);
                }else{
                    _p_to_purge = _targets_current->buffer_upper_pressure; //do this to avoid getting into if clause again
                    // fill o2
                    _valves_controller.setFillValves(VALVE_STATE::CLOSED, VALVE_STATE::OPEN, VALVE_STATE::CLOSED);
                }
            }
            break;
        case FILL_STATES::DECREASE_O2:
            if(_readings_avgs.pressure_buffer >= _targets_current->buffer_upper_pressure){
                _valves_controller.setFillValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
            } else if(_readings_avgs.pressure_buffer < _targets_current->buffer_lower_pressure){
                if ((_readings_avgs.pressure_buffer > _p_to_purge) && (millis() - _t_start_purge < _t_max_purge)){
                    // purge
                    _valves_controller.setFillValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::OPEN);
                }else{
                    _p_to_purge = _targets_current->buffer_upper_pressure; //do this to avoid getting into if clause again
                    // fill air
                    _valves_controller.setFillValves(VALVE_STATE::OPEN, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
                }
            }
            break;
        case FILL_STATES::MAINTAIN_O2:
            if(_readings_avgs.pressure_buffer >= _targets_current->buffer_upper_pressure){
                _valves_controller.setFillValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
		        _finished_filling = true;
            } else if(_readings_avgs.pressure_buffer < _targets_current->buffer_lower_pressure || !_finished_filling){
                if (_readings_avgs.pressure_buffer < _o2_frac_pressure){
                    // fill O2
                    _valves_controller.setFillValves(VALVE_STATE::CLOSED, VALVE_STATE::OPEN, VALVE_STATE::CLOSED);
                }else if(_valves_controller.getO2Valve()){
                    // close O2 valve before opening air valve
                    _valves_controller.setFillValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
		        }else if (millis() - _time_valve_closure > 20){
                    // fill air
                    _valves_controller.setFillValves(VALVE_STATE::OPEN, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
                }
            }
            break;
        default:
            // TODO - shouldn't get here: raise alarm
            break;
    }
}

void BreathingLoop::measureDurations( ) {
    if (_bl_state != _bl_laststate) {
        uint32_t tnow = static_cast<uint32_t>(millis());
        uint32_t tdiff = tnow - _lasttime;
        switch (_bl_laststate)
        {
        case BL_STATES::PRE_CALIBRATION:
            _measured_durations.pre_calibration = tdiff;
            break;
        case BL_STATES::CALIBRATION:
            _measured_durations.calibration = tdiff;
            break;
        case BL_STATES::BUFF_PRE_INHALE:
            _measured_durations.buff_pre_inhale = tdiff;
            break;
        case BL_STATES::INHALE:
            _measured_durations.inhale = tdiff;
            break;
        case BL_STATES::PAUSE:
            _measured_durations.pause = tdiff;
            break;
        case BL_STATES::EXHALE:
            _measured_durations.exhale = tdiff;
            break;
        case BL_STATES::BUFF_PURGE:
            _measured_durations.buff_purge = tdiff;
            break;
        case BL_STATES::BUFF_FLUSH:
            _measured_durations.buff_flush = tdiff;
            break;
        default:
            break;
        }
        _bl_laststate = _bl_state;
        _lasttime = tnow;
    }
}

void BreathingLoop::measurePEEP()
{
    if(fabs(_flow) < 1){
        //    _peep = _readings_avgs.pressure_patient;
        float sum_peep = 0;
        _running_peep[_running_index_peep] = _readings_avgs.pressure_patient;

        for(int i=0; i<RUNNING_AVG_READINGS-1; i++){
            sum_peep += static_cast<float>(fabs(_running_peep[i]));
        }
        //_running_avg_peep = sum_peep/RUNNING_AVG_READINGS;

        _running_index_peep = (_running_index_peep == RUNNING_AVG_READINGS-1 ) ? 0 : _running_index_peep+1;

    }
    //KH
        _running_avg_peep = _readings_avgs.pressure_patient;
	
}

void BreathingLoop::safetyCheck()
{
    // based on averages or instantaneous values?
    if (_calibrated){
        if (_readings_avgs.pressure_inhale > _pid.max_patient_pressure)
            _safe = false;
        else if (_readings_avgs.pressure_patient > _pid.max_patient_pressure)
            _safe = false;
        else 
            _safe = true;
    }
}

void BreathingLoop::doStart()
{
    _running = true;
    _standby = false;
}

void BreathingLoop::doStop()
{
    _running = false;
    _standby = false;
}

void BreathingLoop::doReset()
{
    _reset = true;
    _standby = false;
}

void BreathingLoop::doStandby()
{
    _standby = true;
}

bool BreathingLoop::getRunning()
{
    return _running;
}

void BreathingLoop::calibrate()
{
	_fiO2_est = 0.21; // reset (as of now, always start with pure air in buffer)
    // get pressure_air_regulated over last sec of 10s calc mean
    uint32_t tnow = static_cast<uint32_t>(millis());
    if (tnow - _calib_time >= _calib_timeout ) {
        _calib_N++;
        _calib_sums.pressure_air_regulated += static_cast<float>(analogRead(pin_pressure_air_regulated));
        _calib_avgs.pressure_air_regulated  = static_cast<float>(_calib_sums.pressure_air_regulated/ _calib_N);
        _calib_sums.pressure_o2_regulated += static_cast<float>(analogRead(pin_pressure_o2_regulated));
        _calib_avgs.pressure_o2_regulated  = static_cast<float>(_calib_sums.pressure_o2_regulated/ _calib_N);
        _calib_sums.pressure_buffer += static_cast<float>(analogRead(pin_pressure_buffer));
        _calib_avgs.pressure_buffer  = static_cast<float>(_calib_sums.pressure_buffer/ _calib_N);
        _calib_sums.pressure_inhale += static_cast<float>(analogRead(pin_pressure_inhale));
        _calib_avgs.pressure_inhale  = static_cast<float>(_calib_sums.pressure_inhale/ _calib_N);
        _calib_sums.pressure_patient += static_cast<float>(analogRead(pin_pressure_patient));   
        _calib_avgs.pressure_patient = static_cast<float>(_calib_sums.pressure_patient/ _calib_N);
        _calib_sums.pressure_diff_patient += static_cast<float>(analogRead(pin_pressure_diff_patient));
        _calib_avgs.pressure_diff_patient = static_cast<float>(_calib_sums.pressure_diff_patient/ _calib_N);

	_calib_time = tnow;
	_calib_timeout = 10;
    }
}


void BreathingLoop::initCalib()
{   // do calibration in last sec of calibration step (normally 10s) or default to 10ms
    _calibrated = false;
    _calib_timeout = 10;  
    if (_states_durations.calibration - 1000 >= 10)
        _calib_timeout = _states_durations.calibration - 1000;
    _calib_time = static_cast<uint32_t>(millis());
    _calib_sums.pressure_air_regulated = 0;
    _calib_sums.pressure_o2_regulated  = 0;
    _calib_sums.pressure_buffer = 0;
    _calib_sums.pressure_inhale = 0;
    _calib_sums.pressure_patient = 0;
    _calib_sums.pressure_diff_patient = 0;
    _calib_avgs.pressure_air_regulated = 0;
    _calib_avgs.pressure_o2_regulated  = 0;
    _calib_avgs.pressure_buffer = 0;
    _calib_avgs.pressure_inhale = 0;
    _calib_avgs.pressure_patient = 0;
    _calib_avgs.pressure_diff_patient = 0;
    _calib_N = 0;
}


states_durations &BreathingLoop::getDurations() { return _states_durations; }
cycle_readings &BreathingLoop::getCycleReadings() { return _cycle_readings; }

uint32_t BreathingLoop::calculateDurationExhale() {
//     uint32_t exhale_duration = (_states_durations.inhale * getIERatio())  - _states_durations.exhale ;
//     if (exhale_duration < _min_exhale_time)
//         exhale_duration = _min_exhale_time;
//     return static_cast<uint32_t>(exhale_duration);
    float total_dur = 60000.0/_targets_current->respiratory_rate;
    float new_exhale = total_dur 
                - ( _measured_durations.buff_pre_inhale
                  + _measured_durations.inhale
                  + _measured_durations.pause);
    if (new_exhale < _min_exhale_time)
        new_exhale = _min_exhale_time;
    // logMsg("new exhale " 
    //               + String(total_dur) 
    //               +" "+String( _measured_durations.buff_pre_inhale)
    //               +" "+String( _measured_durations.inhale)
    //               +" "+String( _measured_durations.pause)
    //               +" "+String( _measured_durations.exhale));
    
    return static_cast<uint32_t>(new_exhale);
}

float    BreathingLoop::getIERatio(){
    // TODO : check with Oscar/Xavier 
    float total_inhale_time = _states_durations.inhale + _states_durations.pause;
    float total_exhale_time = _states_durations.exhale;
    return total_inhale_time/total_exhale_time;
}


// KH 20200518 - TODO; 
//   - need an update CycleReadings function called from exhale
//   - need to track times for inhale and exhale to measure IE
//   - need to find peak and plateau of pressure
void BreathingLoop::updateIE()
{

    uint32_t total_cycle = static_cast<uint32_t>(60*1000/_targets_current->respiratory_rate);
    int32_t inhale_duration = _targets_current->inhale_time;

    if (_targets_current->ie_selected == true){
	
	    uint32_t tot_inh = total_cycle / (1.0 + (1.0/_targets_current->ie_ratio)); 
//	    uint32_t tot_exh = total_cycle / (1.0 + (_targets_current->ie_ratio)); 

	    inhale_duration = tot_inh - _states_durations.pause;
	    //_targets_current->ie_selected =false;
        if (inhale_duration < _min_inhale_time){
            _states_durations.inhale = _min_inhale_time;
        } else {
            _states_durations.inhale = inhale_duration; 
        }
        _targets_current->inhale_time = _states_durations.inhale;
	    
    } else {
        if (inhale_duration < _min_inhale_time){
            _states_durations.inhale = _min_inhale_time;
        } else {
            _states_durations.inhale = inhale_duration; 
        }
        float tot_inh = _states_durations.inhale + _states_durations.pause;
        float exhale_duration = total_cycle - tot_inh;
        _targets_current->ie_ratio = tot_inh / exhale_duration;
    }


    // TODO - what if exhale time is less than min; raise error?
}

void BreathingLoop::updateFromTargets()
{
    _pid.target_final_pressure = _targets_current->inspiratory_pressure ;  //TODO -  should fix this to one variable
    updateIE();

}


float BreathingLoop::getTargetRespiratoryRate(){
    return _targets_current->respiratory_rate;
}

ValvesController* BreathingLoop::getValvesController()
{
    return &_valves_controller;
}

// void BreathingLoop::updateTotalCycleDuration(uint16_t newtotal)
// {
//     const uint8_t N = 3;
//     for(int i=0; i<N-1; i++){
//         _total_cycle_duration[i] = _total_cycle_duration[i+1];

//     }
//     _total_cycle_duration[N-1] = newtotal;
// }

float BreathingLoop::calculateFlow(const uint32_t &current_time, const float &pressure_patient, const float &pressure_buffer, float volume_tube, float volume_buffer) {
    float dp_tube, dp_buffer, offset;
    uint8_t linreg;
    float const_pressure = 1013.; //mbar

    _pressure_buffer_fitter .appendPoints(current_time, pressure_buffer  + const_pressure);
    _pressure_patient_fitter.appendPoints(current_time, pressure_patient + const_pressure);

    linreg = _pressure_buffer_fitter .linearRegression(dp_buffer, offset);
    linreg += _pressure_patient_fitter.linearRegression(dp_tube  , offset);

    if (linreg == 0) return (((-1./(pressure_patient + const_pressure)) * ((dp_tube * volume_tube) + (dp_buffer * volume_buffer))));// - (1. * 4 * dp_tube));
    //if (linreg == 0) return _pressure_buffer_fitter.GetSumX2(); //(((-1./(pressure_patient + const_pressure)) * ((dp_tube * volume_tube) + (dp_buffer * volume_buffer))));// - (1. * 4 * dp_tube));
    else return 0;
    //return dp_buffer;
}

float BreathingLoop::getFlow(){
    const float temperature = 298.0;
    const float pressure = 1030.0;
    const float calibration_factor=1.40 ;// adjusted to make VTE=VTI
    
    float l2nl = (temperature *1013.25)/(pressure * 273.15 ) ; 
    float dp_raw = _readings_avgs.pressure_diff_patient;
    float flowtmp;
    

     

    flowtmp = pow(dp_raw,3)*0.1512-3.3422*pow(dp_raw,2)+dp_raw*41.657;  // this is in slm (standard liter per minute)

    _flow =  calibration_factor * flowtmp * l2nl;  // now expressed in l/min

    if (_calibrated == true){
        return _flow;
    }
    return 0.0;
}
/*
float BreathingLoop::getFlow(){
    float normal_volume = 1;
    float si_volume = (_readings_avgs.temperature_buffer / _readings_avgs.pressure_patient ) * (1013.25/273.15) * normal_volume;
    // conversion from V to dp from dp-sensor manual: https://docs.rs-online.com/7d77/0900766b81568899.pdf (500 Pa range?) [Pa -> mbar => 525 -> 5.25]
    float dp_raw = _readings_avgs.pressure_diff_patient / 4096.0 ; // assuming 12bit ADC
    int sign = (dp_raw -0.5) < 0 ? -1 : 1;
    if ((dp_raw -0.5) == 0.000) 
        sign = 0.0;
    float dp = sign*pow(((dp_raw/0.4)-1.25),2) * 5.25; 
    // 
    float flow = dp;


    // NLPM - normal litres per minute = 1 Si Litre per minute * (293.15/T)*(P/1013.25)
    float T = 25+273.15; //_readings_avgs.temperature_buffer;
    float P = _readings_avgs.pressure_patient;
    float nlpm_factor = (293.15/T)*(P/1013.25); 
    return flow;
    // float R = 0.08206 * 1/0.98692 *1000; // mbar *l * mol-1 *K-1
    // float T = 25+273.15; //_readings_avgs.temperature_buffer;
    // float V_buffer = 10.0 ; //l 
    // float V_tube = 1.4 ; //l
    // float P_tube = _readings_avgs.pressure_inhale;
    // 
    // float n1 = _readings_avgs.pressure_buffer * V_buffer/(R*T);
    // float n2 = _readings_avgs.pressure_inhale * V_tube/(R*T);
    // float M = 15.99; // molar mass O2 g.mol-1
    // float rho = 1.42 * 1000; // density  1.2kg/m3 @ 25 deg
}
*/

float BreathingLoop::getVolume()
{

    // TODO: need a real calib here
    const float temperature = 298.0;
    const float pressure = 1030.0;
    // normal litres/h to millilitres
    //  need to get dt - assume dt = 10ms
    float nl2l = (pressure * 273.15 )/(temperature *1013.25) ; 

    float flow = _calculations.flow; //getFlow(); // flow is now in l/min
    float vol = flow*1000.0 / (60 * 100) ; //1000 l-> ml; 60s ; 100 = 10ms measure -> 1s

    _volume += vol * nl2l; // real KH

    if (_calibrated == true){
        return _volume;
    }
    return 0.0;
}

float BreathingLoop::getAirwayPressure(){
    if (_calibrated == true){
        return _airway_pressure;
    }
    return 0.0;
}

void BreathingLoop::doPID(){

    // Set PID profile using the set point
    // nsteps defines the number of intermediate steps
    //
    //

    _pid.istep +=1;

    //_pid.process_pressure = _readings_avgs.pressure_inhale;

    float _pid_set_point_step = _pid.target_final_pressure/_pid.nsteps;

    _pid.target_pressure += _pid_set_point_step;

    // Slightly ad hoc way of setting the target pressure steps! NB! the number of statements must match the number of steps (_pid.nsteps)
    if (_pid.istep == 1) _pid.target_pressure = 0.1*_pid.target_final_pressure;
    if (_pid.istep == 2) _pid.target_pressure = 0.4*_pid.target_final_pressure;
    if (_pid.istep >= 3) _pid.target_pressure = _pid.target_final_pressure;

    if(_pid.target_pressure > _pid.target_final_pressure) _pid.target_pressure = _pid.target_final_pressure;

    //Calculate the PID error based on the pid set point
    float error = _pid.target_pressure - _pid.process_pressure;

    //_pid.proportional       = _targets_current->pid_gain * _pid.Kp*error;
    //_pid.integral          += _targets_current->pid_gain * _pid.Ki*error;

    _pid.proportional       = _pid.pid_gain * _pid.Kp*error;
    _pid.integral          += _pid.pid_gain * _pid.Ki*error;
    //Derivative calculation

    float _derivative = _pid.previous_process_pressure - _pid.process_pressure ;

    _pid.derivative = 0.7*_pid.derivative + 0.3*_derivative;

    //Checking minium and maximum duty cycle
    
    float minimum_open_frac = 0.52; //Minimum opening to avoid vibrations on the valve control
    float maximum_open_frac = 0.74; //Maximum opening for the PID control

    //_pid.valve_duty_cycle = _pid.proportional + _pid.integral + (_targets_current->pid_gain * _pid.Kd * _pid.derivative) + minimum_open_frac;
    _pid.valve_duty_cycle = _pid.proportional + _pid.integral + (_pid.pid_gain * _pid.Kd * _pid.derivative) + minimum_open_frac;

    if(_pid.valve_duty_cycle > maximum_open_frac) _pid.valve_duty_cycle = maximum_open_frac;
    if(_pid.valve_duty_cycle < minimum_open_frac) _pid.valve_duty_cycle = minimum_open_frac;

}

//void BreathingLoop::PID_process_pressure_derivative(float &_pid_process_pressure_derivative, float process_pressure){
	//process_pressure
//}

pid_variables& BreathingLoop::getPIDVariables()
{
    return _pid;
}

target_variables& BreathingLoop::getTargetVariablesPC_AC(){ return _targets_pcac; }
target_variables& BreathingLoop::getTargetVariablesPC_AC_PRVC(){ return _targets_pcac_prvc; }
target_variables& BreathingLoop::getTargetVariablesPC_PSV(){ return _targets_pc_psv; }
target_variables& BreathingLoop::getTargetVariablesCPAP(){ return _targets_cpap; }
target_variables& BreathingLoop::getTargetVariablesTest(){ return _targets_test; }
target_variables& BreathingLoop::getTargetVariablesCurrent(){ return (*_targets_current); }

bool BreathingLoop::inhaleTrigger()
{
    bool en = _targets_current->inhale_trigger_enable;

    //logMsg("inhale trig- " + String(_readings_avgs.pressure_diff_patient,6) + " " + String(_valves_controller.getValveParams().inhale_trigger_threshold,6));
    String result = "";

    if(en == true){
        if (_inhale_triggered)
        {
            _fsm_timeout = 0; // go to next state immediately
            return _mandatory_inhale;
        }
        //_fsm_timeout = _max_exhale_time;
        uint32_t tnow = static_cast<uint32_t>(millis());


        //TODO: calculate expected point here?
        float expected_flow =  _flow_fitter.extrapolate(tnow); // will return correct extrapolation of max float value

	//if ((tnow - _fsm_time) % 100 == 0)logMsg("A " + String(expected_flow) +" "+String(_flow));
	/*
	uint32_t x0, xn;
	float y;
	uint8_t e; 
        float extrap = _flow_fitter.extrapolate(millis()); 

	_flow_fitter.getLast(x0, xn,y,e);
	logMsg("x0 "+String(x0)+ " xn "+String(xn)+" y "+String(y)+" e "+String(e) +" extrap "+extrap);
	*/


        // NOTE: _flow should be positive only in this case?
        if (((_flow - expected_flow) > _targets_current->inhale_trigger_threshold)
        //if((_readings_avgs.pressure_diff_patient > _targets_current->inhale_trigger_threshold)
            && (_flow > _valley_flow*0.1)
            && (tnow - _valley_flow_time >= 100)){  // wait 100ms after the valley
            if (tnow - _fsm_time >= _min_exhale_time ) {
                // TRIGGER
                //logMsg("   -- INHALE TRIGGER "  +String(millis()) + String("Exp. Flow: ") + String(expected_flow) + String(" Difference: ") + String(_flow - expected_flow));
                //logMsg("   -- INHALE TRIGGER "  +String(millis()) );//+ String("Exp. Flow: ") + String(expected_flow) + String(" Difference: ") + String(_flow - expected_flow));
                result = "   -- INHALE TRIGGER" ;
                _fsm_timeout = 0; // go to next state immediately
                _apnea_event = false;
                _inhale_triggered = true;
		digitalWrite(pin_led_red, HIGH);
                return false;
            }
	//	logMsg("D " + String(expected_flow) +" "+String(_flow));
		//logMsg("D FSM " + String(tnow) + " " + String(_fsm_time)+" "+String(_fsm_timeout));
		//logMsg("D Valley " + String(_valley_flow_time) + " " + String(_valley_flow));
        } else if (tnow - _fsm_time >= _max_exhale_time){
                // TRIGGER
                _apnea_event = true;
                //logMsg("   -- inhale trigger - max exhale time exceeded");// + String("Exp. Flow: ") + String(expected_flow) + String(" Difference: ") + String(_flow - expected_flow));
                result = "   -- TIME EXCEEDED" ;
                _fsm_timeout = 0; // go to next state immediately
                _apnea_event = true;
                return true;
        }
    }
    return true;
}

bool BreathingLoop::exhaleTrigger()
{
    bool en = _targets_current->exhale_trigger_enable;

    //logMsg("EXhale trig- " + String(_flow) + " " + String(_running_avg_flow) +" "+ String(_valves_controller.getValveParams().exhale_trigger_threshold)+" "+String(_peak_flow));

    if(en == true){
        //logMsg("exhale trigger");
        uint32_t tnow = static_cast<uint32_t>(millis());
        if((_running_avg_flow < (_targets_current->exhale_trigger_threshold * _peak_flow)) 
            && (tnow - _peak_flow_time >= 100)){ // wait 10ms after peak
            //TODO - check we're past 'peak'
            //logMsg("  EXhale trig- " + String(_running_avg_flow) +" "+ String(vp.exhale_trigger_threshold)+" "+String(_peak_flow));
            if (tnow - _fsm_time >= _min_inhale_time ) {
                // TRIGGER
                _fsm_timeout = 0; // go to next state immediately
		digitalWrite(pin_led_red , HIGH);
                return false;// not mandatory exhale
            }
        }
    }
    return true; //mandatory exhale
}

bool BreathingLoop::volumeTrigger()
{
    bool en = _targets_current->volume_trigger_enable;

    //logMsg("volume trig- " + String(_flow) + " " + String(_running_avg_flow) +" "+ String(_valves_controller.getValveParams().exhale_trigger_threshold)+" "+String(_peak_flow));

    if(en == true){
        //logMsg("volume trigger");
        uint32_t tnow = static_cast<uint32_t>(millis());
        if(_volume < _targets_current->volume){ 
            if (tnow - _fsm_time >= _min_inhale_time ) {
                // TRIGGER
                _fsm_timeout = 0; // go to next state immediately
		digitalWrite(pin_led_red , HIGH);
                return false;// not mandatory exhale
            }
        }
    }
    return true; //mandatory exhale
}

void BreathingLoop::runningAvgs()
{

    // take the average of the last N flows 
    float sum_flow = 0;
    _running_flows[_running_index] = getFlow(); //_flow;


    for(int i=0; i<RUNNING_AVG_READINGS-1; i++){
        // use absolute value to avoid averaging out negative vals
        sum_flow += static_cast<float>(fabs(_running_flows[i]));
    }
    _running_avg_flow = sum_flow/RUNNING_AVG_READINGS;

    _running_index = (_running_index == RUNNING_AVG_READINGS-1 ) ? 0 : _running_index+1;

    if ((_flow > _peak_flow) && (_bl_state == BL_STATES::INHALE)){
        uint32_t tnow = static_cast<uint32_t>(millis());
        _peak_flow_time = tnow;
        _peak_flow = _flow;
    }
    
    if ((_flow < _valley_flow) && (_bl_state == BL_STATES::EXHALE )){
        uint32_t tnow = static_cast<uint32_t>(millis());
        _valley_flow_time = tnow;
        _valley_flow = _flow;

        _flow_fitter.resetCalculation(tnow);
    }

    if(_bl_state == BL_STATES::PAUSE ){
        // even if pause duration is 0, this should execute once
        _cycle_readings.plateau_pressure = _readings_avgs.pressure_patient; //_running_avg_plateau_pressure;
    }

    if ((_readings_avgs.pressure_patient > _cycle_readings.peak_inspiratory_pressure) && (_bl_state == BL_STATES::INHALE)){
        _cycle_readings.peak_inspiratory_pressure = _readings_avgs.pressure_patient;
    }

    
    if((_bl_state == BL_STATES::INHALE) || (_bl_state == BL_STATES::BUFF_PRE_INHALE) || (_bl_state == BL_STATES::PAUSE)){
        _volume_inhale = _volume; //getVolume();
	//logMsg("INHALE "+String(_volume_inhale));
    } else if (_bl_state == BL_STATES::EXHALE){
        _volume_exhale = _volume_inhale - _volume; //getVolume();
        //if(fabs(_flow) < 0.02){
        //    _peep = _readings_avgs.pressure_patient;
        //}
	//logMsg(" EXHALE "+String(_volume_exhale));
	_flow_fitter.appendPoints(millis(), _flow);
    }

    _sum_airway_pressure += _readings_avgs.pressure_patient;
    _ap_readings_N++;

}

void BreathingLoop::tsigReset()
{
	uint32_t tnow = static_cast<uint32_t>(millis());
	if (tnow - _tsig_time >= _tsig_timeout ) {
		_tsig_time = tnow;
		digitalWrite(pin_led_red , LOW);
	}
}



// void BreathingLoop::doO2ValveFrac(float desired_fiO2, float pressure_change)
// {
//     // this assumes o2 and air valves fill at same rates, AND that we fill sequentially - o2, then air.

//     // pressure_change is proportional to the amount of volume exhanged in a cycle
//     // I think this equals tidal inhale volume
    
//     // we calculate amount of o2 : air to input
//     // if we have to fill 300 mbar, we fill up to (o2_frac * 300) mbar of o2, then (1-o2_frac)*300 mbar air

//     // we estimate the current o2 fraction, rather than wait for o2 sensor
//     // we should have an alarm if o2 sensor and o2 expectation is wrong after 1 min

//     float o2change = (desired_fiO2*(1000+pressure_change) - _expected_fiO2 *1000 -0.21*pressure_change)/(0.79*pressure_change);
//     if (o2change > 1){
//         o2change = 1;
//     } else if (o2change < 0){
//         o2change = 0;
//     }
//     _new_expected_fiO2 = _expected_fiO2*1000 + o2change*pressure_change + 0.21*(1-o2change)*pressure_change;
//     _o2_valve_frac = o2change;

// 	// airValveFrac = 1.0 - O2ValveFrac
// }

bool BreathingLoop::doExhalePurge()
{
	// do nothing for now
	return false;
	uint32_t tnow = millis();
	// purge-to-fill ratio  = 0.66 => spend 66% time purging 33% filling buffer
	
        if (tnow - _fsm_time >= static_cast<uint32_t>(0.66*_min_exhale_time) ) {
            if (fabs(_targets_current->fiO2_percent - _readings_avgs.o2_percent) < 1) {   // 1% tolerance
                return true;
            }
    }
	return false;
}

void BreathingLoop::updateO2Concentration()
{
    // Check for valves state
    bool vin_air, vin_o2, vpurge;
    uint8_t vinhale, vexhale;
    float p_atm         = 1013.15; // [mbar]
    float p_buff_now    = _readings_avgs.pressure_buffer + p_atm;
    float delta_p       = p_buff_now - _pressure_before_filling;
    _valves_controller.getValves(vin_air, vin_o2, vinhale, vexhale, vpurge); // TODO create function to only read air_in and O2_in

    // check if state changed
    if(vin_air == _valve_air_last_state && vin_o2 == _valve_O2_last_state)
    {
        // states did not change -> do nothing
    }else if (vin_air != _valve_air_last_state && vin_o2 != _valve_O2_last_state)
    {
        logMsg("Both valves changed state");
	    // should not happen - raise alarm. For now do nothing
    }else if (vin_o2 != _valve_O2_last_state){
        if(vin_o2){
            // O2 valve from closed->open
            _pressure_before_filling = p_buff_now;
        }else{
            // O2 valve from open->closed
            _time_valve_closure = millis();
	    if (delta_p < 0){
                _fill_state = FILL_STATES::AIR_FILL; // safety precaution: when during O2 filling not enough pressure is provided, fill with air
            }else{
                // _fiO2_est = (delta_p + _fiO2_est * _pressure_before_filling) / p_buff_now; //old
                _fiO2_est = _fiO2_est + (1 - _fiO2_est) * (delta_p / p_buff_now);
            }   
        }
    }else if (vin_air != _valve_air_last_state){
        if(vin_air){
            // air valve from closed->open
            _pressure_before_filling = p_buff_now;
        }else{
            // air valve from open->closed
            _time_valve_closure = millis();
	        // TODO check this calculation
            if (delta_p < 0){
                _fill_state = FILL_STATES::AIR_FILL;
            }else{
                // _fiO2_est = 1 - (delta_p * 0.79 +(1 - _fiO2_est) * _pressure_before_filling) / p_buff_now;
                _fiO2_est = 0.21 + (_fiO2_est - 0.21) * (p_buff_now - delta_p) / p_buff_now;
            }
        }
    }
    _valve_O2_last_state = vin_o2;
    _valve_air_last_state = vin_air;

    if(_fiO2_est <= 0.21) 
    {
        _fiO2_est = 0.211; //NEVER equal to 0.21 since a division by 0 could occur
    }else if(_fiO2_est >=1){
        // something went wrong, raise error
        _fiO2_est = 0.99;  //NEVER equal to 1 since a division by 0 could occur
    }
    // _readings_avgs.o2_percent = _fiO2_est * 100;
}

uint8_t BreathingLoop::determineFillMode()
{
    /*
     * The derivation of this control can be found in oxygen_control_analytics.pdf
     * TODO find atmospheric pressure during calibration
     *
     */	
    float p_buff_now    = _readings_avgs.pressure_buffer;
    float p_buff_upper  = _targets_current->buffer_upper_pressure;
    float fiO2_desired  = _targets_current->fiO2_percent / 100;
    float p_atm = 997; // [mbar]
    float p_max_purge = 150;
    float delta_fiO2	= fiO2_desired - _fiO2_est;
    uint8_t next_fill_state;

    if (fiO2_desired < 0.22 && delta_fiO2 > -0.1){
        // If fiO2_est is below 32% fill with air without purging
	next_fill_state = FILL_STATES::AIR_FILL;
    }else if (delta_fiO2 > 0.){      
        float dp_purge = (p_atm + p_buff_upper) * delta_fiO2 / (1 - _fiO2_est);
        if (dp_purge < (p_buff_upper - p_max_purge)){
            _p_to_purge = p_buff_upper - dp_purge;
        }else{
            _p_to_purge = p_max_purge;
        }
        _t_max_purge = 0.5 *  _states_durations.exhale;
        _t_start_purge = millis();
        next_fill_state = FILL_STATES::INCREASE_O2;
    }else if (delta_fiO2 < -0.05){      // tolerance of 5%
        float dp_purge = (p_atm + p_buff_upper) * -1 * delta_fiO2 / (_fiO2_est - .21);
        if (dp_purge < (p_buff_upper - p_max_purge)){
            _p_to_purge = p_buff_upper - dp_purge;
        }else{
            _p_to_purge = p_max_purge;
        }
        _t_max_purge = 0.5 * _states_durations.exhale;
        _t_start_purge = millis();
        next_fill_state = FILL_STATES::DECREASE_O2;
    }else{
        _o2_frac_pressure = p_buff_now + (fiO2_desired - 0.21) * (p_buff_upper - p_buff_now) / 0.79; 
        _finished_filling = false;
	    next_fill_state = FILL_STATES::MAINTAIN_O2;
    }    
    return next_fill_state;
}
