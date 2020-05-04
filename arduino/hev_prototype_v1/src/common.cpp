#include "common.h"

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

float_t adcToMillibarFloat(int16_t adc, int16_t offset = 0)
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

    return static_cast<float_t>(mbar);
    //return static_cast<int16_t>(adc);
} 
