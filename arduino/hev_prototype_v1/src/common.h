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


#ifndef COMMON_H
#define COMMON_H
#include <Arduino.h>
#include <limits>
#include "localconf.h"
#include "CommsControl.h"
#include "SystemUtils.h"


#if defined(ARDUINO_FEATHER_ESP32)
#include <huzzah32_pinout.h>
#elif defined(ARDUINO_NodeMCU_32S)
#include <nodemcu_32s_pinout.h>
#elif defined(ARDUINO_SAMD_MKRVIDOR4000)
#include <Arduino_MKR_4000_Vidor_pinout.h>
#elif defined(ARDUINO_SAMD_MKRWIFI1010)
#include <Arduino_MKR_1010_WIFI_pinout.h>
#elif defined(ARDUINO_SAMD_NANO_33_IOT)
#include <Arduino_Nano_33_IOT_pinout.h>
#elif defined(ARDUINO_SAM_DUE)
#include <Arduino_Due_pinout.h>
#endif

#define HEV_FORMAT_VERSION 0xB6

// 
const float MAX_VALVE_FRAC_OPEN = 0.74;
//const uint8_t MAX_PATIENT_PRESSURE = 45; //mbar
const uint8_t RUNNING_AVG_READINGS = 3;
const uint8_t CYCLE_AVG_READINGS = 3;


// input params
enum PAYLOAD_TYPE : uint8_t {
    UNSET        = 0,
    DATA         = 1,
    READBACK     = 2,
    CYCLE        = 3,
    THRESHOLDS   = 4,
    CMD          = 5,
    ALARM        = 6,
    DEBUG        = 7,
    IVT          = 8,
    LOGMSG       = 9,
    TARGET       = 10,
    BATTERY      = 11,
    LOOP_STATUS  = 12,
    PERSONAL     = 13
};

enum CMD_TYPE  : uint8_t {
    GENERAL                =  1,
    SET_DURATION           =  2,
    SET_MODE               =  3,
    SET_THRESHOLD_MIN      =  4,
    SET_THRESHOLD_MAX      =  5,
    SET_VALVE              =  6,
    SET_PID                =  7,
    SET_TARGET_PC_AC       =  8,
    SET_TARGET_PC_AC_PRVC  =  9,
    SET_TARGET_PC_PSV      =  10,
    SET_TARGET_CPAP        =  11,
    SET_TARGET_TEST        =  12,
    SET_TARGET_CURRENT     =  13,
    GET_TARGETS            =  14,
    SET_PERSONAL           =  15,
    GET_THRESHOLD_MIN      =  16,
    GET_THRESHOLD_MAX      =  17
};

enum CMD_GENERAL : uint8_t {
    START        = 1,
    STOP         = 2,
    RESET        = 3,
    STANDBY      = 4,
    GET_PERSONAL = 5
};

// Taken from the FSM doc. Correct as of 1400 on 20200417
enum CMD_SET_DURATION : uint8_t {
    PRE_CALIBRATION =  1,
    CALIBRATION     =  2,
    BUFF_PURGE      =  3,
    BUFF_FLUSH      =  4,
    BUFF_PREFILL    =  5,
    BUFF_FILL       =  6,
    BUFF_PRE_INHALE =  7,
    INHALE          =  8,
    PAUSE           =  9,
    EXHALE          =  10
};

enum VENTILATION_MODE : uint8_t {
    UNKNOWN    = 0,
    PC_AC      = 1,
    PC_AC_PRVC = 2,
    PC_PSV     = 3,
    CPAP       = 4,
    TEST       = 5,
    PURGE      = 6,
    FLUSH      = 7,
    CURRENT    = 100  // not settable
};

enum CMD_SET_VALVE: uint8_t {
    AIR_IN_ENABLE = 1,
    O2_IN_ENABLE  = 2,
    PURGE_ENABLE  = 3,
    INHALE_DUTY_CYCLE = 4,
    INHALE_OPEN_MIN = 5,
    INHALE_OPEN_MAX = 6,
};

