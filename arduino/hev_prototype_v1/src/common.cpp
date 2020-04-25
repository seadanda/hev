#include "common.h"


void setThreshold(ALARM_CODES alarm, alarm_thresholds &thresholds, uint32_t &value) {
    switch (alarm) {
        case ALARM_CODES::APNEA                         :
            thresholds.apnea = value;
            break;
        case ALARM_CODES::CHECK_VALVE_EXHALE            :
            thresholds.check_valve_exhale = value;
            break;
        case ALARM_CODES::CHECK_P_PATIENT               :
            thresholds.check_p_patient = value;
            break;
        case ALARM_CODES::EXPIRATION_SENSE_FAULT_OR_LEAK:
            thresholds.expiration_sense_fault_or_leak = value;
            break;
        case ALARM_CODES::EXPIRATION_VALVE_Leak         :
            thresholds.expiration_valve_leak = value;
            break;
        case ALARM_CODES::HIGH_FIO2                     :
            thresholds.high_fio2 = value;
            break;
        case ALARM_CODES::HIGH_PRESSURE                 :
            thresholds.high_pressure = value;
            break;
        case ALARM_CODES::HIGH_RR                       :
            thresholds.high_rr = value;
            break;
        case ALARM_CODES::HIGH_VTE                      :
            thresholds.high_vte = value;
            break;
        case ALARM_CODES::LOW_VTE                       :
            thresholds.low_vte = value;
            break;
        case ALARM_CODES::HIGH_VTI                      :
            thresholds.high_vti = value;
            break;
        case ALARM_CODES::LOW_VTI                       :
            thresholds.low_vti = value;
            break;
        case ALARM_CODES::INTENTIONAL_STOP              :
            thresholds.intentional_stop = value;
            break;
        case ALARM_CODES::LOW_BATTERY                   :
            thresholds.low_battery = value;
            break;
        case ALARM_CODES::LOW_FIO2                      :
            thresholds.low_fio2 = value;
            break;
        case ALARM_CODES::OCCLUSION                     :
            thresholds.occlusion = value;
            break;
        case ALARM_CODES::HIGH_PEEP                     :
            thresholds.high_peep = value;
            break;
        case ALARM_CODES::LOW_PEEP                      :
            thresholds.low_peep = value;
            break;
        case ALARM_CODES::AC_POWER_DISCONNECTION        :
            thresholds.ac_power_disconnection = value;
            break;
        case ALARM_CODES::BATTERY_FAULT_SRVC            :
            thresholds.battery_fault_srvc = value;
            break;
        case ALARM_CODES::BATTERY_CHARGE                :
            thresholds.battery_charge = value;
            break;
        case ALARM_CODES::AIR_FAIL                      :
            thresholds.air_fail = value;
            break;
        case ALARM_CODES::O2_FAIL                       :
            thresholds.o2_fail = value;
            break;
        case ALARM_CODES::PRESSURE_SENSOR_FAULT         :
            thresholds.pressure_sensor_fault = value;
            break;
        case ALARM_CODES::ARDUINO_FAIL                  :
            thresholds.arduino_fail = value;
            break;
        default:
            break;
    }
}

void setDuration(CMD_SET_DURATION cmd, states_durations &durations, uint32_t &value) {
    switch (cmd) {
        case CMD_SET_DURATION::CALIBRATION:
            durations.calibration     = value;
            break;
        case CMD_SET_DURATION::BUFF_PURGE:
            durations.buff_purge      = value;
            break;
        case CMD_SET_DURATION::BUFF_FLUSH:
            durations.buff_flush      = value;
            break;
        case CMD_SET_DURATION::BUFF_PREFILL:
            durations.buff_prefill    = value;
            break;
        case CMD_SET_DURATION::BUFF_FILL:
            durations.buff_fill       = value;
            break;
        case CMD_SET_DURATION::BUFF_LOADED:
            durations.buff_loaded     = value;
            break;
        case CMD_SET_DURATION::BUFF_PRE_INHALE:
            durations.buff_pre_inhale = value;
            break;
        case CMD_SET_DURATION::INHALE:
            durations.inhale          = value;
            break;
        case CMD_SET_DURATION::PAUSE:
            durations.pause           = value;
            break;
        case CMD_SET_DURATION::EXHALE_FILL:
            durations.exhale_fill     = value;
            break;
        case CMD_SET_DURATION::EXHALE:
            durations.exhale          = value;
            break;
        default:
            break;
    }
}
