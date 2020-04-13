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
                // Serial.println("Exit IDLE") ;
            } else {
                next_state = BS_IDLE;
            }
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
            setValves(V_CLOSED, V_CLOSED, V_OPEN, V_OPEN, V_CLOSED, V_CLOSED);
            break;
        case BS_BUFF_PREFILL:
            setValves(V_CLOSED, V_CLOSED, V_CLOSED, V_OPEN, V_CLOSED, V_CLOSED);
            timeout = 100;
            break;
        case BS_BUFF_FILL:
            setValves(V_OPEN, V_OPEN, V_CLOSED, V_OPEN, V_CLOSED, V_CLOSED);
            timeout = 1200;
            break;
        case BS_BUFF_LOADED:
            setValves(V_CLOSED, V_CLOSED, V_CLOSED, V_OPEN, V_CLOSED, V_CLOSED);
            switch (lab_cycle_mode)
            {
                case LAB_MODE_FLUSH:
                    timeout = 100;
                    
                    break;
                case LAB_MODE_PURGE:
                    timeout =500;
                    
                    break;
                default:
                    timeout =1500;
            }
            break;
        case BS_BUFF_PRE_INHALE:
            setValves(V_CLOSED, V_CLOSED, V_CLOSED, V_CLOSED, V_CLOSED, V_CLOSED);
            timeout = 100;
        
            break;
        case BS_INHALE:
            setValves(V_CLOSED, V_CLOSED, V_OPEN, V_CLOSED, V_CLOSED, V_CLOSED);
            timeout =1600;
            
            break;
        case BS_PAUSE:
            setValves(V_CLOSED, V_CLOSED, V_CLOSED, V_CLOSED, V_CLOSED, V_CLOSED);
            timeout = 200;
            
            break;
        case BS_EXHALE_FILL:
            setValves(V_OPEN, V_OPEN, V_CLOSED, V_OPEN, V_CLOSED, V_CLOSED);
            timeout =1200;
        
            break;
        case BS_EXHALE:
            setValves(V_CLOSED, V_CLOSED, V_CLOSED, V_OPEN, V_CLOSED, V_CLOSED);
            timeout = 400;
            
            break;
        case BS_BUFF_PURGE:
            setValves(V_CLOSED, V_CLOSED, V_CLOSED, V_OPEN, V_OPEN, V_CLOSED);
            timeout =1000;
            break;
        case BS_BUFF_FLUSH:
            setValves(V_CLOSED, V_CLOSED, V_OPEN, V_OPEN, V_CLOSED, V_CLOSED);
            timeout =1000;
            break;
    }

//  Serial.println("state FSM_breath_cycle: " + String(bs_state));
//  Serial.println("start: " + String(start));
}

void do_start()
{
    running = true;
}

void do_stop()
{
    running = false;
}

bool get_running()
{
    return running;
}