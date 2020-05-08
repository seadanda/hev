#include "common.h"

void setDuration(CMD_SET_DURATION cmd, states_durations &durations, float &value) {
    switch (cmd) {
        case CMD_SET_DURATION::CALIBRATION:
            durations.calibration     = static_cast<uint32_t>(value);
            break;
        case CMD_SET_DURATION::BUFF_PURGE:
            durations.buff_purge      = static_cast<uint32_t>(value);
            break;
        case CMD_SET_DURATION::BUFF_FLUSH:
            durations.buff_flush      = static_cast<uint32_t>(value);
            break;
        case CMD_SET_DURATION::BUFF_PREFILL:
            durations.buff_prefill    = static_cast<uint32_t>(value);
            break;
        case CMD_SET_DURATION::BUFF_FILL:
            durations.buff_fill       = static_cast<uint32_t>(value);
            break;
        case CMD_SET_DURATION::BUFF_LOADED:
            durations.buff_loaded     = static_cast<uint32_t>(value);
            break;
        case CMD_SET_DURATION::BUFF_PRE_INHALE:
            durations.buff_pre_inhale = static_cast<uint32_t>(value);
            break;
        case CMD_SET_DURATION::INHALE:
            durations.inhale          = static_cast<uint32_t>(value);
            break;
        case CMD_SET_DURATION::PAUSE:
            durations.pause           = static_cast<uint32_t>(value);
            break;
        case CMD_SET_DURATION::EXHALE_FILL:
            durations.exhale_fill     = static_cast<uint32_t>(value);
            break;
        case CMD_SET_DURATION::EXHALE:
            durations.exhale          = static_cast<uint32_t>(value);
            break;
        default:
            break;
    }
}

void setValveParam(CMD_SET_VALVE cmd, valve_params &vparams, float value)
{
    switch(cmd){
        case CMD_SET_VALVE::AIR_IN_ENABLE :
            vparams.valve_air_in_enable = (value > 0.9);
            break;
        case CMD_SET_VALVE::O2_IN_ENABLE :
            vparams.valve_o2_in_enable = (value > 0.9);
            break;
        case CMD_SET_VALVE::PURGE_ENABLE :
            vparams.valve_purge_enable = (value > 0.9);
            break;
        case CMD_SET_VALVE::INHALE_TRIGGER_ENABLE :
            vparams.inhale_trigger_enable = (value > 0.9);
            break;
        case CMD_SET_VALVE::EXHALE_TRIGGER_ENABLE :
            vparams.exhale_trigger_enable = (value > 0.9);
            break;
        case CMD_SET_VALVE::INHALE_DUTY_CYCLE : 
            vparams.inhale_duty_cycle = (value < 0) ? 0.0 : (value > MAX_VALVE_FRAC_OPEN) ? MAX_VALVE_FRAC_OPEN : value;
            break;
        case CMD_SET_VALVE::INHALE_OPEN_MIN :
            vparams.inhale_open_min = (value < 0) ? 0.0 : (value > MAX_VALVE_FRAC_OPEN) ? MAX_VALVE_FRAC_OPEN : value;
            break;
        case CMD_SET_VALVE::INHALE_OPEN_MAX :
            vparams.inhale_open_max = (value < 0) ? 0.0 : (value > MAX_VALVE_FRAC_OPEN) ? MAX_VALVE_FRAC_OPEN : value;
            break;
        default:
            break;
    }
}

void setPID(CMD_SET_PID cmd, pid_variables &pid, float &value)
{
    switch(cmd){
        case CMD_SET_PID::KP:
            pid.Kp = value;
            break;
        case CMD_SET_PID::KI:
            pid.Ki = value;
            break;
        case CMD_SET_PID::KD:
            pid.Kd = value;
            break;
        default:
            break;
    }
}

int16_t adcToMillibar(int16_t adc, int16_t offset)
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

    float PCB_Gain		= 2.		; // real voltage is two times higher thant the measured in the PCB (there is a voltage divider)
    float Sensor_Gain		= 400./4000.	; // the sensor gain is 400 mbar / 4000 mVolts
    float ADC_to_Voltage_Gain	= 3300./4096.0  ; // maximum Voltage of 3.3V for 4096 ADC counts - (It might need recalibration?)
    
    mbar = PCB_Gain * Sensor_Gain * ADC_to_Voltage_Gain * (adc - offset); // same calculation as in the Labview Code  

    return static_cast<int16_t>(mbar);
    //return static_cast<int16_t>(adc);
} 

float adcToMillibarFloat(int16_t adc, int16_t offset)
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

    return static_cast<float>(mbar);
    //return static_cast<int16_t>(adc);
} 
