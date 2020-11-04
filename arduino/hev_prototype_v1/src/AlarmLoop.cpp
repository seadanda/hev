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


#include "AlarmLoop.h"

AlarmLoop::AlarmLoop()
{
    // make sure starting value is between thresholds
    for (uint8_t alarm_num = 0; alarm_num < ALARM_CODES::ALARMS_COUNT; alarm_num++) {
        _alarms.values[alarm_num] = (_alarms.thresholds_max[alarm_num] + _alarms.thresholds_min[alarm_num]) / 2;
    }

    setBatteryThresholds();
}

AlarmLoop::~AlarmLoop()
{;}

ALARM_TYPE AlarmLoop::checkThresholds() {
    _type = ALARM_TYPE::ALARM_TYPE_UNKNOWN;
    bool active = false;
    for (uint8_t alarm_num = 0; alarm_num < ALARM_CODES::ALARMS_COUNT; alarm_num++) {
        active |= _alarms.actives[alarm_num] = ( _alarms.values[alarm_num] < _alarms.thresholds_min[alarm_num]
                                              || _alarms.values[alarm_num] > _alarms.thresholds_max[alarm_num]);
        if (_alarms.actives[alarm_num] && _alarms.priorities[alarm_num] > _type) {
            _type = _alarms.priorities[alarm_num];
        }
    }

    return _type;
}

void AlarmLoop::fireAlarms() {
    switch (checkThresholds()) {
        case ALARM_TYPE::PRIORITY_LOW:
            _av_controller.setAVs(AV_STYLE::PERM_OFF, AV_STYLE::PERM_ON , AV_STYLE::PERM_OFF, AV_STYLE::OSCIL   );
            break;
        case ALARM_TYPE::PRIORITY_MEDIUM:
            _av_controller.setAVs(AV_STYLE::PERM_OFF, AV_STYLE::OSCIL   , AV_STYLE::PERM_OFF, AV_STYLE::OSCIL   );
            break;
        case ALARM_TYPE::PRIORITY_HIGH:
            _av_controller.setAVs(AV_STYLE::PERM_OFF, AV_STYLE::PERM_OFF, AV_STYLE::OSCIL   , AV_STYLE::OSCIL   );
            break;
        default:
            _av_controller.setAVs(AV_STYLE::PERM_ON , AV_STYLE::PERM_OFF, AV_STYLE::PERM_OFF, AV_STYLE::PERM_OFF);
            break;
    }

    _av_controller.update();
}

