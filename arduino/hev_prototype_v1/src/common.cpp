#include "common.h"

CommsControl* global_comms;
SystemUtils* global_sys_utils;

void setDuration(CMD_SET_DURATION cmd, states_durations &durations, float value) {
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
        case CMD_SET_DURATION::BUFF_PRE_INHALE:
            durations.buff_pre_inhale = static_cast<uint32_t>(value);
            break;
        case CMD_SET_DURATION::INHALE:
            durations.inhale          = static_cast<uint32_t>(value);
            break;
        case CMD_SET_DURATION::PAUSE:
            durations.pause           = static_cast<uint32_t>(value);
            break;
        case CMD_SET_DURATION::EXHALE:
            durations.exhale     = static_cast<uint32_t>(value);
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

void setPID(CMD_SET_PID cmd, pid_variables &pid, float value)
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
        case CMD_SET_PID::TARGET_FINAL_PRESSURE:
            pid.target_final_pressure = value;
            break;
        case CMD_SET_PID::NSTEPS:
            pid.nsteps = value;
            break;
        default:
            break;
    }
}

void setTarget(CMD_SET_TARGET cmd, target_variables &targets, float value)
{

    switch(cmd){
        case CMD_SET_TARGET::INSPIRATORY_PRESSURE : 
            targets.inspiratory_pressure = value;
            break;
        case CMD_SET_TARGET::RESPIRATORY_RATE: 
            targets.respiratory_rate = value;
            break;
        case CMD_SET_TARGET::IE_RATIO: 
            targets.ie_ratio = value;
            targets.ie_selected = true;
            break;
        case CMD_SET_TARGET::VOLUME: 
            targets.volume = value;
            break;
        case CMD_SET_TARGET::PEEP: 
            targets.peep = value;
            break;
        case CMD_SET_TARGET::FIO2: 
            targets.fiO2_percent = value;
            break;
        case CMD_SET_TARGET::INHALE_TIME: 
            targets.inhale_time = 1000.0*value;// set in s, stored in ms
            targets.ie_selected = false;
            break;
        case CMD_SET_TARGET::INHALE_TRIGGER_ENABLE :
            targets.inhale_trigger_enable = (value > 0.9);
            break;
        case CMD_SET_TARGET::EXHALE_TRIGGER_ENABLE :
            targets.exhale_trigger_enable = (value > 0.9);
            break;
        case CMD_SET_TARGET::VOLUME_TRIGGER_ENABLE :
            targets.volume_trigger_enable = (value > 0.9);
            break;
        case CMD_SET_TARGET::INHALE_TRIGGER_THRESHOLD :
            targets.inhale_trigger_threshold = value;
            break;
        case CMD_SET_TARGET::EXHALE_TRIGGER_THRESHOLD :
            targets.exhale_trigger_threshold = value/100.0;
            break;
        case CMD_SET_TARGET::PID_GAIN: 
            targets.pid_gain = value;
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

float adcToMillibarFloat(float adc, float offset)
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

    return static_cast<float>(mbar);
    //return static_cast<int16_t>(adc);
} 

float adcToMillibarDPFloat(float adc, float offset)
{
    // The calibration for the DP sensor is provided by the manufacturer
    // https://docs.rs-online.com/7d77/0900766b81568899.pdf

    float PCB_Gain		= 2.		; // real voltage is two times higher thant the measured in the PCB (there is a voltage divider)
    float ADC_to_Voltage_Gain	= 3300./4096.0  ; // maximum Voltage of 3.3V for 4096 ADC counts - (It might need recalibration?)

    float zeroDPvoltageInADC    = (2500./PCB_Gain)*(1./ADC_to_Voltage_Gain);

    float _voltage = PCB_Gain * ADC_to_Voltage_Gain * (adc - offset + zeroDPvoltageInADC);

    float PaTombar = 0.01;

    float AoutVdd  = _voltage/5000.; // The board provides 5000 mV to the input of the DP sensor

    float sign = 2*((AoutVdd-0.5 > 0.)-0.5);
    
    float dp_mbar = PaTombar * sign * pow(((AoutVdd/0.4)-1.25), 2)*525; // same calculation as in the Labview Code  

    return static_cast<float>(dp_mbar);
} 


float adcToO2PercentFloat(float adc, float offset)
{
    // calibration should flush air only (21% o2) or o2 only (100%) for N secs 

    float PCB_Gain		= 4.		; // real voltage is 4 times higher thant the measured in the PCB (there is a voltage divider)
    float Sensor_Gain		= 100./10000.	; // the sensor gain is 100 % / 10000 mVolts
    float ADC_to_Voltage_Gain	= 3300./4096.0  ; // maximum Voltage of 3.3V for 4096 ADC counts - (It might need recalibration?)
    
    float o2pc = 100.0 * PCB_Gain * Sensor_Gain * ADC_to_Voltage_Gain * (adc - offset); 

    return o2pc;
}

void logMsg(String s)
{
        CommsControl *comms = getGlobalComms();
        Payload pl_send;

        logmsg_data_format log;
        sprintf(log.message, "%50s", "");
        sprintf(log.message, "%s", s.c_str() );
        pl_send.setPayload(PRIORITY::DATA_ADDR, reinterpret_cast<void *>(&log), sizeof(log));
        comms->writePayload(pl_send);
}

CommsControl* getGlobalComms() { return global_comms; }
void setGlobalComms(CommsControl *comms){ global_comms = comms; }
SystemUtils* getSystemUtils(){ return global_sys_utils; }
void setSystemUtils(SystemUtils *sys_utils){ global_sys_utils = sys_utils; }
