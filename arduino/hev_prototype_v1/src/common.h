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

#define HEV_FORMAT_VERSION 0xA2

// 
const float MAX_VALVE_FRAC_OPEN = 0.68;
// input params
enum CMD_TYPE  : uint8_t {
    GENERAL           =  1,
    SET_DURATION      =  2,
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

enum CMD_SET_MODE : uint8_t {
    HEV_MODE_PS,
    HEV_MODE_CPAP,
    HEV_MODE_PRVC,
    HEV_MODE_TEST
};

#pragma pack(1)
struct cmd_format {
    uint8_t  version   = HEV_FORMAT_VERSION;
    uint32_t timestamp = 0;
    uint8_t  cmd_type  = 0;
    uint8_t  cmd_code  = 0;
    uint32_t param     = 0;
};
#pragma pack()


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

#pragma pack(1)
struct alarm_format {
    uint8_t  version    = HEV_FORMAT_VERSION;
    uint32_t timestamp  = 0;
    uint8_t  alarm_type = 0;
    uint8_t  alarm_code = 0;
    uint32_t param      = 0;
};
#pragma pack()

enum DATA_TYPE: uint8_t  {
    FAST       =  1,
    READBACK   =  2,
    CYCLE      =  3,
    THRESHOLDS =  4
};

// struct for all data sent
#pragma pack(1)
struct fast_data_format {
// fast values - read every ~10 ms
    uint8_t  version                = HEV_FORMAT_VERSION;
    uint32_t timestamp              = 0;
    uint8_t  data_type              = DATA_TYPE::FAST;
    uint8_t  fsm_state              = 0;
    uint16_t pressure_air_supply    = 0;
    uint16_t pressure_air_regulated = 0;
    uint16_t pressure_o2_supply     = 0;
    uint16_t pressure_o2_regulated  = 0;
    uint16_t pressure_buffer        = 0;
    uint16_t pressure_inhale        = 0;
    uint16_t pressure_patient       = 0;
    uint16_t temperature_buffer     = 0;
    uint16_t pressure_diff_patient  = 0;
    uint16_t ambient_pressure       = 0;
    uint16_t ambient_temperature    = 0;
    float airway_pressure           = 0;
    float flow                      = 0;
    float volume                    = 0;
};
#pragma pack()

#pragma pack(1)
struct readback_data_format {
// readback values
    uint8_t  version                  = HEV_FORMAT_VERSION;
    uint32_t timestamp                = 0;
    uint8_t  data_type                = DATA_TYPE::READBACK;
    uint16_t duration_calibration     = 0;
    uint16_t duration_buff_purge      = 0;
    uint16_t duration_buff_flush      = 0;
    uint16_t duration_buff_prefill    = 0;
    uint16_t duration_buff_fill       = 0;
    uint16_t duration_buff_loaded     = 0;
    uint16_t duration_buff_pre_inhale = 0;
    uint16_t duration_inhale          = 0;
    uint16_t duration_pause           = 0;
    uint16_t duration_exhale_fill     = 0;
    uint16_t duration_exhale          = 0;

    uint8_t  valve_air_in             = 0;
    uint8_t  valve_o2_in              = 0;
    uint8_t  valve_inhale             = 0;
    uint8_t  valve_exhale             = 0;
    uint8_t  valve_purge              = 0;
    uint8_t  ventilation_mode         = 0;

    uint8_t valve_inhale_percent      = 0;
    uint8_t valve_exhale_percent      = 0;
    uint8_t valve_air_in_enable       = 0;
    uint8_t valve_o2_in_enable        = 0;
    uint8_t valve_purge_enable        = 0;
    uint8_t inhale_trigger_enable     = 0;
    uint8_t exhale_trigger_enable     = 0;
    uint8_t peep                      = 0;
    float   inhale_exhate_ratio       = 0.0;
};
#pragma pack()

#pragma pack(1)
struct cycle_data_format {
// per breath values
    uint8_t  version                    = HEV_FORMAT_VERSION;
    uint32_t timestamp                  = 0;
    uint8_t  data_type                  = DATA_TYPE::CYCLE;

    float respiratory_rate              = 0;

    float tidal_volume                  = 0;
    float exhaled_tidal_volume          = 0;
    float inhaled_tidal_volume          = 0;

    float minute_volume                 = 0;
    float exhaled_minute_volume         = 0;
    float inhaled_minute_volume         = 0;

    float lung_compliance               = 0;
    float static_compliance             = 0;

    uint16_t inhalation_pressure        = 0;
    uint16_t peak_inspiratory_pressure  = 0;
    uint16_t plateau_pressure           = 0;
    uint16_t mean_airway_pressure       = 0;

    uint8_t  fi02_percent               = 0;

    uint16_t apnea_index                = 0;
    uint16_t apnea_time                 = 0;

    uint8_t mandatory_breath            = 0;
};
#pragma pack()


enum VALVE_STATES : bool {
    V_OPEN = HIGH,
    V_CLOSED = LOW
};

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

// static uint32_t valve_port_states = 0x0; 
// static int pin_to_chan[50];  // too lazy to create a proper hashmap for 2 variables; 50 pins is probably fine
// static int chan_to_pin[50];  


void setThreshold(ALARM_CODES alarm, alarm_thresholds &thresholds, uint32_t &value);
void setDuration(CMD_SET_DURATION cmd, states_durations &timeouts, uint32_t &value);

// used for calculating averages, template due to different size for sums and averages
template <typename T> struct readings{
    uint64_t timestamp       = 0; //
    T pressure_air_supply    = 0;
    T pressure_air_regulated = 0;
    T pressure_buffer        = 0;
    T pressure_inhale        = 0;
    T pressure_patient       = 0;
    T temperature_buffer     = 0;
    T pressure_o2_supply     = 0;
    T pressure_o2_regulated  = 0;
    T pressure_diff_patient  = 0;
};
#endif
