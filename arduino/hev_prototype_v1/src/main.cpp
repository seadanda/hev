#include <Arduino.h>
#include <WiFi.h>
// #include <MemoryFree.h>
#include <Wire.h>
#include <Adafruit_MCP9808.h>
#include <INA.h>
#include "CommsControl.h"
#include "BreathingLoop.h"
#include "ValvesController.h"
#include "UILoop.h"
#include "AlarmLoop.h"
#include "common.h"

int ventilation_mode = HEV_MODE_PS;

uint32_t report_timeout = 50; //ms
uint32_t report_time = 0;
float working_pressure = 1;             //?
float inspiratory_minute_volume = 6000; // ml/min
float respiratory_rate = 15;            //  10-40 +-1 ;aka breaths_per_min
float inspiratory_pressure = 10;        // 10-80 cmH2O +-1
//float tidal_volume = 200; // calc 200-1500ml +- 100
float inspiratory_time = 1.0; // 0.4-1.5s +-0.1
float pause_time = 1.0;       // range?
//float expiratory_time ; // calc
float expiratory_minute_volume; // calc?? same as inspiratory_minute_volume?
float trigger_sensitivity;

// comms
data_format data;
CommsControl comms;
Payload plReceive;
Payload plSend;

// loops
BreathingLoop breathing_loop;
UILoop        ui_loop(&breathing_loop);
AlarmLoop     alarm_loop;

bool start_fsm = false;

// calculations
float calcTidalVolume()
{
    return inspiratory_minute_volume / respiratory_rate;
}

float calcExpirationTime()
{
    float total_respiratory_time = 60.0 / respiratory_rate;
    // total = expire + inspire + pause
    return (total_respiratory_time - inspiratory_time - pause_time);
}

float calcExpiratoryMinuteVolume()
{
    // probably need to calculate this from readings
    return 0;
}

void setup()
{
#ifdef CHIP_ESP32
    WiFi.mode(WIFI_OFF);
    btStop();
    ledcSetup(pwm_chan_inhale, pwm_frequency, pwm_resolution);
    ledcSetup(pwm_chan_exhale, pwm_frequency, pwm_resolution);
    ledcAttachPin(pin_valve_inhale , pwm_chan_inhale);  
    ledcAttachPin(pin_valve_exhale , pwm_chan_exhale);  
    pin_to_chan[pin_valve_inhale] = pwm_chan_inhale;
    pin_to_chan[pin_valve_exhale] = pwm_chan_exhale;

// map<int,int> pin_to_chan; // = { pin_valve_inhale : pwm_chan_inhale , pin_valve_exhale : pwm_chan_exhale};
#else
// NOTE defaults to whatever the frequency of the pin is for non-ESP32 boards.  Changing frequency is possible but complicated
    pinMode(pin_valve_inhale, OUTPUT);
    pinMode(pin_valve_exhale, OUTPUT);
#endif

    pinMode(pin_valve_air_in, OUTPUT);
    pinMode(pin_valve_o2_in, OUTPUT);
    pinMode(pin_valve_purge, OUTPUT);
    pinMode(pin_valve_atmosphere, OUTPUT);

    pinMode(pin_pressure_air_supply, INPUT);
    pinMode(pin_pressure_air_regulated, INPUT);
    pinMode(pin_pressure_buffer, INPUT);
    pinMode(pin_pressure_inhale, INPUT);
    pinMode(pin_pressure_patient, INPUT);
    pinMode(pin_temperature_buffer, INPUT);
#ifdef HEV_FULL_SYSTEM
    pinMode(pin_pressure_o2_supply, INPUT);
    pinMode(pin_pressure_o2_regulated, INPUT);
    pinMode(pin_pressure_diff_patient, INPUT);
#endif

    pinMode(pin_led_green, OUTPUT);
    pinMode(pin_led_yellow, OUTPUT);
    pinMode(pin_led_red, OUTPUT);

    pinMode(pin_buzzer, OUTPUT);
    pinMode(pin_button_0, INPUT);

    while (!Serial) ;
    comms.beginSerial();

}

void loop()
{
    // buzzer
    // tone(pin, freq (Hz), duration);

    bool vin_air, vin_o2, vpurge ;
    float vinhale, vexhale;
    ValvesController *valves_controller = breathing_loop.getValvesController();
    valves_controller->getValves(vin_air, vin_o2, vinhale, vexhale, vpurge);
    data.readback_valve_air_in = vin_air;
    data.readback_valve_o2_in = vin_o2;
    data.readback_valve_inhale = vinhale;
    data.readback_valve_exhale = vexhale;
    data.readback_valve_purge = vpurge;

    data.fsm_state = breathing_loop.getFsmState();
    data.readback_mode = breathing_loop.getVentilationMode();
    readings readings_avgs = breathing_loop.getReadingAverages();
    data.pressure_air_supply = readings_avgs.pressure_air_supply;
    data.pressure_air_regulated = readings_avgs.pressure_air_regulated;
    data.pressure_buffer = readings_avgs.pressure_buffer;
    data.pressure_inhale = readings_avgs.pressure_inhale;
    data.pressure_patient = readings_avgs.pressure_patient;
    data.temperature_buffer = readings_avgs.temperature_buffer;
    data.pressure_o2_supply = readings_avgs.pressure_o2_supply;
    data.pressure_o2_regulated = readings_avgs.pressure_o2_regulated;
    data.pressure_diff_patient = readings_avgs.pressure_diff_patient;

    breathing_loop.FSM_assignment();
    breathing_loop.FSM_breathCycle();

    unsigned long tnow = millis();
    if(tnow > report_time + report_timeout)
    {
        plSend.setType(PAYLOAD_TYPE::DATA);
        plSend.setData(&data);
        comms.writePayload(plSend);
        report_time = tnow;
    }
    // per cycle sender
    comms.sender();
    // per cycle receiver
    comms.receiver();

    if(comms.readPayload(plReceive)){
      if (plReceive.getType() == PAYLOAD_TYPE::CMD) {
          ui_loop.doCommand(plReceive.getCmd());
          plReceive.setType(PAYLOAD_TYPE::UNSET);
      }
    }

    breathing_loop.updateReadings(); 
}
