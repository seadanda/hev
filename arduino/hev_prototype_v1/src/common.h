#ifndef COMMON_H
#define COMMON_H
#include <Arduino.h>

//#define HEV_MINI_SYSTEM  // uncomment this if using lab 14-1-014

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

// 
const float MAX_VALVE_FRAC_OPEN = 0.68;
// input params
enum hev_modes : byte
{
    HEV_MODE_PS,
    HEV_MODE_CPAP,
    HEV_MODE_PRVC,
    HEV_MODE_TEST
};



#endif