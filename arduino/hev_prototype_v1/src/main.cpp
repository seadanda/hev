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

//    while (!Serial) ;
    comms.beginSerial();
}

void loop()
{
    // buzzer
    // tone(pin, freq (Hz), duration);

    // bool vin_air, vin_o2, vpurge ;
    // float vinhale, vexhale;
    // ValvesController *valves_controller = breathing_loop.getValvesController();
    // valves_controller->getValves(vin_air, vin_o2, vinhale, vexhale, vpurge);

    // readings<uint16_t> readings_avgs = breathing_loop.getReadingAverages();
    // data.timestamp              = static_cast<uint32_t>(readings_avgs.timestamp);
    // data.pressure_air_supply    = readings_avgs.pressure_air_supply;
    // data.pressure_air_regulated = readings_avgs.pressure_air_regulated;
    // data.pressure_buffer        = readings_avgs.pressure_buffer;
    // data.pressure_inhale        = readings_avgs.pressure_inhale;
    // data.pressure_patient       = readings_avgs.pressure_patient;
    // data.temperature_buffer     = readings_avgs.temperature_buffer;
    // data.pressure_o2_supply     = readings_avgs.pressure_o2_supply;
    // data.pressure_o2_regulated  = readings_avgs.pressure_o2_regulated;
    // data.pressure_diff_patient  = readings_avgs.pressure_diff_patient;

    // data.fsm_state              = breathing_loop.getFsmState();
    // data.ventilation_mode          = breathing_loop.getVentilationMode();

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
}
