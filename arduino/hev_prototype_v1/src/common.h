#ifndef COMMON_H
#define COMMON_H
#include <Arduino.h>

#define HEV_MINI_SYSTEM  // uncomment this if using lab 14-1-014

#if defined(ARDUINO_FEATHER_ESP32)
#include <huzzah32_pinout.h>
#elif defined(ARDUINO_NodeMCU_32S)
#include <nodemcu_32s_pinout.h>
#elif defined(ARDUINO_AVR_UNO)
#ifdef HEV_MINI_SYSTEM
#include <Arduino_uno_pinout_minisystem.h>
#else
#include <Arduino_uno_pinout.h>
#endif
#elif defined(ARDUINO_SAMD_MKRVIDOR4000)
#include <Arduino_MKR_4000_Vidor_pinout.h>
#elif defined(ARDUINO_SAMD_MKRWIFI1010)
#include <Arduino_MKR_1010_WIFI_pinout.h>
#elif defined(ARDUINO_SAMD_NANO_33_IOT)
#include <Arduino_Nano_33_IOT_pinout.h>
#elif defined(ARDUINO_SAM_DUE)
#include <Arduino_Due_pinout.h>
#elif defined(ARDUINO_AVR_YUN)
#include <Arduino_Yun_pinout.h>
#endif

// input params
enum CMD_TYPE  : uint8_t {
    GENERAL           =  1,
    SET_TIMEOUT       =  2,
    SET_MODE          =  3,
    SET_THRESHOLD_MIN =  4,
    SET_THRESHOLD_MAX =  5
};

enum CMD_GENERAL : uint8_t {
    START =  1,
    STOP  =  2,
    PURGE =  3,
    FLUSH =  4
};

// Taken from the FSM doc. Correct as of 1400 on 20200417
enum CMD_SET_TIMEOUT : uint8_t {
    CALIBRATION     =  1,
    BUFF_PURGE      =  2,
    BUFF_FLUSH      =  3,
    BUFF_PREFILL    =  4,
    BUFF_FILL       =  5,
    BUFF_LOADED     =  6,
    BUFF_PRE_INHALE =  7,
    INHALE          =  8,
    PAUSE           =  9,
    EXHALE_FILL     = 10,
    EXHALE          = 11
};

enum CMD_SET_MODE : uint8_t {
    HEV_MODE_PS,
    HEV_MODE_CPAP,
    HEV_MODE_PRVC,
    HEV_MODE_TEST
};

enum ALARM_TYPE: uint8_t {
    LP   = 1,
    MP   = 2,
    HP   = 3
};

enum ALARM_CODES: uint8_t {
    APNEA                          =  1,  // HP
    CHECK_VALVE_EXHALE             =  2,  // HP
    CHECK_P_PATIENT                =  3,  // HP
    EXPIRATION_SENSE_FAULT_OR_LEAK =  4,  //   MP
    EXPIRATION_VALVE_Leak          =  5,  //   MP
    HIGH_FIO2                      =  6,  //   MP
    HIGH_PRESSURE                  =  7,  // HP
    HIGH_RR                        =  8,  //   MP
    HIGH_VTE                       =  9,  //   MP
    LOW_VTE                        = 10,  //   MP
    HIGH_VTI                       = 11,  //   MP
    LOW_VTI                        = 12,  //   MP
    INTENTIONAL_STOP               = 13,  // HP
    LOW_BATTERY                    = 14,  // HP (LP) if AC power isn't (is) connected
    LOW_FIO2                       = 15,  // HP
    OCCLUSION                      = 16,  // HP
    HIGH_PEEP                      = 17,  // HP
    LOW_PEEP                       = 18,  // HP
    AC_POWER_DISCONNECTION         = 19,  //   MP
    BATTERY_FAULT_SRVC             = 20,  //   MP
    BATTERY_CHARGE                 = 21,  //   MP
    AIR_FAIL                       = 22,  // HP
    O2_FAIL                        = 23,  // HP
    PRESSURE_SENSOR_FAULT          = 24,  // HP
    ARDUINO_FAIL                   = 25   // HP
};

enum VALVE_STATES : bool {
    V_OPEN = HIGH,
    V_CLOSED = LOW
};

struct fsm_timeouts {
    uint32_t calibration;
    uint32_t buff_purge;
    uint32_t buff_flush;
    uint32_t buff_prefill;
    uint32_t buff_fill;
    uint32_t buff_loaded;
    uint32_t buff_pre_inhale;
    uint32_t inhale;
    uint32_t pause;
    uint32_t exhale_fill;
    uint32_t exhale; // has to be calculated using function getTimeoutExhale()
};

struct alarm_thresholds {
    uint32_t apnea;
    uint32_t check_valve_exhale;
    uint32_t check_p_patient;
    uint32_t expiration_sense_fault_or_leak;
    uint32_t expiration_valve_leak;
    uint32_t high_fio2;
    uint32_t high_pressure;
    uint32_t high_rr;
    uint32_t high_vte;
    uint32_t low_vte;
    uint32_t high_vti;
    uint32_t low_vti;
    uint32_t intentional_stop;
    uint32_t low_battery;
    uint32_t low_fio2;
    uint32_t occlusion;
    uint32_t high_peep;
    uint32_t low_peep;
    uint32_t ac_power_disconnection;
    uint32_t battery_fault_srvc;
    uint32_t battery_charge;
    uint32_t air_fail;
    uint32_t o2_fail;
    uint32_t pressure_sensor_fault;
    uint32_t arduino_fail;
};

// default values definitions
static fsm_timeouts     fsm_timeout = {10000, 600, 600, 100, 600, 100, 100, 1000, 500, 600, 400};
static alarm_thresholds alarm_threshold_min;
static alarm_thresholds alarm_threshold_max;

static struct struct_valve_port_states {
    // bools are used for valves that are digitally controlled - i.e. only on or off.
    bool air_in;
    bool o2_in;
    float inhale;
    float exhale;
    bool purge;
    bool atmos;
} valve_port_states;

// static uint32_t valve_port_states = 0x0; 
static int pin_to_chan[50];  // too lazy to create a proper hashmap for 2 variables; 50 pins is probably fine
static int chan_to_pin[50];  

void setValves(bool vin_air, bool vin_o2, float vinhale, 
               float vexhale, bool vpurge, bool vatmos);
void getValves(bool &vin_air, bool &vin_o2, float &vinhale,  
               float &vexhale, bool &vpurge, bool &vatmos);

void setThreshold(ALARM_CODES alarm, alarm_thresholds &thresholds, uint32_t value);
void setTimeout(CMD_SET_TIMEOUT cmd, fsm_timeouts &timeouts, uint32_t value);
uint32_t getTimeoutExhale();

#endif
