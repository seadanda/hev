#include "ValvesController.h"
#include "common.h"

ValvesController::ValvesController()
{
    _air_in.pin = pin_valve_air_in;
    _air_in.proportional = false;
    _air_in.state = VALVE_STATE::CLOSED;

    _o2_in.pin = pin_valve_o2_in;
    _o2_in.proportional = false;
    _o2_in.state = VALVE_STATE::CLOSED;

    _inhale.pin = pin_valve_inhale;
    _inhale.proportional = true;
    _inhale.state = VALVE_STATE::FULLY_CLOSED;

    _exhale.pin = pin_valve_exhale;
    _exhale.proportional = true;
    _exhale.state = VALVE_STATE::FULLY_CLOSED;

    _purge.pin = pin_valve_purge;
    _purge.proportional = false;
    _purge.state = VALVE_STATE::CLOSED;

#ifdef CHIP_ESP32
    _pin_to_chan[pin_valve_inhale] = pwm_chan_inhale;
    _pin_to_chan[pin_valve_exhale] = pwm_chan_exhale;
#endif

    _inhale_duty_cycle = 0;
    _inhale_open_max = MAX_VALVE_FRAC_OPEN;
    _inhale_open_min = 0.54;

    _valve_inhale_percent      = 0;   // replaced by a min level and a max level; bias inhale level.  very slightly open at "closed" position
    _valve_exhale_percent      = 0;
    _valve_air_in_enable       = 1;
    _valve_o2_in_enable        = 1;
    _valve_purge_enable        = 1;
    _inhale_trigger_enable     = 0;   // params - associated val of peak flow
    _exhale_trigger_enable     = 0;

    _PID_output                = 0;
}

ValvesController::~ValvesController()
{ ; }

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
void ValvesController::setInhaleDutyCycle(uint32_t value)
{
    float fdc = value / 100.0;
    if (fdc > MAX_VALVE_FRAC_OPEN ) 
        fdc = MAX_VALVE_FRAC_OPEN;
    _inhale_duty_cycle = fdc;
    
}

void ValvesController::setInhaleOpenMin(uint32_t value)
{
    float fop_min = value / 100.0;
    if (fop_min > MAX_VALVE_FRAC_OPEN ) 
        fop_min = MAX_VALVE_FRAC_OPEN;
    _inhale_open_min = fop_min;

}

void ValvesController::setInhaleOpenMax(uint32_t value)
{
    float fop_max = value / 100.0;
    if (fop_max > MAX_VALVE_FRAC_OPEN ) 
        fop_max = MAX_VALVE_FRAC_OPEN;
    _inhale_open_max = fop_max;

}

void ValvesController::setValves(bool vin_air, bool vin_o2, uint8_t vinhale, 
               uint8_t vexhale, bool vpurge)
{
    digitalWrite(_air_in.pin, vin_air * _valve_air_in_enable);
    digitalWrite(_o2_in.pin, vin_o2 * _valve_o2_in_enable);
    digitalWrite(_purge.pin, vpurge * _valve_purge_enable);

    switch(vinhale){
        case VALVE_STATE::FULLY_CLOSED:
            setPWMValve(_inhale.pin, 0.0);
            break;
        case VALVE_STATE::FULLY_OPEN:
            setPWMValve(_inhale.pin, MAX_VALVE_FRAC_OPEN); 
            break;
        case VALVE_STATE::OPEN:
            setPWMValve(_inhale.pin, _inhale_open_max); 
            break;
        case VALVE_STATE::CALIB_OPEN:
            setPWMValve(_inhale.pin, 0.9); 
            break;
        case VALVE_STATE::CLOSED:
            setPWMValve(_inhale.pin, _inhale_open_min); 
            break;
        case VALVE_STATE::PID:
            // placeholder - this should be replaced by:
            //doPID(_inhale.pin);
            setPWMValve(_inhale.pin, _PID_output);//_inhale_open_max);
            break;
        default:
            break;
    }

    switch(vexhale){
        case VALVE_STATE::FULLY_CLOSED:
            setPWMValve(_exhale.pin, 0.0);
            break;
        case VALVE_STATE::FULLY_OPEN:
            setPWMValve(_exhale.pin, MAX_VALVE_FRAC_OPEN); 
            break;
        case VALVE_STATE::CALIB_OPEN:
            setPWMValve(_exhale.pin, 0.9); 
            break;
        case VALVE_STATE::OPEN:
            setPWMValve(_exhale.pin, 0.8); 
            break;
        case VALVE_STATE::CLOSED:
            setPWMValve(_exhale.pin, 0); 
            break;
        default:
            //doPID(_exhale.pin);
            break;

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

uint8_t ValvesController::getValveInhalePercent(){return _valve_inhale_percent;}
uint8_t ValvesController::getValveExhalePercent(){return _valve_exhale_percent;}
uint8_t ValvesController::valveAirInEnabled(){return _valve_air_in_enable;}
uint8_t ValvesController::valveO2InEnabled(){return _valve_o2_in_enable;}
uint8_t ValvesController::valvePurgeEnabled(){return _valve_purge_enable;}
uint8_t ValvesController::inhaleTriggerEnabled(){return _inhale_trigger_enable;}
uint8_t ValvesController::exhaleTriggerEnabled(){return _exhale_trigger_enable;}

void ValvesController::enableO2InValve(bool en)
{
    _valve_o2_in_enable = en;
}

void ValvesController::enablePurgeValve(bool en)
{
    _valve_purge_enable = en;
}

void ValvesController::enableAirInValve(bool en)
{
    _valve_air_in_enable = en;
}

void ValvesController::setPIDoutput(float value){
	_PID_output = value;
}

float ValvesController::getPIDoutput(){
	return _PID_output;
}
