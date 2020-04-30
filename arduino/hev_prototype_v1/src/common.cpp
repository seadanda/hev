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

void setValveParam(CMD_SET_VALVE cmd, ValvesController *valves_controller, uint32_t &value)
{
    switch(cmd){
        case CMD_SET_VALVE::AIR_IN_ENABLE :
            valves_controller->enableAirInValve( (value > 0) );
            break;
        case CMD_SET_VALVE::O2_IN_ENABLE :
            valves_controller->enableO2InValve( (value > 0) );
            break;
        case CMD_SET_VALVE::PURGE_ENABLE :
            valves_controller->enablePurgeValve( (value > 0) );
            break;
        case CMD_SET_VALVE::INHALE_DUTY_CYCLE : 
            valves_controller->setInhaleDutyCycle(value); // should be 0-100
            break;
        case CMD_SET_VALVE::INHALE_OPEN_MIN :
            valves_controller->setInhaleOpenMin(value); // should be 0-100
            break;
        case CMD_SET_VALVE::INHALE_OPEN_MAX :
            valves_controller->setInhaleOpenMax(value); // should be 0-100
            break;
        default:
            break;
    }
}

int16_t adcToMillibar(int16_t adc, int16_t offset = 0)
{
    // TODO -  a proper calibration
    // rough guess - ADP51A11 spec sheet -Panasonic ADP5 pressure sensor
    // range is 0.5 to 4.5V ==  40 kPA range == 400 mbar ; but - voltage divide by 2 on PCB
    // 12 bit ADC => range = 0-4095
    float bits_per_millivolt = 3300/4096.0;
    float max_p = 400; //mbar
    float min_p = 0;
    float max_adc = 0.5 * 4500 / bits_per_millivolt;
    float min_adc = 0; //0.5 * 500 / bits_per_millivolt;
    float m = (max_p - min_p) / (max_adc - min_adc );
    float c = max_p - m * max_adc;
    float mbar = m*(adc-offset) + c; 

    return static_cast<int16_t>(mbar);
    //return static_cast<int16_t>(adc);
} 
