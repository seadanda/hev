#include "test_hw_loop.h"
#include "common.h"
/*
The Idea of this code is to unfold the FSM in two: one to assign the transitions and the second one to program the states.
*/
uint64_t FSM_time = millis();
int timeout = 1000;
byte lab_cycle_mode = 0;
byte bs_state = BS_IDLE;
bool running = false;
bool reset = false;
int next_state;

byte getLabCycleMode()
{
    return lab_cycle_mode;
}

byte getFsmState()
{
    return bs_state;
}

//This is used to assign the transitions of the fsm
void FSM_assignment( ) {  
    if (millis() > FSM_time + timeout ) {
        switch (bs_state)
        {
        case BS_IDLE:
            if (running == true) {
                // FSM_time = millis();
                next_state = BS_BUFF_PREFILL;
            } else {
                next_state = BS_IDLE;
            }
            reset = false;
            break;
        case BS_CALIBRATION:
            next_state = BS_BUFF_PREFILL;
            break;
        case BS_BUFF_PREFILL:
            next_state = BS_BUFF_FILL;
            break;
        case BS_BUFF_FILL:
            next_state = BS_BUFF_LOADED;
            break;
        case BS_BUFF_LOADED:
            switch (lab_cycle_mode)
            {
            case LAB_MODE_FLUSH:
                next_state = BS_BUFF_FLUSH;
                break;
            case LAB_MODE_PURGE:
                next_state = BS_BUFF_PURGE;
                break;
            default:
                next_state = BS_BUFF_PRE_INHALE;
            }
            break;
        case BS_BUFF_PRE_INHALE:
            next_state = BS_INHALE;
            break;
        case BS_INHALE:
            next_state = BS_PAUSE;
            break;
        case BS_PAUSE:
            next_state = BS_EXHALE_FILL;
            break;
        case BS_EXHALE_FILL:
            next_state = BS_EXHALE;
            break;
        case BS_EXHALE:
            if (running == false) {
                next_state = BS_IDLE;
            } else {
                next_state = BS_BUFF_LOADED;
            }
            break;
        case BS_BUFF_PURGE:
            if (running == false) {
                next_state = BS_IDLE;
            } else {
                next_state = BS_BUFF_PREFILL;
            }
            break;
        case BS_BUFF_FLUSH:
            next_state = BS_IDLE;
            break;
        case BS_STOP:
            if (reset == true) {
                next_state = BS_IDLE;
            }
            break;
        default:
            next_state = bs_state;
        }
        bs_state = next_state;
        FSM_time = millis();
    }
}

void FSM_breath_cycle()
{
    // basic cycle for testing hardware
    // start = digitalRead(pin_button_0);
    switch (bs_state) {
        case BS_IDLE:
            
            if (running == true) {
                // FSM_time = millis();
            } else {
                timeout = 1000; 
            }
            // TODO
            // air, o2, purge are based on button states in idle
            setValves(V_CLOSED, V_CLOSED, 0.0, 0.0, V_CLOSED, V_CLOSED);
            break;
        case BS_CALIBRATION : 
            setValves(V_CLOSED, V_CLOSED, 0.9, 0.9, V_OPEN, V_CLOSED);
            // TODO
            // do calib - measure P_regulated for 10 s and calc mean
            // P_patient, P_buffer and P_inhale shoudl be equal
            timeout = 10000;
        case BS_BUFF_PREFILL:
            // TODO - exhale settable; timeout expert settable
            setValves(V_CLOSED, V_CLOSED, 0.0, 0.8, V_CLOSED, V_CLOSED);
            timeout = 100;
            break;
        case BS_BUFF_FILL:
            // TODO - exhale settable; timeout settable
            setValves(V_OPEN, V_OPEN, 0.0, 0.8, V_CLOSED, V_CLOSED);
            timeout = 600;
            break;
        case BS_BUFF_LOADED:
            // TODO - exhale settable; timeout expert settable
            // Calc pressure and stay in loaded if not ok
            // pressure settable by expert
            setValves(V_CLOSED, V_CLOSED, 0.0, 0.8, V_CLOSED, V_CLOSED);
            timeout = 100;
            break;
        case BS_BUFF_PRE_INHALE:
            // TODO - timeout settable
            // spontaneous trigger can be enabled
            // - can be triggered by : 
                // P_inhale ; 
                // P_diff_patient //=flow
                // P_patient and p_diff_patient
                // P_patient or p_diff_patient
                // with thresholds on each
            setValves(V_CLOSED, V_CLOSED, 0.0, 0.0, V_CLOSED, V_CLOSED);
            switch (lab_cycle_mode)
            {
                case LAB_MODE_FLUSH:
                    timeout = 100;
                    
                    break;
                case LAB_MODE_PURGE:
                    timeout =500;
                    
                    break;
                default:
                    timeout = 100;
            }
        
            break;
        case BS_INHALE:
            // TODO : spontaneous trigger
            // if p_diff_patient < thresh (def: 25% below nominal)
            // go to exhale fill
            // TODO : spontaneous trigger
            // if p_inhale > max thresh pressure(def: 50?)
            // go to exhale fill
            setValves(V_CLOSED, V_CLOSED, 0.8, 0.0, V_CLOSED, V_CLOSED);
            timeout =1000;
            
            break;
        case BS_PAUSE:
            // TODO: timeout setting
            setValves(V_CLOSED, V_CLOSED, 0.0, 0.0, V_CLOSED, V_CLOSED);
            timeout = 500;
            
            break;
        case BS_EXHALE_FILL:
            setValves(V_OPEN, V_OPEN, V_CLOSED, V_OPEN, V_CLOSED, V_CLOSED);
            timeout =1200;
        
            break;
        case BS_EXHALE:
            // TODO: exhale timeout based on 
            // (inhale_time* (Exhale/Inhale ratio))  -  fill time
            setValves(V_CLOSED, V_CLOSED, 0.0, 0.9, V_CLOSED, V_CLOSED);
            timeout = 400;
            
            break;
        case BS_BUFF_PURGE:
            setValves(V_CLOSED, V_CLOSED, 0.0, 0.9, V_OPEN, V_CLOSED);
            timeout =1000;
            break;
        case BS_BUFF_FLUSH:
            setValves(V_CLOSED, V_CLOSED, 0.9, 0.9, V_CLOSED, V_CLOSED);
            timeout =1000;
            break;
        case BS_STOP: 
            // TODO : require a reset command to go back to idle
            setValves(V_CLOSED, V_CLOSED, 0.0, 0.0, V_CLOSED, V_CLOSED);
            timeout = 1000;
            break;
    }

}

void do_start()
{
    running = true;
}

void do_stop()
{
    running = false;
}

void do_reset()
{
    reset = true;
}

bool get_running()
{
    return running;
}