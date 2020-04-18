#include "BreathingLoop.h"
#include "common.h"
/*
The Idea of this code is to unfold the FSM in two: one to assign the transitions and the second one to program the states.
*/

BreathingLoop::BreathingLoop()
{

    _fsm_time = millis();
    _timeout = 1000;
    _ventilation_mode = 0;
    _bs_state = BL_STATES::IDLE;
    _running = false;
    _reset = false;
    _next_state;

    init_calib();
}

BreathingLoop::~BreathingLoop()
{
;
}

byte BreathingLoop::getLabCycleMode()
{
    return _ventilation_mode;
}

byte BreathingLoop::getFsmState()
{
    return _bs_state;
}

void BreathingLoop::updatePressures()
{
    delay(10); //placeholder
// TODO
// calc pressure every 1ms
// create averages;
}

//This is used to assign the transitions of the fsm
void BreathingLoop::FSM_assignment( ) {  
    if (millis() > _fsm_time + _timeout ) {
        switch (_bs_state)
        {
        case BL_STATES::IDLE:
            if (_running == true) {
                // FSM_time = millis();
                _next_state = BL_STATES::BUFF_PREFILL;
            } else {
                _next_state = BL_STATES::IDLE;
            }
            _reset = false;
            break;
        case BL_STATES::CALIBRATION:
            _next_state = BL_STATES::BUFF_PREFILL;
            break;
        case BL_STATES::BUFF_PREFILL:
            _next_state = BL_STATES::BUFF_FILL;
            break;
        case BL_STATES::BUFF_FILL:
            _next_state = BL_STATES::BUFF_LOADED;
            break;
        case BL_STATES::BUFF_LOADED:
            switch (_ventilation_mode)
            {
            case LAB_MODE_FLUSH:
                _next_state = BL_STATES::BUFF_FLUSH;
                break;
            case LAB_MODE_PURGE:
                _next_state = BL_STATES::BUFF_PURGE;
                break;
            default:
                _next_state = BL_STATES::BUFF_PRE_INHALE;
            }
            break;
        case BL_STATES::BUFF_PRE_INHALE:
            _next_state = BL_STATES::INHALE;
            break;
        case BL_STATES::INHALE:
            _next_state = BL_STATES::PAUSE;
            break;
        case BL_STATES::PAUSE:
            _next_state = BL_STATES::EXHALE_FILL;
            break;
        case BL_STATES::EXHALE_FILL:
            _next_state = BL_STATES::EXHALE;
            break;
        case BL_STATES::EXHALE:
            if (_running == false) {
                _next_state = BL_STATES::IDLE;
            } else {
                _next_state = BL_STATES::BUFF_LOADED;
            }
            break;
        case BL_STATES::BUFF_PURGE:
            if (_running == false) {
                _next_state = BL_STATES::IDLE;
            } else {
                _next_state = BL_STATES::BUFF_PREFILL;
            }
            break;
        case BL_STATES::BUFF_FLUSH:
            _next_state = BL_STATES::IDLE;
            break;
        case BL_STATES::STOP:
            if (_reset == true) {
                _next_state = BL_STATES::IDLE;
            }
            break;
        default:
            _next_state = _bs_state;
        }
        _bs_state = _next_state;
        _fsm_time = millis();
    }
}