enum CMD_SET_PID : uint8_t {
    KP = 1,
    KI = 2,
    KD = 3,
    PID_GAIN = 4,
    TARGET_FINAL_PRESSURE = 5,
    NSTEPS = 6,
    MAX_PATIENT_PRESSURE = 7
};

enum CMD_SET_TARGET : uint8_t {
    INSPIRATORY_PRESSURE     = 1,
    RESPIRATORY_RATE         = 2, 
    IE_RATIO                 = 3,
    VOLUME                   = 4,
    PEEP                     = 5,
    FIO2                     = 6,
    INHALE_TIME              = 7,
    INHALE_TRIGGER_THRESHOLD = 8,
    EXHALE_TRIGGER_THRESHOLD = 9,
    //PID_GAIN                 = 10, 
    // for debugging only; not for UIs
    INHALE_TRIGGER_ENABLE    = 11,
    EXHALE_TRIGGER_ENABLE    = 12,
    VOLUME_TRIGGER_ENABLE    = 13

};

enum CMD_SET_PERSONAL : uint8_t {
    NAME   = 1,
    AGE    = 2,
    SEX    = 3,
    HEIGHT = 4,
    WEIGHT = 5
};

#pragma pack(1)
struct cmd_format {
    uint8_t  version      = HEV_FORMAT_VERSION;
    uint32_t timestamp    = 0;
    uint8_t  payload_type = PAYLOAD_TYPE::CMD;
    uint8_t  cmd_type     = 0;
    uint8_t  cmd_code     = 0;
    float    param        = 0;
};
#pragma pack()


enum ALARM_TYPE: uint8_t {
    ALARM_TYPE_UNKNOWN  =  0,
    PRIORITY_LOW        =  1,
    PRIORITY_MEDIUM     =  2,
    PRIORITY_HIGH       =  3
};

enum ALARM_CODES: uint8_t {
    ALARM_CODE_UNKNOWN             =  0,
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
    ARDUINO_FAIL                   = 25,  // HP

    ALARMS_COUNT                   = 26
};

#pragma pack(1)
struct alarm_format {
    uint8_t  version      = HEV_FORMAT_VERSION;
    uint32_t timestamp    = 0;
    uint8_t  payload_type = PAYLOAD_TYPE::ALARM;
    uint8_t  alarm_type   = 0;
    uint8_t  alarm_code   = 0;
    float    param        = 0;
};
#pragma pack()

// struct for all data sent
#pragma pack(1)
struct fast_data_format {
// fast values - read every ~10 ms
    uint8_t  version                = HEV_FORMAT_VERSION;
    uint32_t timestamp              = 0;
    uint8_t  payload_type           = PAYLOAD_TYPE::DATA;
    uint8_t  fsm_state              = 0; //UNKNOWN
    uint16_t pressure_air_supply    = 0;
    float    pressure_air_regulated = 0.0;
    uint16_t pressure_o2_supply     = 0;
    float    pressure_o2_regulated  = 0.0;
    float    pressure_buffer        = 0.0;
    float    pressure_inhale        = 0.0;
    float    pressure_patient       = 0.0;
    uint16_t temperature_buffer     = 0;
    float    pressure_diff_patient  = 0.0;
    uint16_t ambient_pressure       = 0;
    uint16_t ambient_temperature    = 0;
    float airway_pressure           = 0.0;
    float flow                      = 0.0;
    float flow_calc                 = 0.0;
    float volume                    = 0.0;
    float target_pressure  = 0.0; //
    float process_pressure = 0.0; 
    float valve_duty_cycle = 0.0; 
    float proportional     = 0.0; 
    float integral         = 0.0; //
    float derivative       = 0.0;
};
#pragma pack()

#pragma pack(1)
struct readback_data_format {
// readback values
    uint8_t  version                  = HEV_FORMAT_VERSION;
    uint32_t timestamp                = 0;
    uint8_t  payload_type             = PAYLOAD_TYPE::READBACK;
    uint16_t duration_pre_calibration = 0;
    uint16_t duration_calibration     = 0;
    uint16_t duration_buff_purge      = 0;//
    uint16_t duration_buff_flush      = 0;
    uint16_t duration_buff_prefill    = 0;
    uint16_t duration_buff_fill       = 0;
    uint16_t duration_buff_pre_inhale = 0;//
    uint16_t duration_inhale          = 0;
    uint16_t duration_pause           = 0;
    uint16_t duration_exhale          = 0;

