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
enum hev_modes : byte
{
    HEV_MODE_PS,
    HEV_MODE_CPAP,
    HEV_MODE_PRVC,
    HEV_MODE_TEST
};

enum valve_states : bool
{
    V_OPEN = HIGH,
    V_CLOSED = LOW
};

static struct struct_valve_port_states 
{ 
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

#endif