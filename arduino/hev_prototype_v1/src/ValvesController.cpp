#include "ValvesController.h"

ValvesController::ValvesController()
{
    _air_in.pin = pin_valve_air_in;
    _air_in.proportional = false;
    _air_in.state = VALVE_STATE::CLOSED;
    _air_in.voltage = 0;
    _air_in.current = 0;
    _air_in.device_number = -1;

    _o2_in.pin = pin_valve_o2_in;
    _o2_in.proportional = false;
    _o2_in.state = VALVE_STATE::CLOSED;
    _o2_in.voltage = 0;
    _o2_in.current = 0;
    _o2_in.device_number = -1;

    _inhale.pin = pin_valve_inhale;
    _inhale.proportional = true;
    _inhale.state = VALVE_STATE::FULLY_CLOSED;
    _inhale.voltage = 0;
    _inhale.current = 0;
    _inhale.device_number = -1;

    _exhale.pin = pin_valve_exhale;
#ifdef EXHALE_VALVE_PROPORTIONAL
    _exhale.proportional = true;
#else
    _exhale.proportional = false;
#endif
    _exhale.state = VALVE_STATE::OPEN;
    _exhale.voltage = 0;
    _exhale.current = 0;
    _exhale.device_number = -1;

    _purge.pin = pin_valve_purge;
    _purge.proportional = false;
    _purge.state = VALVE_STATE::CLOSED;
    _purge.voltage = 0;
    _purge.current = 0;
    _purge.device_number = -1;

#ifdef CHIP_ESP32
    _pin_to_chan[pin_valve_inhale] = pwm_chan_inhale;
    _pin_to_chan[pin_valve_exhale] = pwm_chan_exhale;
#endif

    _valve_params.inhale_duty_cycle = 0;
    _valve_params.inhale_open_max = MAX_VALVE_FRAC_OPEN;
    _valve_params.inhale_open_min = 0.52;
    _valve_params.valve_air_in_enable       = 1;
    _valve_params.valve_o2_in_enable        = 1;
    _valve_params.valve_purge_enable        = 1;
    _valve_params.inhale_trigger_enable     = 0;   // params - associated val of peak flow
    _valve_params.exhale_trigger_enable     = 0;

    _valve_params.inhale_trigger_threshold     = 0.0025;   // abs flow ? unit / 
    _valve_params.exhale_trigger_threshold     = 0.3;  // 20% of the peak flow

    _PID_output                = 0;

    _INA_found = false;
}

ValvesController::~ValvesController()
{ ; }

bool ValvesController::INAFound(){ return _INA_found; }

void ValvesController::setupINA(INA_Class *ina, uint8_t num_devices)
{
    _INA = ina;
    for(int i=0; i<num_devices; i++){
        _INA_found = true; 
        uint8_t addr = ina->getDeviceAddress(i);
        switch(addr){
            case 0x40 :   // shared inhale and exhale
                _inhale.device_number = i;
                _exhale.device_number = i;
                _inhale.i2caddr = 0x40;
                _exhale.i2caddr = 0x40;
            case 0x41 : 
                _purge.device_number = i;
                _purge.i2caddr = 0x41;
            case 0x45 : 
                _air_in.device_number = i;
                _air_in.i2caddr = 0x45;
            case 0x44 : 
                _o2_in.device_number = i;
                _o2_in.i2caddr = 0x44;
        }
    }

}

uint32_t ValvesController::calcValveDutyCycle(uint32_t pwm_resolution, float frac_open)
{
    // Here the duty cycle is an uint32_teger in the range of the PWM resolution
    // - for 8 bit, we have range 0-255
    // => duty_cycle = frac_open * 255
    // there's a hard limit set by MAX_VALVE_FRAC_OPEN
    uint32_t range_upper_val = pow(2, pwm_resolution) - 1;
    if (frac_open > MAX_VALVE_FRAC_OPEN) 
        return (uint32_t)(range_upper_val * MAX_VALVE_FRAC_OPEN);
    return (uint32_t)(range_upper_val  * frac_open);
}

void ValvesController::setPWMValve(int pin, float frac_open)
{

#ifdef CHIP_ESP32
    uint32_t duty_cycle = calcValveDutyCycle(pwm_resolution, frac_open);
    int chan = _pin_to_chan[pin];
    //if (pin == pin_valve_exhale)
    //    chan = pwm_chan_exhale;
    //else if (pin == pin_valve_inhale)
    //    chan = pwm_chan_inhale;
    ledcWrite(chan, duty_cycle);
#else
    int duty_cycle = pow(2, pwm_resolution) * frac_open;
    analogWrite(pin, duty_cycle);
#endif
}

// might want to change these to float : 
void ValvesController::setInhaleDutyCycle(float value)
{
    float fdc = value;
    if (fdc > MAX_VALVE_FRAC_OPEN ) 
        fdc = MAX_VALVE_FRAC_OPEN;
    _valve_params.inhale_duty_cycle = fdc;
    
}

void ValvesController::setInhaleOpenMin(float value)
{
    float fop_min = value;
    if (fop_min > MAX_VALVE_FRAC_OPEN ) 
        fop_min = MAX_VALVE_FRAC_OPEN;
    _valve_params.inhale_open_min = fop_min;

}

