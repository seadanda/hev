#include <Arduino.h>

byte getLabCycleMode();
byte getFsmState();
void FSM_assignment();
void FSM_breath_cycle();
void do_start();
void do_stop();
bool get_running();

// states
enum BS_STATES : byte
{
    BS_IDLE,
    BS_BUFF_PREFILL,
    BS_BUFF_FILL,
    BS_BUFF_LOADED,
    BS_BUFF_PRE_INHALE,
    BS_INHALE,
    BS_PAUSE,
    BS_EXHALE_FILL,
    BS_EXHALE,
    BS_BUFF_PURGE,
    BS_BUFF_FLUSH
};


enum lab_cycle_modes : byte
{
    LAB_MODE_BREATHE = 0,
    LAB_MODE_PURGE = 1,
    LAB_MODE_FLUSH = 2
};

