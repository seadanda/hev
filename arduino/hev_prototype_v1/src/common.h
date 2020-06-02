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

#define HEV_FORMAT_VERSION 0xAC

// 
const float MAX_VALVE_FRAC_OPEN = 0.74;
const uint8_t MAX_PATIENT_PRESSURE = 45; //mbar
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
    BATTERY      = 11
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
    GET_TARGETS            =  14
};

enum CMD_GENERAL : uint8_t {
    START =  1,
    STOP  =  2,
    RESET =  3,
    STANDBY = 4
};

// Taken from the FSM doc. Correct as of 1400 on 20200417
enum CMD_SET_DURATION : uint8_t {
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
    INHALE_TRIGGER_ENABLE = 7,
    EXHALE_TRIGGER_ENABLE = 8,
    INHALE_TRIGGER_THRESHOLD = 9,
    EXHALE_TRIGGER_THRESHOLD = 10
};

enum CMD_SET_PID : uint8_t {
    KP = 1,
    KI = 2,
    KD = 3,
    TARGET_FINAL_PRESSURE = 4,
    NSTEPS = 5
};

enum CMD_SET_TARGET : uint8_t {
    INSPIRATORY_PRESSURE = 1,
    RESPIRATORY_RATE     = 2, 
    IE_RATIO             = 3,
    VOLUME               = 4,
    PEEP                 = 5,
    FIO2                 = 6,
    INHALE_TIME          = 7
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
    float volume                    = 0.0;
};
#pragma pack()

#pragma pack(1)
struct readback_data_format {
// readback values
    uint8_t  version                  = HEV_FORMAT_VERSION;
    uint32_t timestamp                = 0;
    uint8_t  payload_type             = PAYLOAD_TYPE::READBACK;
    uint16_t duration_calibration     = 0;
    uint16_t duration_buff_purge      = 0;//
    uint16_t duration_buff_flush      = 0;
    uint16_t duration_buff_prefill    = 0;
    uint16_t duration_buff_fill       = 0;
    uint16_t duration_buff_loaded     = 0;
    uint16_t duration_buff_pre_inhale = 0;//
    uint16_t duration_inhale          = 0;
    uint16_t duration_pause           = 0;
    uint16_t duration_exhale_fill     = 0;
    uint16_t duration_exhale          = 0;

    float    valve_air_in             = 0.0;//
    float    valve_o2_in              = 0.0;
    uint8_t  valve_inhale             = 0;
    uint8_t  valve_exhale             = 0;
    uint8_t  valve_purge              = 0;
    uint8_t  ventilation_mode         = VENTILATION_MODE::PC_AC;//

    uint8_t valve_inhale_percent      = 0;   // replaced by a min level and a max level; bias inhale level.  very slightly open at "closed" position
    uint8_t valve_exhale_percent      = 0;
    uint8_t valve_air_in_enable       = 0;
    uint8_t valve_o2_in_enable        = 0;
    uint8_t valve_purge_enable        = 0;
    uint8_t inhale_trigger_enable     = 0;   // params - associated val of peak flow
    uint8_t exhale_trigger_enable     = 0;
    float   peep                      = 0.0;//
    float   inhale_exhale_ratio       = 0.0;
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
struct target_data_format{
    uint8_t  version                    = HEV_FORMAT_VERSION;
    uint32_t timestamp                  = 0;
    uint8_t  payload_type               = PAYLOAD_TYPE::TARGET;

    uint8_t mode                = 0 ;
    float inspiratory_pressure  = 0.0; // this is also known as driving pressure.  This is pressure above PEEP.  
    float ie_ratio              = 0.0;
    float volume                = 0.0;
    float respiratory_rate      = 0.0;
    float peep                  = 0.0;
    float fiO2                  = 0.0; 
    uint16_t inhale_time        = 0 ; 
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