    float    valve_air_in             = 0.0;//
    float    valve_o2_in              = 0.0;
    uint8_t  valve_inhale             = 0;
    uint8_t  valve_exhale             = 0;
    uint8_t  valve_purge              = 0;
    VENTILATION_MODE  ventilation_mode= VENTILATION_MODE::PC_AC;//

    uint8_t valve_inhale_percent      = 0;   // replaced by a min level and a max level; bias inhale level.  very slightly open at "closed" position
    uint8_t valve_exhale_percent      = 0;
    uint8_t valve_air_in_enable       = 0;
    uint8_t valve_o2_in_enable        = 0;
    uint8_t valve_purge_enable        = 0;
    uint8_t inhale_trigger_enable     = 0;   // params - associated val of peak flow
    uint8_t exhale_trigger_enable     = 0;
    float   peep                      = 0.0;//
    float   inhale_exhale_ratio       = 0.0;
    float kp = 0.0;
    float ki = 0.0;
    float kd = 0.0;
    float pid_gain = 0.0;
    uint8_t max_patient_pressure = 0;
};
#pragma pack()

#pragma pack(1)
struct ivt_data_format {
// IVT  values
    uint8_t  version                  = HEV_FORMAT_VERSION;
    uint32_t timestamp                = 0;
    uint8_t  payload_type             = PAYLOAD_TYPE::IVT;
    float inhale_current = 0.0;
    float exhale_current = 0.0;
    float purge_current  = 0.0;
    float air_in_current = 0.0;
    float o2_in_current  = 0.0;
    float inhale_voltage = 0.0;
    float exhale_voltage = 0.0;
    float purge_voltage  = 0.0;
    float air_in_voltage = 0.0;
    float o2_in_voltage  = 0.0;
    uint8_t inhale_i2caddr = 0.0;
    uint8_t exhale_i2caddr = 0.0;
    uint8_t purge_i2caddr  = 0.0;
    uint8_t air_in_i2caddr = 0.0;
    uint8_t o2_in_i2caddr  = 0.0;

    float system_temp    = 0.0;

};
#pragma pack()

#pragma pack(1)
struct cycle_data_format {
// per breath values
    uint8_t  version                    = HEV_FORMAT_VERSION;
    uint32_t timestamp                  = 0;
    uint8_t  payload_type               = PAYLOAD_TYPE::CYCLE;


    float respiratory_rate              = 0.0;

    float tidal_volume                  = 0.0;
    float exhaled_tidal_volume          = 0.0;
    float inhaled_tidal_volume          = 0.0;

    float minute_volume                 = 0.0;
    float exhaled_minute_volume         = 0.0;
    float inhaled_minute_volume         = 0.0;

    float lung_compliance               = 0.0;
    float static_compliance             = 0.0;

    float inhalation_pressure        = 0;  // mean airway pressure
    float peak_inspiratory_pressure  = 0;  
    float plateau_pressure           = 0;  
    float mean_airway_pressure       = 0;

    float fiO2_percent               = 0.0;  // device from Aurelio

    uint16_t apnea_index                = 0;
    uint16_t apnea_time                 = 0;

    uint8_t mandatory_breath            = 0;
};
#pragma pack()

#pragma pack(1)
struct debug_data_format {
// per breath values
    uint8_t  version                    = HEV_FORMAT_VERSION;
    uint32_t timestamp                  = 0;
    uint8_t  payload_type               = PAYLOAD_TYPE::DEBUG;

    float kp = 0.0;
    float ki = 0.0;
    float kd = 0.0;
    float target_pressure  = 0.0; //
    float process_pressure = 0.0; 
    float valve_duty_cycle = 0.0; 
    float proportional     = 0.0; 
    float integral         = 0.0; //
    float derivative       = 0.0;
};
#pragma pack()

