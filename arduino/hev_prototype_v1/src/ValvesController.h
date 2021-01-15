// © Copyright CERN, Riga Technical University and University of Liverpool 2020.
// All rights not expressly granted are reserved. 
// 
// This file is part of hev-sw.
// 
// hev-sw is free software: you can redistribute it and/or modify it under
// the terms of the GNU General Public Licence as published by the Free
// Software Foundation, either version 3 of the Licence, or (at your option)
// any later version.
// 
// hev-sw is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public Licence
// for more details.
// 
// You should have received a copy of the GNU General Public License along
// with hev-sw. If not, see <http://www.gnu.org/licenses/>.
// 
// The authors would like to acknowledge the much appreciated support
// of all those involved with the High Energy Ventilator project
// (https://hev.web.cern.ch/).


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

    void getValves(bool &vin_air, bool &vin_o2, uint8_t &vinhale,
                   uint8_t &vexhale, bool &vpurge);

    void setFillValves(bool vin_air, bool vin_o2, bool vpurge);
    void setBreatheValves(uint8_t vinhale, uint8_t vexhale);
    
    uint32_t calcValveDutyCycle(uint32_t pwm_resolution, float frac_open);

    valve_params& getValveParams();

    void enableO2InValve(bool en);
    void enablePurgeValve(bool en);
    void enableAirInValve(bool en);
    void setInhaleDutyCycle(float value);
    void setInhaleOpenMin(float value);
    void setInhaleOpenMax(float value);
    
    bool getO2Valve();
    void updateIV(valve &v);
    void updateAllIV();
    IV_readings<float>* getIVReadings();

    void    setPIDoutput(float value);
    float   getPIDoutput();

    bool INAFound();

private:
    valve _air_in;
    valve _o2_in;
    valve _inhale;
    valve _exhale;
    valve _purge;

    uint8_t _pin_to_chan[50]; 

    valve_params _valve_params;

    INA_Class *_INA;
    bool _INA_found;
    IV_readings<float> _iv_readings; 
    float _PID_output;
};

#endif
