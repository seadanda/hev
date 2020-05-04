#include "AlarmLoop.h"

AlarmLoop::AlarmLoop()
{
    ;
}

AlarmLoop::~AlarmLoop()
{;}

int AlarmLoop::fireAlarm(alarms<bool> &triggered, alarms<ALARM_TYPE> &priority)
{
    return 0;
}

bool AlarmLoop::checkTresholds() {
    _triggered = false;
    _triggered |= COMPARE_THRESHOLD(apnea                           );
    _triggered |= COMPARE_THRESHOLD(check_valve_exhale              );
    _triggered |= COMPARE_THRESHOLD(check_p_patient                 );
    _triggered |= COMPARE_THRESHOLD(expiration_sense_fault_or_leak  );
    _triggered |= COMPARE_THRESHOLD(expiration_valve_leak           );
    _triggered |= COMPARE_THRESHOLD(high_fio2                       );
    _triggered |= COMPARE_THRESHOLD(high_pressure                   );
    _triggered |= COMPARE_THRESHOLD(high_rr                         );
    _triggered |= COMPARE_THRESHOLD(high_vte                        );
    _triggered |= COMPARE_THRESHOLD(low_vte                         );
    _triggered |= COMPARE_THRESHOLD(high_vti                        );
    _triggered |= COMPARE_THRESHOLD(low_vti                         );
    _triggered |= COMPARE_THRESHOLD(intentional_stop                );
    _triggered |= COMPARE_THRESHOLD(low_battery                     );
    _triggered |= COMPARE_THRESHOLD(low_fio2                        );
    _triggered |= COMPARE_THRESHOLD(occlusion                       );
    _triggered |= COMPARE_THRESHOLD(high_peep                       );
    _triggered |= COMPARE_THRESHOLD(low_peep                        );
    _triggered |= COMPARE_THRESHOLD(ac_power_disconnection          );
    _triggered |= COMPARE_THRESHOLD(battery_fault_srvc              );
    _triggered |= COMPARE_THRESHOLD(battery_charge                  );
    _triggered |= COMPARE_THRESHOLD(air_fail                        );
    _triggered |= COMPARE_THRESHOLD(o2_fail                         );
    _triggered |= COMPARE_THRESHOLD(pressure_sensor_fault           );
    _triggered |= COMPARE_THRESHOLD(arduino_fail                    );
    return _triggered;
}

template <typename T>
void setAlarm(ALARM_CODES alarm_code, alarms<T> &alarms_list, T value) {
    switch (alarm_code) {
        case ALARM_CODES::APNEA                         :
            alarms_list.apnea = value;
            break;
        case ALARM_CODES::CHECK_VALVE_EXHALE            :
            alarms_list.check_valve_exhale = value;
            break;
        case ALARM_CODES::CHECK_P_PATIENT               :
            alarms_list.check_p_patient = value;
            break;
        case ALARM_CODES::EXPIRATION_SENSE_FAULT_OR_LEAK:
            alarms_list.expiration_sense_fault_or_leak = value;
            break;
        case ALARM_CODES::EXPIRATION_VALVE_Leak         :
            alarms_list.expiration_valve_leak = value;
            break;
        case ALARM_CODES::HIGH_FIO2                     :
            alarms_list.high_fio2 = value;
            break;
        case ALARM_CODES::HIGH_PRESSURE                 :
            alarms_list.high_pressure = value;
            break;
        case ALARM_CODES::HIGH_RR                       :
            alarms_list.high_rr = value;
            break;
        case ALARM_CODES::HIGH_VTE                      :
            alarms_list.high_vte = value;
            break;
        case ALARM_CODES::LOW_VTE                       :
            alarms_list.low_vte = value;
            break;
        case ALARM_CODES::HIGH_VTI                      :
            alarms_list.high_vti = value;
            break;
        case ALARM_CODES::LOW_VTI                       :
            alarms_list.low_vti = value;
            break;
        case ALARM_CODES::INTENTIONAL_STOP              :
            alarms_list.intentional_stop = value;
            break;
        case ALARM_CODES::LOW_BATTERY                   :
            alarms_list.low_battery = value;
            break;
        case ALARM_CODES::LOW_FIO2                      :
            alarms_list.low_fio2 = value;
            break;
        case ALARM_CODES::OCCLUSION                     :
            alarms_list.occlusion = value;
            break;
        case ALARM_CODES::HIGH_PEEP                     :
            alarms_list.high_peep = value;
            break;
        case ALARM_CODES::LOW_PEEP                      :
            alarms_list.low_peep = value;
            break;
        case ALARM_CODES::AC_POWER_DISCONNECTION        :
            alarms_list.ac_power_disconnection = value;
            break;
        case ALARM_CODES::BATTERY_FAULT_SRVC            :
            alarms_list.battery_fault_srvc = value;
            break;
        case ALARM_CODES::BATTERY_CHARGE                :
            alarms_list.battery_charge = value;
            break;
        case ALARM_CODES::AIR_FAIL                      :
            alarms_list.air_fail = value;
            break;
        case ALARM_CODES::O2_FAIL                       :
            alarms_list.o2_fail = value;
            break;
        case ALARM_CODES::PRESSURE_SENSOR_FAULT         :
            alarms_list.pressure_sensor_fault = value;
            break;
        case ALARM_CODES::ARDUINO_FAIL                  :
            alarms_list.arduino_fail = value;
            break;
        default:
            break;
    }
}