#pragma pack(1)
struct status_format {
// per breath values
    uint8_t  version                    = HEV_FORMAT_VERSION;
    uint32_t timestamp                  = 0;
    uint8_t  payload_type               = PAYLOAD_TYPE::LOOP_STATUS;

    float    loop_duration     = 0.0;
    float    loop_duration_max = 0.0;
    uint32_t dropped_send      = 0  ;
    uint32_t dropped_receive   = 0  ;

    uint8_t  buffer_alarm      = 0  ;
    uint8_t  buffer_cmd        = 0  ;
    uint8_t  buffer_data       = 0  ;
};
#pragma pack()

#pragma pack(1)
struct target_data_format{
    uint8_t  version                    = HEV_FORMAT_VERSION;
    uint32_t timestamp                  = 0;
    uint8_t  payload_type               = PAYLOAD_TYPE::TARGET;

    VENTILATION_MODE mode       = VENTILATION_MODE::UNKNOWN ;
    float inspiratory_pressure  = 0.0; // this is also known as driving pressure.  This is pressure above PEEP.  
    float ie_ratio              = 0.0;
    float volume                = 0.0;
    float respiratory_rate      = 0.0;
    float peep                  = 0.0;
    float fiO2_percent          = 0.0; 
    float inhale_time           = 0.0; 
    uint8_t inhale_trigger_enable = 0;   // params - associated val of peak flow
    uint8_t exhale_trigger_enable = 0;
    uint8_t volume_trigger_enable = 0;
    float inhale_trigger_threshold ;   // params - associated val of peak flow
    float exhale_trigger_threshold ;
    float buffer_upper_pressure = 0.0; 
    float buffer_lower_pressure = 0.0; 
    //float pid_gain              = 0; 
};
#pragma pack()

#pragma pack(1)
struct logmsg_data_format {
// per breath values
    uint8_t  version                    = HEV_FORMAT_VERSION;
    uint32_t timestamp                  = 0;
    uint8_t  payload_type               = PAYLOAD_TYPE::LOGMSG;

    char message[50];
};
#pragma pack()

#pragma pack(1)
struct battery_data_format {
// per breath values
    uint8_t  version                    = HEV_FORMAT_VERSION;
    uint32_t timestamp                  = 0;
    uint8_t  payload_type               = PAYLOAD_TYPE::BATTERY;

    uint8_t bat           = 0;
    uint8_t ok            = 0;
    uint8_t alarm         = 0;
    uint8_t rdy2buf       = 0;
    uint8_t process_bat85 = 0;
    uint8_t prob_elec     = 0;
    uint8_t dummy         = 0;
};
#pragma pack()

#pragma pack(1)
struct personal_data_format {
    uint8_t  version                    = HEV_FORMAT_VERSION;
    uint32_t timestamp                  = 0;
    uint8_t  payload_type               = PAYLOAD_TYPE::PERSONAL;

    char    name[60];
    char    patient_id[20];
    uint8_t age;
    char    sex;
    uint8_t height;
    uint8_t weight;  // ideal weight
};
#pragma pack()

struct states_durations {
    uint32_t pre_calibration;
    uint32_t calibration;
    uint32_t buff_purge;
    uint32_t buff_flush;
    uint32_t buff_prefill;
    uint32_t buff_fill;
    uint32_t buff_pre_inhale;
    uint32_t inhale;
    uint32_t pause;
    uint32_t exhale;
};

