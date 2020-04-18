#include "common.h"

//pin_valve_atmosphere  is not used right now

void setPWMValve(int pin, float frac_open)
{

#ifdef CHIP_ESP32
    int duty_cycle = pow(2, pwm_resolution) * frac_open;
    int chan = pin_to_chan[pin];
    ledcWrite(chan, duty_cycle);
#else
    int duty_cycle = pow(2, pwm_resolution) * frac_open;
    analogWrite(pin, duty_cycle);
#endif
}

void setValves(bool vin_air, bool vin_o2, float vinhale, 
               float vexhale, bool vpurge , bool vatmos)
{
    digitalWrite(pin_valve_air_in, vin_air);
    digitalWrite(pin_valve_o2_in, vin_o2);
    setPWMValve(pin_valve_inhale, vinhale);
    setPWMValve(pin_valve_exhale, vexhale);
    digitalWrite(pin_valve_purge, vpurge);
    // digitalWrite(pin_valve_atmosphere, vatmos);

    // save the state 
    valve_port_states.air_in = vin_air;
    valve_port_states.o2_in  = vin_o2;
    valve_port_states.inhale = vinhale;
    valve_port_states.exhale = vexhale;
    valve_port_states.purge  = vpurge;
    // valve_port_states.atmos = vatmos;
}

void getValves(bool &vin_air, bool &vin_o2, float &vinhale, 
               float &vexhale, bool &vpurge, bool &vatmos)
{
    // read the state
    vin_air = valve_port_states.air_in;
    vin_o2  = valve_port_states.o2_in ;
    vinhale = valve_port_states.inhale;
    vexhale = valve_port_states.exhale;
    vpurge  = valve_port_states.purge ;
    vatmos  = valve_port_states.atmos;
}