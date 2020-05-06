#ifndef VALVES_CONTROLLER_H
#define VALVES_CONTROLLER_H

#include <Arduino.h>
#include <INA.h>

struct valve {
    int pin = -1;
    bool proportional = false;
    uint8_t state; 
    float voltage;
    float current;
    uint8_t i2caddr;
    int8_t device_number;
};

template <typename T> struct IV_readings{
    uint64_t timestamp       = 0; //
    T inhale_current = 0;
    T exhale_current = 0;
    T purge_current  = 0;
    T air_in_current = 0;
    T o2_in_current  = 0;
    T inhale_voltage = 0;
    T exhale_voltage = 0;
    T purge_voltage  = 0;
    T air_in_voltage = 0;
    T o2_in_voltage  = 0;
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
    void setupINA(INA_Class *ina, uint8_t num_devices);
    void setPWMValve(int pin, float frac_open);
    void setValves(bool vin_air, bool vin_o2, float vinhale,
                   float vexhale, bool vpurge);
    void getValves(bool &vin_air, bool &vin_o2, float &vinhale,
                   float &vexhale, bool &vpurge);
    int calcValveDutyCycle(int pwm_resolution, float frac_open);
    uint8_t getValveInhalePercent();
    uint8_t getValveExhalePercent();
    uint8_t valveAirInEnabled();
    uint8_t valveO2InEnabled();
    uint8_t valvePurgeEnabled();
    uint8_t inhaleTriggerEnabled();
    uint8_t exhaleTriggerEnabled();

    void enableO2InValve(bool en);
    void enablePurgeValve(bool en);
    void enableAirInValve(bool en);
    void setInhaleDutyCycle(uint32_t value);
    void setInhaleOpenMin(uint32_t value);
    void setInhaleOpenMax(uint32_t value);
    void updateIV(valve v);
    void updateAllIV();
    IV_readings<float>* getIVReadings();

        private : valve _air_in;
    valve _o2_in;
    valve _inhale;
    valve _exhale;
    valve _purge;
    uint8_t _pin_to_chan[50]; 

    uint8_t _valve_inhale_percent  ;   // replaced by a min level and a max level; bias inhale level.  very slightly open at "closed" position
    uint8_t _valve_o2_in_enable    ;
    uint8_t _valve_purge_enable    ;
    uint8_t _inhale_trigger_enable ;   // params - associated val of peak flow
    uint8_t _exhale_trigger_enable ;

    float _inhale_duty_cycle;
    float _inhale_open_min;
    float _inhale_open_max;
    INA_Class *_INA;
    IV_readings<float> _iv_readings; 
};

#endif