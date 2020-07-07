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
    _alarms.values[ALARM_CODES::CHECK_P_PATIENT] = static_cast<float>(fast_data.pressure_patient);
    _alarms.values[ALARM_CODES::LOW_FIO2] = static_cast<float>(cr.fiO2_percent);
    _alarms.values[ALARM_CODES::HIGH_FIO2] = static_cast<float>(cr.fiO2_percent);
    _alarms.values[ALARM_CODES::APNEA] = static_cast<float>(cr.apnea_index);
    _alarms.values[ALARM_CODES::HIGH_PRESSURE] = static_cast<float>(fast_data.pressure_patient);
    _alarms.values[ALARM_CODES::HIGH_RR] = static_cast<float>(cr.respiratory_rate);
    _alarms.values[ALARM_CODES::HIGH_VTE] = static_cast<float>(cr.exhaled_tidal_volume);
    _alarms.values[ALARM_CODES::HIGH_VTI] = static_cast<float>(cr.inhaled_tidal_volume);
    _alarms.values[ALARM_CODES::LOW_VTE] = static_cast<float>(cr.exhaled_tidal_volume);
    _alarms.values[ALARM_CODES::LOW_VTI] = static_cast<float>(cr.inhaled_tidal_volume);
//    _alarms.values[ALARM_CODES::LOW_PEEP] = static_cast<float>(cr.peep);
    _alarms.values[ALARM_CODES::AIR_FAIL] = static_cast<float>(fast_data.pressure_air_regulated);
    _alarms.values[ALARM_CODES::O2_FAIL] = static_cast<float>(fast_data.pressure_o2_regulated);
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
