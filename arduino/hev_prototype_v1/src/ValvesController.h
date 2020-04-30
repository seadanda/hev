#ifndef VALVES_CONTROLLER_H
#define VALVES_CONTROLLER_H

#include <Arduino.h>

struct valve {
    int pin = -1;
    bool proportional = false;
    float state; 
};

enum VALVE_STATE : bool
{
    CLOSED = LOW,
    OPEN = HIGH
};


class ValvesController
{


public:
    ValvesController();
    ~ValvesController();
    void setPWMValve(int pin, float frac_open);
    void setValves(bool vin_air, bool vin_o2, float vinhale,
                   float vexhale, bool vpurge);
    void getValves(bool &vin_air, bool &vin_o2, float &vinhale,
                   float &vexhale, bool &vpurge);
    int calcValveDutyCycle(int pwm_resolution, float frac_open);

private:
    valve _air_in;
    valve _o2_in;
    valve _inhale;
    valve _exhale;
    valve _purge;
    uint8_t _pin_to_chan[50]; 

};

#endif