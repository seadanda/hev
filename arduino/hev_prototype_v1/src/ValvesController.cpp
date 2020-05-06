#include "ValvesController.h"
#include "common.h"

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
    _exhale.proportional = true;
    _exhale.state = VALVE_STATE::FULLY_CLOSED;
    _exhale.voltage = 0;
    _exhale.current = 0;
    _exhale.device_number = -1;

    _purge.pin = pin_valve_purge;
    _purge.proportional = false;
    _purge.state = VALVE_STATE::CLOSED;
    _purge.voltage = 0;
    _purge.current = 0;
    _purge.i2caddr = 0x40; 
    _purge.device_number = -1;

#ifdef CHIP_ESP32
    _pin_to_chan[pin_valve_inhale] = pwm_chan_inhale;
    _pin_to_chan[pin_valve_exhale] = pwm_chan_exhale;
#endif
}

ValvesController::~ValvesController()
{ ; }

void ValvesController::setupINA(INA_Class *ina, uint8_t num_devices)
{
    _INA = ina;
    for(int i=0; i<num_devices; i++){

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

void ValvesController::updateIV(valve v)
{
    v.voltage = (float)(_INA->getBusMilliVolts(v.device_number)/1000.0);
    v.current = (float)(_INA->getShuntMicroVolts(v.device_number)/5.0);
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

    return &_iv_readings;
}
