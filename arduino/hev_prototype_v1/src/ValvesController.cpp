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
    _inhale.state = VALVE_STATE::CLOSED;

    _exhale.pin = pin_valve_exhale;
    _exhale.proportional = false;
    _exhale.state = VALVE_STATE::CLOSED;

    _purge.pin = pin_valve_purge;
    _purge.proportional = false;
    _purge.state = VALVE_STATE::CLOSED;

}

ValvesController::~ValvesController()
{ ; }

int ValvesController::calcValveDutyCycle(int pwm_resolution, float frac_open)
{
    // Here the duty cycle is an integer in the range of the PWM resolution
    // - for 8 bit, we have range 0-255
    // => duty_cycle = frac_open * 255
    // there's a hard limit set by MAX_VALVE_FRAC_OPEN
    int range_upper_val = pow(2, pwm_resolution) - 1;
    if (frac_open > MAX_VALVE_FRAC_OPEN) 
        return (int)(range_upper_val * MAX_VALVE_FRAC_OPEN);
    return (int)(range_upper_val  * frac_open);
}

void ValvesController::setPWMValve(int pin, float frac_open)
{

#ifdef CHIP_ESP32
    int duty_cycle = calcValveDutyCycle(pwm_resolution, frac_open);
    int chan = pin_to_chan[pin];
    ledcWrite(chan, duty_cycle);
#else
    int duty_cycle = pow(2, pwm_resolution) * frac_open;
    analogWrite(pin, duty_cycle);
#endif
}

void ValvesController::setValves(bool vin_air, bool vin_o2, float vinhale, 
               float vexhale, bool vpurge)
{
    digitalWrite(_air_in.pin, vin_air);
    digitalWrite(_o2_in.pin, vin_o2);
    setPWMValve(_inhale.pin, vinhale);
    setPWMValve(_exhale.pin, vexhale);
    digitalWrite(_purge.pin, vpurge);

    // save the state 
    _air_in.state = vin_air;
    _o2_in.state  = vin_o2;
    _inhale.state = vinhale;
    _exhale.state = vexhale;
    _purge.state  = vpurge;
}

void ValvesController::getValves(bool &vin_air, bool &vin_o2, float &vinhale, 
               float &vexhale, bool &vpurge)
{
    // read the state
    vin_air = _air_in.state;
    vin_o2  = _o2_in.state ;
    vinhale = _inhale.state;
    vexhale = _exhale.state;
    vpurge  = _purge.state ;
}