struct alarms {
    ALARM_TYPE  priorities     [ALARM_CODES::ALARMS_COUNT] = {
        ALARM_TYPE::ALARM_TYPE_UNKNOWN,    // TEMPORARY VALUE DUE TO START FROM 1
        ALARM_TYPE::PRIORITY_HIGH     ,    // APNEA
        ALARM_TYPE::PRIORITY_HIGH     ,    // CHECK_VALVE_EXHALE
        ALARM_TYPE::PRIORITY_HIGH     ,    // CHECK_P_PATIENT
        ALARM_TYPE::PRIORITY_MEDIUM   ,    // EXPIRATION_SENSE_FAULT_OR_LEAK
        ALARM_TYPE::PRIORITY_MEDIUM   ,    // EXPIRATION_VALVE_Leak
        ALARM_TYPE::PRIORITY_MEDIUM   ,    // HIGH_FIO2
        ALARM_TYPE::PRIORITY_HIGH     ,    // HIGH_PRESSURE
        ALARM_TYPE::PRIORITY_MEDIUM   ,    // HIGH_RR
        ALARM_TYPE::PRIORITY_MEDIUM   ,    // HIGH_VTE
        ALARM_TYPE::PRIORITY_MEDIUM   ,    // LOW_VTE
        ALARM_TYPE::PRIORITY_MEDIUM   ,    // HIGH_VTI
        ALARM_TYPE::PRIORITY_MEDIUM   ,    // LOW_VTI
        ALARM_TYPE::PRIORITY_HIGH     ,    // INTENTIONAL_STOP
        ALARM_TYPE::PRIORITY_HIGH     ,    // LOW_BATTERY
        ALARM_TYPE::PRIORITY_HIGH     ,    // LOW_FIO2
        ALARM_TYPE::PRIORITY_HIGH     ,    // OCCLUSION
        ALARM_TYPE::PRIORITY_HIGH     ,    // HIGH_PEEP
        ALARM_TYPE::PRIORITY_HIGH     ,    // LOW_PEEP
        ALARM_TYPE::PRIORITY_MEDIUM   ,    // AC_POWER_DISCONNECTION
        ALARM_TYPE::PRIORITY_MEDIUM   ,    // BATTERY_FAULT_SRVC
        ALARM_TYPE::PRIORITY_MEDIUM   ,    // BATTERY_CHARGE
        ALARM_TYPE::PRIORITY_HIGH     ,    // AIR_FAIL
        ALARM_TYPE::PRIORITY_HIGH     ,    // O2_FAIL
        ALARM_TYPE::PRIORITY_HIGH     ,    // PRESSURE_SENSOR_FAULT
        ALARM_TYPE::PRIORITY_HIGH          // ARDUINO_FAIL
    };
    bool        actives        [ALARM_CODES::ALARMS_COUNT] = {
        false,    // TEMPORARY VALUE DUE TO START FROM 1
        false,    // APNEA
        false,    // CHECK_VALVE_EXHALE
        false,    // CHECK_P_PATIENT
        false,    // EXPIRATION_SENSE_FAULT_OR_LEAK
        false,    // EXPIRATION_VALVE_Leak
        false,    // HIGH_FIO2
        false,    // HIGH_PRESSURE
        false,    // HIGH_RR
        false,    // HIGH_VTE
        false,    // LOW_VTE
        false,    // HIGH_VTI
        false,    // LOW_VTI
        false,    // INTENTIONAL_STOP
        false,    // LOW_BATTERY
        false,    // LOW_FIO2
        false,    // OCCLUSION
        false,    // HIGH_PEEP
        false,    // LOW_PEEP
        false,    // AC_POWER_DISCONNECTION
        false,    // BATTERY_FAULT_SRVC
        false,    // BATTERY_CHARGE
        false,    // AIR_FAIL
        false,    // O2_FAIL
        false,    // PRESSURE_SENSOR_FAULT
        false     // ARDUINO_FAIL
    };
    uint32_t    last_broadcasts[ALARM_CODES::ALARMS_COUNT] = {
        0,    // TEMPORARY VALUE DUE TO START FROM 1
        0,    // APNEA
        0,    // CHECK_VALVE_EXHALE
        0,    // CHECK_P_PATIENT
        0,    // EXPIRATION_SENSE_FAULT_OR_LEAK
        0,    // EXPIRATION_VALVE_Leak
        0,    // HIGH_FIO2
        0,    // HIGH_PRESSURE
        0,    // HIGH_RR
        0,    // HIGH_VTE
        0,    // LOW_VTE
        0,    // HIGH_VTI
        0,    // LOW_VTI
        0,    // INTENTIONAL_STOP
        0,    // LOW_BATTERY
        0,    // LOW_FIO2
        0,    // OCCLUSION
        0,    // HIGH_PEEP
        0,    // LOW_PEEP
        0,    // AC_POWER_DISCONNECTION
        0,    // BATTERY_FAULT_SRVC
        0,    // BATTERY_CHARGE
        0,    // AIR_FAIL
        0,    // O2_FAIL
        0,    // PRESSURE_SENSOR_FAULT
        0     // ARDUINO_FAIL
    };
    float       thresholds_min [ALARM_CODES::ALARMS_COUNT] = {
        std::numeric_limits<float>::lowest(),    // TEMPORARY VALUE DUE TO START FROM 1
        -1,    // APNEA
        -1000,    // CHECK_VALVE_EXHALE
        0,    // CHECK_P_PATIENT
        -1000,    // EXPIRATION_SENSE_FAULT_OR_LEAK
        -1000,    // EXPIRATION_VALVE_Leak
        -1000,    // HIGH_FIO2
        -1000,    // HIGH_PRESSURE
        -1000,    // HIGH_RR
        -1000,    // HIGH_VTE
        300,    // LOW_VTE
        -1000,    // HIGH_VTI
        300,    // LOW_VTI
        -1,    // INTENTIONAL_STOP
        -1.0,    // LOW_BATTERY
        19.5,    // LOW_FIO2  // 19.5 %
        -1000,    // OCCLUSION
        -1000,    // HIGH_PEEP
        0,    // LOW_PEEP
        -1.0,    // AC_POWER_DISCONNECTION
        -1.0,    // BATTERY_FAULT_SRVC
        -1.0,    // BATTERY_CHARGE
        -1000,    // AIR_FAIL
        400,    // O2_FAIL
        -1000,    // PRESSURE_SENSOR_FAULT
        -1000   // ARDUINO_FAIL
    };
    float       thresholds_max [ALARM_CODES::ALARMS_COUNT] = {
        std::numeric_limits<float>::max()   ,    // TEMPORARY VALUE DUE TO START FROM 1
        3,    // APNEA
        1000,    // CHECK_VALVE_EXHALE
        45,    // CHECK_P_PATIENT
        1000,    // EXPIRATION_SENSE_FAULT_OR_LEAK
        1000,    // EXPIRATION_VALVE_Leak
        90.0,    // HIGH_FIO2  // 90%
        45,    // HIGH_PRESSURE
        30,    // HIGH_RR
        700,    // HIGH_VTE
        10000,    // LOW_VTE
        700,    // HIGH_VTI
        10000,  // LOW_VTI 
        1,    // INTENTIONAL_STOP
        0.5,    // LOW_BATTERY
        100,    // LOW_FIO2
        1000,    // OCCLUSION
        15,     // HIGH_PEEP
        -1000,    // LOW_PEEP
        0.5,    // AC_POWER_DISCONNECTION
        0.5,    // BATTERY_FAULT_SRVC
        0.5,    // BATTERY_CHARGE
        10000,    // AIR_FAIL
        650,    // O2_FAIL
        1000   ,    // PRESSURE_SENSOR_FAULT
        1000,      // ARDUINO_FAIL
    };
    float       values         [ALARM_CODES::ALARMS_COUNT];
};