void BreathingLoop::FSM_breath_cycle()
{
    // basic cycle for testing hardware
    // start = digitalRead(pin_button_0);
    switch (_bs_state) {
        case BL_STATES::IDLE:
            
            if (_running == true) {
                // FSM_time = millis();
            } else {
                _timeout = 1000; 
            }
            // TODO
            // air, o2, purge are based on button states in idle
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
            init_calib();
            break;
        case BL_STATES::CALIBRATION : 
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, 0.9 * VALVE_STATE::OPEN, 0.9 * VALVE_STATE::OPEN, VALVE_STATE::OPEN);
            calibrate();
            // TODO
            // do calib - measure P_regulated for 10 s and calc mean
            // P_patient, P_buffer and P_inhale shoudl be equal
            // WHERE do I call getCalibrationOffset()?
            _timeout = 10000;
        case BL_STATES::BUFF_PREFILL:
            // TODO - exhale settable; timeout expert settable
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, 0.8 * VALVE_STATE::OPEN, VALVE_STATE::CLOSED);
            _timeout = 100;
            break;
        case BL_STATES::BUFF_FILL:
            // TODO - exhale settable; timeout settable
            _valves_controller.setValves(VALVE_STATE::OPEN, VALVE_STATE::OPEN, VALVE_STATE::CLOSED, 0.8 * VALVE_STATE::OPEN, VALVE_STATE::CLOSED);
            _timeout = 600;
            break;
        case BL_STATES::BUFF_LOADED:
            // TODO - exhale settable; timeout expert settable
            // Calc pressure and stay in loaded if not ok
            // pressure settable by expert
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, 0.8 * VALVE_STATE::OPEN, VALVE_STATE::CLOSED);
            _timeout = 100;
            break;
        case BL_STATES::BUFF_PRE_INHALE:
            // TODO - timeout settable
            // spontaneous trigger can be enabled
            // - can be triggered by : 
                // P_inhale ; 
                // P_diff_patient //=flow
                // P_patient and p_diff_patient
                // P_patient or p_diff_patient
                // with thresholds on each
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
            switch (_ventilation_mode)
            {
                case LAB_MODE_FLUSH:
                    _timeout = 100;
                    
                    break;
                case LAB_MODE_PURGE:
                    _timeout =500;
                    
                    break;
                default:
                    _timeout = 100;
            }
        
            break;
        case BL_STATES::INHALE:
            // TODO : spontaneous trigger
            // if p_diff_patient < thresh (def: 25% below nominal)
            // go to exhale fill
            // TODO : spontaneous trigger
            // if p_inhale > max thresh pressure(def: 50?)
            // go to exhale fill
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, 0.8*VALVE_STATE::OPEN, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
            _timeout =1000;
            
            break;
        case BL_STATES::PAUSE:
            // TODO: timeout setting
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
            _timeout = 500;
            
            break;
        case BL_STATES::EXHALE_FILL:
            // TODO: timeout setting
            _valves_controller.setValves(VALVE_STATE::OPEN, VALVE_STATE::OPEN, VALVE_STATE::CLOSED, 0.9 * VALVE_STATE::OPEN, VALVE_STATE::CLOSED);
            _timeout = 600;
        
            break;
        case BL_STATES::EXHALE:
            // TODO: exhale timeout based on 
            // (inhale_time* (Exhale/Inhale ratio))  -  fill time
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, 0.9 * VALVE_STATE::OPEN, VALVE_STATE::CLOSED);
            _timeout = 400;
            
            break;
        case BL_STATES::BUFF_PURGE:
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, 0.9 * VALVE_STATE::OPEN, VALVE_STATE::OPEN);
            _timeout =1000;
            break;
        case BL_STATES::BUFF_FLUSH:
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, 0.9 * VALVE_STATE::OPEN, 0.9 * VALVE_STATE::OPEN, VALVE_STATE::CLOSED);
            _timeout =1000;
            break;
        case BL_STATES::STOP: 
            // TODO : require a reset command to go back to idle
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
            _timeout = 1000;
            break;
    }

}

void BreathingLoop::doStart()
{
    _running = true;
}

void BreathingLoop::doStop()
{
    _running = false;
}

void BreathingLoop::doReset()
{
    _reset = true;
}

bool BreathingLoop::getRunning()
{
    return _running;
}

void BreathingLoop::calibrate()
{
    // get pressure_air_regulated over 10s calc mean
    if (_calib_time + _calib_timeout > millis() ){
        _calib_N++;
        _calib_sum_pressure += analogRead(pin_pressure_air_regulated);
        _calib_avg_pressure = _calib_sum_pressure / _calib_N;
    }
}


void BreathingLoop::init_calib()
{

    _calib_timeout = 10;
    _calib_time = millis();
    _calib_sum_pressure = 0;
    _calib_avg_pressure = 0;
    _calib_N = 0;

}

float BreathingLoop::getCalibrationOffset()
{
    return _calib_avg_pressure;
}


ValvesController* BreathingLoop::getValvesController()
{
    return &_valves_controller;
}