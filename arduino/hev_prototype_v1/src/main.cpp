#include <Arduino.h>
#include "common.h"
#ifdef CHIP_ESP32
#include <WiFi.h>
#endif
// #include <MemoryFree.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_MCP9808.h>
#include <INA.h>
#include "CommsControl.h"
#include "BreathingLoop.h"
#include "ValvesController.h"
#include "UILoop.h"
#include "AlarmLoop.h"

int ventilation_mode = HEV_MODE_PS;

uint8_t prev_state = LOW;
uint32_t report_timeout = 50; //ms
uint32_t report_time = 0;


// comms
// fast_data_format data;
CommsControl comms;

// loops
BreathingLoop breathing_loop;
AlarmLoop     alarm_loop;
UILoop        ui_loop(&breathing_loop, &alarm_loop, &comms);


void setup()
{
#ifdef CHIP_ESP32
    WiFi.mode(WIFI_OFF);
    btStop();
    ledcSetup(pwm_chan_inhale, pwm_frequency, pwm_resolution);
    ledcSetup(pwm_chan_exhale, pwm_frequency, pwm_resolution);
    ledcSetup(3, 2000, pwm_resolution);
    ledcAttachPin(pin_buzzer, 3);  
    ledcAttachPin(pin_valve_inhale , pwm_chan_inhale);  
    ledcAttachPin(pin_valve_exhale , pwm_chan_exhale);  

// map<int,int> pin_to_chan; // = { pin_valve_inhale : pwm_chan_inhale , pin_valve_exhale : pwm_chan_exhale};

    pinMode(pin_pressure_air_supply, INPUT);
    pinMode(pin_pressure_o2_supply, INPUT);
#else
// NOTE defaults to whatever the frequency of the pin is for non-ESP32 boards.  Changing frequency is possible but complicated
    pinMode(pin_valve_inhale, OUTPUT);
    pinMode(pin_valve_exhale, OUTPUT);
#endif

    pinMode(pin_valve_air_in, OUTPUT);
    pinMode(pin_valve_o2_in, OUTPUT);
    pinMode(pin_valve_purge, OUTPUT);

    pinMode(pin_pressure_air_regulated, INPUT);
    pinMode(pin_pressure_buffer, INPUT);
    pinMode(pin_pressure_inhale, INPUT);
    pinMode(pin_pressure_patient, INPUT);
    pinMode(pin_temperature_buffer, INPUT);
    pinMode(pin_pressure_o2_regulated, INPUT);
    pinMode(pin_pressure_diff_patient, INPUT);

    pinMode(pin_led_green, OUTPUT);
    pinMode(pin_led_yellow, OUTPUT);
    pinMode(pin_led_red, OUTPUT);

    //pinMode(pin_buzzer, OUTPUT);

    comms.beginSerial();
}

void loop()
{

    breathing_loop.FSM_assignment();
    breathing_loop.FSM_breathCycle();

    ui_loop.reportFastReadings();
    ui_loop.reportReadbackValues();
    ui_loop.reportCycleReadings();

    // per cycle sender
    comms.sender();
    // per cycle receiver
    comms.receiver();

    // // check any received payload
    ui_loop.receiveCommands();
    // run value readings
    breathing_loop.updateReadings();
    breathing_loop.updateRawReadings();

}
