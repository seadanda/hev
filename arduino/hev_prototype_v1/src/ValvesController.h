#ifndef VALVES_CONTROLLER_H
#define VALVES_CONTROLLER_H

#include <Arduino.h>

struct valve {
    int pin = -1;
    bool proportional = false;
    uint8_t state; 
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
    void setPWMValve(int pin, float frac_open);
    void setValves(bool vin_air, bool vin_o2, uint8_t vinhale,
                   uint8_t vexhale, bool vpurge);
    void getValves(bool &vin_air, bool &vin_o2, uint8_t &vinhale,
                   uint8_t &vexhale, bool &vpurge);
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

private:
    valve _air_in;
    valve _o2_in;
    valve _inhale;
    valve _exhale;
    valve _purge;
    uint8_t _pin_to_chan[50]; 

    uint8_t _valve_inhale_percent  ;   // replaced by a min level and a max level; bias inhale level.  very slightly open at "closed" position
    uint8_t _valve_exhale_percent  ;
    uint8_t _valve_air_in_enable   ;
    uint8_t _valve_o2_in_enable    ;
    uint8_t _valve_purge_enable    ;
    uint8_t _inhale_trigger_enable ;   // params - associated val of peak flow
    uint8_t _exhale_trigger_enable ;

    float _inhale_duty_cycle;
    float _inhale_open_min;
    float _inhale_open_max;
};

#endif