#ifndef VALVES_CONTROLLER_H
#define VALVES_CONTROLLER_H

#include <Arduino.h>
#include <INA.h>
#include "common.h"

struct valve {
    int pin = -1;
    bool proportional = false;
    uint8_t state; 
    float voltage;
    float current;
    uint8_t i2caddr;
    int8_t device_number;
};



enum VALVE_STATE : uint8_t
{
    CLOSED = 0,
    OPEN = 1,
    PID = 2,
    CALIB_OPEN = 3,  // 
    FULLY_OPEN = 4,
    FULLY_CLOSED = 5
};


class ValvesController
{


public:
    ValvesController();
    ~ValvesController();
    void setupINA(INA_Class *ina, uint8_t num_devices);
    void setPWMValve(int pin, float frac_open);
    void setValves(bool vin_air, bool vin_o2, uint8_t vinhale,
                   uint8_t vexhale, bool vpurge);
    void getValves(bool &vin_air, bool &vin_o2, uint8_t &vinhale,
                   uint8_t &vexhale, bool &vpurge);
    int calcValveDutyCycle(int pwm_resolution, float frac_open);

    valve_params& getValveParams();

    void enableO2InValve(bool en);
    void enablePurgeValve(bool en);
    void enableAirInValve(bool en);
    void setInhaleDutyCycle(float value);
    void setInhaleOpenMin(float value);
    void setInhaleOpenMax(float value);

    void updateIV(valve v);
    void updateAllIV();
    IV_readings<float>* getIVReadings();

private : 
    valve _air_in;
    valve _o2_in;
    valve _inhale;
    valve _exhale;
    valve _purge;

    uint8_t _pin_to_chan[50]; 

    valve_params _valve_params;

    INA_Class *_INA;
    IV_readings<float> _iv_readings; 
};

#endif