struct pid_variables {
    // input
    float Kp; // proportional factor
    float Ki; // integral factor
    float Kd; // derivative factor
    float pid_gain;
    uint8_t max_patient_pressure;
    // results of calculation
    float target_pressure  ; 
    float process_pressure ; 
    float valve_duty_cycle ; 
    float proportional     ; 
    float integral         ; 
    float derivative       ;
    float previous_process_pressure ;
    float target_final_pressure;
    int nsteps		   ;
    int istep		   ;
};

struct target_variables {
    VENTILATION_MODE mode;
    float inspiratory_pressure; // this is also known as driving pressure.  This is pressure above PEEP.  
    float ie_ratio;
    float volume;
    float respiratory_rate;
    float peep;
    float fiO2_percent; 
    uint16_t inhale_time; 
    bool  inhale_trigger_enable ;   // params - associated val of peak flow
    bool  exhale_trigger_enable ;
    bool  volume_trigger_enable ;
    float inhale_trigger_threshold ;   // params - associated val of peak flow
    float exhale_trigger_threshold ;
    float buffer_upper_pressure; 
    float buffer_lower_pressure; 
    /*float pid_gain;  //ms*/
    bool  ie_selected;
};

template <typename T>
void setAlarm(ALARM_CODES alarm_code, T *alarms, T value) { alarms[alarm_code] = value; }