void ValvesController::setInhaleOpenMax(float value)
{
    float fop_max = value;
    if (fop_max > MAX_VALVE_FRAC_OPEN ) 
        fop_max = MAX_VALVE_FRAC_OPEN;
    _valve_params.inhale_open_max = fop_max;

}

void ValvesController::setValves(bool vin_air, bool vin_o2, uint8_t vinhale, 
               uint8_t vexhale, bool vpurge)
{
    digitalWrite(_air_in.pin, vin_air * _valve_params.valve_air_in_enable);
    digitalWrite(_o2_in.pin, vin_o2 * _valve_params.valve_o2_in_enable);
    digitalWrite(_purge.pin, vpurge * _valve_params.valve_purge_enable);

    switch(vinhale){
        case VALVE_STATE::FULLY_CLOSED:
            setPWMValve(_inhale.pin, 0.0);
            break;
        case VALVE_STATE::FULLY_OPEN:
            setPWMValve(_inhale.pin, _valve_params.inhale_open_max); 
            break;
        case VALVE_STATE::OPEN:
            setPWMValve(_inhale.pin, _valve_params.inhale_open_max); 
            break;
        case VALVE_STATE::CALIB_OPEN:
            setPWMValve(_inhale.pin, _valve_params.inhale_open_max); 
            break;
        case VALVE_STATE::CLOSED:
            setPWMValve(_inhale.pin, _valve_params.inhale_open_min); 
            break;
        case VALVE_STATE::PID:
            // placeholder - this should be replaced by:
            //doPID(_inhale.pin);
            setPWMValve(_inhale.pin, _PID_output);//_inhale_open_max);
            break;
        default:
            break;
    }
    if(_exhale.proportional == true){
	    switch(vexhale){
		    case VALVE_STATE::FULLY_CLOSED:
			    setPWMValve(_exhale.pin, 0);
			    break;
		    case VALVE_STATE::FULLY_OPEN:
			    setPWMValve(_exhale.pin, _valve_params.inhale_open_max); 
			    break;
		    case VALVE_STATE::CALIB_OPEN:
			    setPWMValve(_exhale.pin, _valve_params.inhale_open_max); 
			    break;
		    case VALVE_STATE::OPEN:
			    setPWMValve(_exhale.pin, _valve_params.inhale_open_max); 
			    break;
		    case VALVE_STATE::CLOSED:
			    setPWMValve(_exhale.pin, 0); 
			    break;
		    default:
			    //doPID(_exhale.pin);
			    break;
	    }
    } else if(_exhale.proportional == false){
        if (vexhale == VALVE_STATE::OPEN)
            digitalWrite(_exhale.pin, VALVE_STATE::CLOSED); //inverted logic; normally open;
        else
            digitalWrite(_exhale.pin, VALVE_STATE::OPEN); //inverted logic; normally open;
    }

    // save the state 
    _air_in.state = vin_air;
    _o2_in.state  = vin_o2;
    _inhale.state = vinhale;
    _exhale.state = vexhale;
    _purge.state  = vpurge;
}

void ValvesController::getValves(bool &vin_air, bool &vin_o2, uint8_t &vinhale, 
               uint8_t &vexhale, bool &vpurge)
{
    // read the state
    vin_air = _air_in.state;
    vin_o2  = _o2_in.state ;
    vinhale = _inhale.state;
    vexhale = _exhale.state;
    vpurge  = _purge.state ;
}


void ValvesController::enableO2InValve(bool en)
{
    _valve_params.valve_o2_in_enable = en;
}

void ValvesController::enablePurgeValve(bool en)
{
    _valve_params.valve_purge_enable = en;
}

void ValvesController::enableAirInValve(bool en)
{
    _valve_params.valve_air_in_enable = en;
}

valve_params& ValvesController::getValveParams()
{
    return _valve_params;
}

void ValvesController::updateIV(valve &v)
{
    if(_INA_found){
        v.voltage = (float)(_INA->getBusMilliVolts(v.device_number) / 1000.0);
        v.current = (float)(_INA->getShuntMicroVolts(v.device_number) / 5.0);
    }
}

IV_readings<float>* ValvesController::getIVReadings()
{
    updateIV(_inhale);
    updateIV(_exhale);
    updateIV(_purge);
    updateIV(_air_in);
    updateIV(_o2_in);

    _iv_readings.timestamp = millis();
    _iv_readings.inhale_current = _inhale.current;
    _iv_readings.exhale_current = _exhale.current;
    _iv_readings.purge_current = _purge.current;
    _iv_readings.o2_in_current = _o2_in.current;
    _iv_readings.air_in_current = _air_in.current;
    _iv_readings.inhale_voltage = _inhale.voltage;
    _iv_readings.exhale_voltage = _exhale.voltage;
    _iv_readings.purge_voltage = _purge.voltage;
    _iv_readings.o2_in_voltage = _o2_in.voltage;
    _iv_readings.air_in_voltage = _air_in.voltage;
    _iv_readings.inhale_i2caddr = _inhale.i2caddr;
    _iv_readings.exhale_i2caddr = _exhale.i2caddr;
    _iv_readings.purge_i2caddr = _purge.i2caddr;
    _iv_readings.o2_in_i2caddr = _o2_in.i2caddr;
    _iv_readings.air_in_i2caddr = _air_in.i2caddr;

    return &_iv_readings;
}

void ValvesController::setPIDoutput(float value){
	_PID_output = value;
}

float ValvesController::getPIDoutput(){
	return _PID_output;
}
