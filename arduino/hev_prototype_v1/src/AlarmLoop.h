#ifndef ALARM_LOOP_H
#define ALARM_LOOP_H

#include <Arduino.h>
#include "common.h"
#include "CommsFormat.h"
#include "AudioVisualController.h"

// general function to set alarm of any defined kind
template <typename T>
void setAlarm(ALARM_CODES alarm_code, T *alarms, T value) {
    alarms[alarm_code] = value;
}

class AlarmLoop {

public:
    AlarmLoop();
    ~AlarmLoop();
    bool fireAlarm(alarm_format &result, int &alarm_num, uint32_t &tnow);

    void processAlarms();

    uint32_t *getValues       () { return _alarms.values        ; }
    uint32_t *getThresholdsMin() { return _alarms.thresholds_min; }
    uint32_t *getThresholdsMax() { return _alarms.thresholds_max; }

    bool isTriggered()  { return _triggered; }
    bool *getActive() { return _alarms.actives; }

    uint32_t *getLastBroadcasts() { return _alarms.last_broadcasts; }

    ALARM_TYPE *getTypes() { return _alarms.priorities; }

private:
    bool checkTresholds();

private:
    AudioVisualController _av_controller;

    // automatically all triggered defined as false
    bool _triggered = false;
    alarms _alarms;

//    // default types set
//    alarms<ALARM_TYPE> _alarms_priority = {
//        ALARM_TYPE::PRIORITY_HIGH  ,    // APNEA
//        ALARM_TYPE::PRIORITY_HIGH  ,    // CHECK_VALVE_EXHALE
//        ALARM_TYPE::PRIORITY_HIGH  ,    // CHECK_P_PATIENT
//        ALARM_TYPE::PRIORITY_MEDIUM,    // EXPIRATION_SENSE_FAULT_OR_LEAK
//        ALARM_TYPE::PRIORITY_MEDIUM,    // EXPIRATION_VALVE_Leak
//        ALARM_TYPE::PRIORITY_MEDIUM,    // HIGH_FIO2
//        ALARM_TYPE::PRIORITY_HIGH  ,    // HIGH_PRESSURE
//        ALARM_TYPE::PRIORITY_MEDIUM,    // HIGH_RR
//        ALARM_TYPE::PRIORITY_MEDIUM,    // HIGH_VTE
//        ALARM_TYPE::PRIORITY_MEDIUM,    // LOW_VTE
//        ALARM_TYPE::PRIORITY_MEDIUM,    // HIGH_VTI
//        ALARM_TYPE::PRIORITY_MEDIUM,    // LOW_VTI
//        ALARM_TYPE::PRIORITY_HIGH  ,    // INTENTIONAL_STOP
//        ALARM_TYPE::PRIORITY_HIGH  ,    // LOW_BATTERY
//        ALARM_TYPE::PRIORITY_HIGH  ,    // LOW_FIO2
//        ALARM_TYPE::PRIORITY_HIGH  ,    // OCCLUSION
//        ALARM_TYPE::PRIORITY_HIGH  ,    // HIGH_PEEP
//        ALARM_TYPE::PRIORITY_HIGH  ,    // LOW_PEEP
//        ALARM_TYPE::PRIORITY_MEDIUM,    // AC_POWER_DISCONNECTION
//        ALARM_TYPE::PRIORITY_MEDIUM,    // BATTERY_FAULT_SRVC
//        ALARM_TYPE::PRIORITY_MEDIUM,    // BATTERY_CHARGE
//        ALARM_TYPE::PRIORITY_HIGH  ,    // AIR_FAIL
//        ALARM_TYPE::PRIORITY_HIGH  ,    // O2_FAIL
//        ALARM_TYPE::PRIORITY_HIGH  ,    // PRESSURE_SENSOR_FAULT
//        ALARM_TYPE::PRIORITY_HIGH       // ARDUINO_FAIL
//    };

};

#endif