// used for calculating averages, template due to different size for sums and averages
template <typename T> struct readings{
    uint32_t timestamp       = 0; //
    T pressure_air_supply    = 0;
    T pressure_air_regulated = 0;
    T pressure_buffer        = 0;
    T pressure_inhale        = 0;
    T pressure_patient       = 0;
    T temperature_buffer     = 0;
    T pressure_o2_supply     = 0;
    T pressure_o2_regulated  = 0;
    T pressure_diff_patient  = 0;
    T o2_percent             = 0;
};

template <typename T> struct calculations {
    uint32_t timestamp  = 0;
    T flow              = 0;
    T flow_calc         = 0;
    T volume            = 0;

    T pressure_airway   = 0;
};

template <typename T> struct IV_readings{
    uint64_t timestamp       = 0; //
    T inhale_current = 0;
    T exhale_current = 0;
    T purge_current  = 0;
    T air_in_current = 0;
    T o2_in_current  = 0;
    T inhale_voltage = 0;
    T exhale_voltage = 0;
    T purge_voltage  = 0;
    T air_in_voltage = 0;
    T o2_in_voltage  = 0;
    uint8_t inhale_i2caddr = 0;
    uint8_t exhale_i2caddr = 0;
    uint8_t purge_i2caddr  = 0;
    uint8_t air_in_i2caddr = 0;
    uint8_t o2_in_i2caddr  = 0;
};

struct valve_params{
    bool valve_air_in_enable   ;
    bool valve_o2_in_enable    ;
    bool valve_purge_enable    ;
    float inhale_duty_cycle;
    float inhale_open_min;
    float inhale_open_max;

};

struct cycle_readings{

    uint64_t timestamp       = 0; 
    float respiratory_rate              = 0.0;

    float tidal_volume                  = 0.0;
    float exhaled_tidal_volume          = 0.0;
    float inhaled_tidal_volume          = 0.0;

    float minute_volume                 = 0.0;
    float exhaled_minute_volume         = 0.0;
    float inhaled_minute_volume         = 0.0;

    float lung_compliance               = 0.0;
    float static_compliance             = 0.0;

    float inhalation_pressure        = 0;  
    float peak_inspiratory_pressure  = 0;  
    float plateau_pressure           = 0;  
    float mean_airway_pressure       = 0;

    float fiO2_percent               = 0;  

    uint16_t apnea_index                = 0;
    uint16_t apnea_time                 = 0;

    uint8_t mandatory_breath            = 0;

};

struct personal_details{
    char name[60];
    char patient_id[20];
    uint8_t age;
    char    sex;
    uint8_t height;
    uint8_t weight;  // ideal weight
};

//void setThreshold(ALARM_CODES alarm, alarm_thresholds &thresholds, uint32_t &value);
void setDuration(CMD_SET_DURATION cmd, states_durations &timeouts, float value);
void setValveParam(CMD_SET_VALVE cmd, valve_params &vparams, float value);
void setPID(CMD_SET_PID cmd, pid_variables &pid, float value);
void setTarget(CMD_SET_TARGET cmd, target_variables &targets,  float value);
int16_t adcToMillibar(int16_t adc, int16_t offset = 0);
float adcToMillibarFloat(float adc, float offset = 0);
float adcToO2PercentFloat(float adc, float offset = 0);
float adcToMillibarDPFloat(float adc, float offset = 1500);
void logMsg(String s);
CommsControl* getGlobalComms();
void setGlobalComms(CommsControl *comms);
SystemUtils* getSystemUtils();
void setSystemUtils(SystemUtils *sys_utils);


#endif