    uint8_t bat           = 0.0;
    uint8_t ok            = 0.0;
    uint8_t alarm         = 0.0;
    uint8_t rdy2buf       = 0.0;
    uint8_t process_bat85 = 0.0;
    uint8_t prob_elec     = 0.0;
    uint8_t dummy         = 0.0;
};
#pragma pack()
//enum VALVE_STATES : bool {
//    V_OPEN = HIGH,
//    V_CLOSED = LOW
//};

struct states_durations {
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
        std::numeric_limits<float>::lowest(),    // APNEA
        std::numeric_limits<float>::lowest(),    // CHECK_VALVE_EXHALE
        std::numeric_limits<float>::lowest(),    // CHECK_P_PATIENT
        std::numeric_limits<float>::lowest(),    // EXPIRATION_SENSE_FAULT_OR_LEAK
        std::numeric_limits<float>::lowest(),    // EXPIRATION_VALVE_Leak
        std::numeric_limits<float>::lowest(),    // HIGH_FIO2
        std::numeric_limits<float>::lowest(),    // HIGH_PRESSURE
        std::numeric_limits<float>::lowest(),    // HIGH_RR
        std::numeric_limits<float>::lowest(),    // HIGH_VTE
        std::numeric_limits<float>::lowest(),    // LOW_VTE
        std::numeric_limits<float>::lowest(),    // HIGH_VTI
        std::numeric_limits<float>::lowest(),    // LOW_VTI
        std::numeric_limits<float>::lowest(),    // INTENTIONAL_STOP
        std::numeric_limits<float>::lowest(),    // LOW_BATTERY
        std::numeric_limits<float>::lowest(),    // LOW_FIO2
        std::numeric_limits<float>::lowest(),    // OCCLUSION
        std::numeric_limits<float>::lowest(),    // HIGH_PEEP
        std::numeric_limits<float>::lowest(),    // LOW_PEEP
        std::numeric_limits<float>::lowest(),    // AC_POWER_DISCONNECTION
        std::numeric_limits<float>::lowest(),    // BATTERY_FAULT_SRVC
        std::numeric_limits<float>::lowest(),    // BATTERY_CHARGE
        std::numeric_limits<float>::lowest(),    // AIR_FAIL
        std::numeric_limits<float>::lowest(),    // O2_FAIL
        std::numeric_limits<float>::lowest(),    // PRESSURE_SENSOR_FAULT
        std::numeric_limits<float>::lowest()     // ARDUINO_FAIL
    };
    float       thresholds_max [ALARM_CODES::ALARMS_COUNT] = {
        std::numeric_limits<float>::max()   ,    // TEMPORARY VALUE DUE TO START FROM 1
        std::numeric_limits<float>::max()   ,    // APNEA
        std::numeric_limits<float>::max()   ,    // CHECK_VALVE_EXHALE
        std::numeric_limits<float>::max()   ,    // CHECK_P_PATIENT
        std::numeric_limits<float>::max()   ,    // EXPIRATION_SENSE_FAULT_OR_LEAK
        std::numeric_limits<float>::max()   ,    // EXPIRATION_VALVE_Leak
        std::numeric_limits<float>::max()   ,    // HIGH_FIO2
        std::numeric_limits<float>::max()   ,    // HIGH_PRESSURE
        std::numeric_limits<float>::max()   ,    // HIGH_RR
        std::numeric_limits<float>::max()   ,    // HIGH_VTE
        std::numeric_limits<float>::max()   ,    // LOW_VTE
        std::numeric_limits<float>::max()   ,    // HIGH_VTI
        std::numeric_limits<float>::max()   ,    // LOW_VTI
        std::numeric_limits<float>::max()   ,    // INTENTIONAL_STOP
        std::numeric_limits<float>::max()   ,    // LOW_BATTERY
        std::numeric_limits<float>::max()   ,    // LOW_FIO2
        std::numeric_limits<float>::max()   ,    // OCCLUSION
        std::numeric_limits<float>::max()   ,    // HIGH_PEEP
        std::numeric_limits<float>::max()   ,    // LOW_PEEP
        std::numeric_limits<float>::max()   ,    // AC_POWER_DISCONNECTION
        std::numeric_limits<float>::max()   ,    // BATTERY_FAULT_SRVC
        std::numeric_limits<float>::max()   ,    // BATTERY_CHARGE
        std::numeric_limits<float>::max()   ,    // AIR_FAIL
        std::numeric_limits<float>::max()   ,    // O2_FAIL
        std::numeric_limits<float>::max()   ,    // PRESSURE_SENSOR_FAULT
        std::numeric_limits<float>::max()        // ARDUINO_FAIL
    };
    float       values         [ALARM_CODES::ALARMS_COUNT];
};

struct pid_variables {
    // input
    float Kp; // proportional factor
    float Ki; // integral factor
    float Kd; // derivative factor
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
    uint8_t mode;
    float inspiratory_pressure; // this is also known as driving pressure.  This is pressure above PEEP.  
    float ie_ratio;
    float volume;
    float respiratory_rate;
    float peep;
    float fiO2; 
    uint16_t inhale_time; 
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
    bool inhale_trigger_enable ;   // params - associated val of peak flow
    bool exhale_trigger_enable ;
    float inhale_duty_cycle;
    float inhale_open_min;
    float inhale_open_max;
    float inhale_trigger_threshold ;   // params - associated val of peak flow
    float exhale_trigger_threshold ;

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