void AlarmLoop::updateValues(readings<float> fast_data, cycle_readings cr) {
//     ALARM_CODES::ALARM_CODE_UNKNOWN
     setAlarm<float>(ALARM_CODES::APNEA                         , _alarms.values, static_cast<float>(cr.apnea_index));
//     setAlarm<float>(ALARM_CODES::CHECK_VALVE_EXHALE            , _alarms.values, );
     setAlarm<float>(ALARM_CODES::CHECK_P_PATIENT               , _alarms.values, static_cast<float>(fast_data.pressure_patient));
//     setAlarm<float>(ALARM_CODES::EXPIRATION_SENSE_FAULT_OR_LEAK, _alarms.values, );
//     setAlarm<float>(ALARM_CODES::EXPIRATION_VALVE_Leak         , _alarms.values, );
     setAlarm<float>(ALARM_CODES::HIGH_FIO2                     , _alarms.values, static_cast<float>(cr.fiO2_percent));
     setAlarm<float>(ALARM_CODES::HIGH_PRESSURE                 , _alarms.values, static_cast<float>(fast_data.pressure_patient));
     setAlarm<float>(ALARM_CODES::HIGH_RR                       , _alarms.values, static_cast<float>(cr.respiratory_rate));
     setAlarm<float>(ALARM_CODES::HIGH_VTE                      , _alarms.values, static_cast<float>(cr.exhaled_tidal_volume));
     setAlarm<float>(ALARM_CODES::LOW_VTE                       , _alarms.values, static_cast<float>(cr.exhaled_tidal_volume));
     setAlarm<float>(ALARM_CODES::HIGH_VTI                      , _alarms.values, static_cast<float>(cr.inhaled_tidal_volume));
     setAlarm<float>(ALARM_CODES::LOW_VTI                       , _alarms.values, static_cast<float>(cr.inhaled_tidal_volume));
//     setAlarm<float>(ALARM_CODES::INTENTIONAL_STOP              , _alarms.values, );
//     ALARM_CODES::LOW_BATTERY
     setAlarm<float>(ALARM_CODES::LOW_FIO2                      , _alarms.values, static_cast<float>(cr.fiO2_percent));
//     setAlarm<float>(ALARM_CODES::OCCLUSION                     , _alarms.values, );
//     setAlarm<float>(ALARM_CODES::HIGH_PEEP                     , _alarms.values, );
//     setAlarm<float>(ALARM_CODES::LOW_PEEP                      , _alarms.values, static_cast<float>(cr.peep);
//     ALARM_CODES::AC_POWER_DISCONNECTION
//     ALARM_CODES::BATTERY_FAULT_SRVC
//     ALARM_CODES::BATTERY_CHARGE
     setAlarm<float>(ALARM_CODES::AIR_FAIL                      , _alarms.values, static_cast<float>(fast_data.pressure_air_regulated));
     setAlarm<float>(ALARM_CODES::O2_FAIL                       , _alarms.values, static_cast<float>(fast_data.pressure_o2_regulated));
//     setAlarm<float>(ALARM_CODES::PRESSURE_SENSOR_FAULT         , _alarms.values, );
//     setAlarm<float>(ALARM_CODES::ARDUINO_FAIL                  , _alarms.values, );
}

void AlarmLoop::setBatteryThresholds()
{

    // these are booleans
    // 0 = no alarm
    // 1 = alarm
    // => limits are -1 to 0.5

    setAlarm<float>(ALARM_CODES::AC_POWER_DISCONNECTION, _alarms.thresholds_min, -1.0);
    setAlarm<float>(ALARM_CODES::BATTERY_CHARGE,         _alarms.thresholds_min, -1.0);
    setAlarm<float>(ALARM_CODES::BATTERY_FAULT_SRVC,     _alarms.thresholds_min, -1.0);
    setAlarm<float>(ALARM_CODES::LOW_BATTERY,            _alarms.thresholds_min, -1.0);

    setAlarm<float>(ALARM_CODES::AC_POWER_DISCONNECTION, _alarms.thresholds_max, 0.5);
    setAlarm<float>(ALARM_CODES::BATTERY_CHARGE,         _alarms.thresholds_max, 0.5);
    setAlarm<float>(ALARM_CODES::BATTERY_FAULT_SRVC,     _alarms.thresholds_max, 0.5);
    setAlarm<float>(ALARM_CODES::LOW_BATTERY,            _alarms.thresholds_max, 0.5);
}

void AlarmLoop::setBatteryAlarms(battery_data_format &bat)
{
    bool ac_power_disconnection = (bat.ok == 0);
    bool battery_charge         = (bat.rdy2buf == 0);
    bool low_battery            = (bat.process_bat85 == 0);
    bool battery_fault_svc      = ((bat.prob_elec == 1) || (bat.alarm == 1));

    setAlarm<float>(ALARM_CODES::AC_POWER_DISCONNECTION, _alarms.values, ac_power_disconnection);
    setAlarm<float>(ALARM_CODES::BATTERY_CHARGE,         _alarms.values, battery_charge);
    setAlarm<float>(ALARM_CODES::BATTERY_FAULT_SRVC,     _alarms.values, battery_fault_svc);
    setAlarm<float>(ALARM_CODES::LOW_BATTERY,            _alarms.values, low_battery);
}
