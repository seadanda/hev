#ifndef ALARM_LOOP_H
#define ALARM_LOOP_H

#include <Arduino.h>
#include "common.h"
#include "CommsFormat.h"
#include "AudioVisualController.h"

// to simplify comparison and typing
#define COMPARE_THRESHOLD(VAL) (_alarms_triggered.VAL = (_alarms_thresholds.VAL < _thresholds_min.VAL || _alarms_thresholds.VAL > _thresholds_max.VAL) )

// general function to set alarm of any defined kind
template <typename T>
void setAlarm(ALARM_CODES alarm_code, alarms<T> &alarms, T value);

class AlarmLoop
{

public:
    AlarmLoop();
    ~AlarmLoop();
    int fireAlarm(alarms<bool> &triggered, alarms<ALARM_TYPE> &priority);

    bool checkTresholds();
    alarms<uint32_t>& getThresholdsMin() { return _thresholds_min; }
    alarms<uint32_t>& getThresholdsMax() { return _thresholds_max; }

    bool isTriggered() { return _triggered; }
    alarms<bool> &getAlarmsTriggered()   { return _alarms_triggered; }

    alarms<ALARM_TYPE>& getAlarmTypes   () { return _alarms_priority; }

private:
    AudioVisualController _av_controller;

    // automatically all triggered defined as false
    bool _triggered = false;
    alarms<bool> _alarms_triggered;
    alarms<uint32_t> _alarms_thresholds;

    // TODO fill in default min values
    alarms<uint32_t> _thresholds_min = {
        0x00000000,         // APNEA
        0x00000000,         // CHECK_VALVE_EXHALE
        0x00000000,         // CHECK_P_PATIENT
        0x00000000,         // EXPIRATION_SENSE_FAULT_OR_LEAK
        0x00000000,         // EXPIRATION_VALVE_Leak
        0x00000000,         // HIGH_FIO2
        0x00000000,         // HIGH_PRESSURE
        0x00000000,         // HIGH_RR
        0x00000000,         // HIGH_VTE
        0x00000000,         // LOW_VTE
        0x00000000,         // HIGH_VTI
        0x00000000,         // LOW_VTI
        0x00000000,         // INTENTIONAL_STOP
        0x00000000,         // LOW_BATTERY
        0x00000000,         // LOW_FIO2
        0x00000000,         // OCCLUSION
        0x00000000,         // HIGH_PEEP
        0x00000000,         // LOW_PEEP
        0x00000000,         // AC_POWER_DISCONNECTION
        0x00000000,         // BATTERY_FAULT_SRVC
        0x00000000,         // BATTERY_CHARGE
        0x00000000,         // AIR_FAIL
        0x00000000,         // O2_FAIL
        0x00000000,         // PRESSURE_SENSOR_FAULT
        0x00000000          // ARDUINO_FAIL
    };

    // TODO fill in default max values
    alarms<uint32_t> _thresholds_max = {
        0xFFFFFFFF,         // APNEA
        0xFFFFFFFF,         // CHECK_VALVE_EXHALE
        0xFFFFFFFF,         // CHECK_P_PATIENT
        0xFFFFFFFF,         // EXPIRATION_SENSE_FAULT_OR_LEAK
        0xFFFFFFFF,         // EXPIRATION_VALVE_Leak
        0xFFFFFFFF,         // HIGH_FIO2
        0xFFFFFFFF,         // HIGH_PRESSURE
        0xFFFFFFFF,         // HIGH_RR
        0xFFFFFFFF,         // HIGH_VTE
        0xFFFFFFFF,         // LOW_VTE
        0xFFFFFFFF,         // HIGH_VTI
        0xFFFFFFFF,         // LOW_VTI
        0xFFFFFFFF,         // INTENTIONAL_STOP
        0xFFFFFFFF,         // LOW_BATTERY
        0xFFFFFFFF,         // LOW_FIO2
        0xFFFFFFFF,         // OCCLUSION
        0xFFFFFFFF,         // HIGH_PEEP
        0xFFFFFFFF,         // LOW_PEEP
        0xFFFFFFFF,         // AC_POWER_DISCONNECTION
        0xFFFFFFFF,         // BATTERY_FAULT_SRVC
        0xFFFFFFFF,         // BATTERY_CHARGE
        0xFFFFFFFF,         // AIR_FAIL
        0xFFFFFFFF,         // O2_FAIL
        0xFFFFFFFF,         // PRESSURE_SENSOR_FAULT
        0xFFFFFFFF          // ARDUINO_FAIL
    };

    // default types set
    alarms<ALARM_TYPE> _alarms_priority = {
        ALARM_TYPE::PRIORITY_HIGH  ,    // APNEA
        ALARM_TYPE::PRIORITY_HIGH  ,    // CHECK_VALVE_EXHALE
        ALARM_TYPE::PRIORITY_HIGH  ,    // CHECK_P_PATIENT
        ALARM_TYPE::PRIORITY_MEDIUM,    // EXPIRATION_SENSE_FAULT_OR_LEAK
        ALARM_TYPE::PRIORITY_MEDIUM,    // EXPIRATION_VALVE_Leak
        ALARM_TYPE::PRIORITY_MEDIUM,    // HIGH_FIO2
        ALARM_TYPE::PRIORITY_HIGH  ,    // HIGH_PRESSURE
        ALARM_TYPE::PRIORITY_MEDIUM,    // HIGH_RR
        ALARM_TYPE::PRIORITY_MEDIUM,    // HIGH_VTE
        ALARM_TYPE::PRIORITY_MEDIUM,    // LOW_VTE
        ALARM_TYPE::PRIORITY_MEDIUM,    // HIGH_VTI
        ALARM_TYPE::PRIORITY_MEDIUM,    // LOW_VTI
        ALARM_TYPE::PRIORITY_HIGH  ,    // INTENTIONAL_STOP
        ALARM_TYPE::PRIORITY_HIGH  ,    // LOW_BATTERY
        ALARM_TYPE::PRIORITY_HIGH  ,    // LOW_FIO2
        ALARM_TYPE::PRIORITY_HIGH  ,    // OCCLUSION
        ALARM_TYPE::PRIORITY_HIGH  ,    // HIGH_PEEP
        ALARM_TYPE::PRIORITY_HIGH  ,    // LOW_PEEP
        ALARM_TYPE::PRIORITY_MEDIUM,    // AC_POWER_DISCONNECTION
        ALARM_TYPE::PRIORITY_MEDIUM,    // BATTERY_FAULT_SRVC
        ALARM_TYPE::PRIORITY_MEDIUM,    // BATTERY_CHARGE
        ALARM_TYPE::PRIORITY_HIGH  ,    // AIR_FAIL
        ALARM_TYPE::PRIORITY_HIGH  ,    // O2_FAIL
        ALARM_TYPE::PRIORITY_HIGH  ,    // PRESSURE_SENSOR_FAULT
        ALARM_TYPE::PRIORITY_HIGH       // ARDUINO_FAIL
    };

};

#endif
