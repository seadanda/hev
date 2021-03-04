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
#include "SystemUtils.h"
#include "AlarmLoop.h"
#include "UILoop.h"

// System temp sensor
Adafruit_MCP9808 tempsensor = Adafruit_MCP9808();
// I2C devices
INA_Class      INA;    
TwoWire I2CMCP9808 = TwoWire(0);

// comms
CommsControl comms;

// loops
BreathingLoop breathing_loop;
AlarmLoop     alarm_loop;
UILoop        ui_loop(&breathing_loop, &alarm_loop, &comms);

SystemUtils   sys_utils;

#define STATUS_CHECK_COUNTS 10000
uint16_t loop_count = 0;
uint32_t loop_start = 0;
uint32_t loop_start_sum = 0;
status_format status;

void setup()
{
#ifdef CHIP_ESP32
    WiFi.mode(WIFI_OFF);
    btStop();
    ledcSetup(pwm_chan_inhale, 500, pwm_resolution); // 500 Hz for proportional valves
#ifdef EXHALE_VALVE_PROPORTIONAL
    ledcSetup(pwm_chan_exhale, 500, pwm_resolution); // 500 Hz for proportional valves
    ledcAttachPin(pin_valve_exhale , pwm_chan_exhale);  
#else
    pinMode(pin_valve_exhale, OUTPUT);
#endif
    ledcSetup(3, 2000, pwm_resolution);
    ledcAttachPin(pin_buzzer, 3);  
    ledcAttachPin(pin_valve_inhale , pwm_chan_inhale);  

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
    pinMode(pin_o2_sensor, INPUT);

    pinMode(pin_led_green, OUTPUT);
    pinMode(pin_led_yellow, OUTPUT);
    pinMode(pin_led_red, OUTPUT);

    // use channel for 4 of PWM generator to output calculated FiO2
    ledcSetup(pwm_chan_debug, pwm_frequency_debug, pwm_resolution_debug); // channel 4, Frequency 500, 8bit resolution
    ledcAttachPin(pin_spare_2, pwm_chan_debug);  

    //pinMode(pin_buzzer, OUTPUT);

    comms.beginSerial();
    setGlobalComms(&comms);

    Wire.begin(22, 23);
    I2CMCP9808.begin(22, 23);

    sys_utils.setupTempSensor(&tempsensor, &I2CMCP9808);
    setSystemUtils(&sys_utils);

    bool foundINADevices = false;
    int8_t ntries = 3; 
    uint8_t devicesFound = INA.begin(1, 500000); // Set to an expected 1 Amp maximum and a 100000 microOhm resistor
    while ((INA.begin(1, 500000) == 0) && ntries > 0)
    {
        delay(1000); 
        ntries--;
    }                
    if (ntries > 0)
        foundINADevices = true;
    if (foundINADevices){
        INA.setBusConversion(8500);            // Maximum conversion time 8.244ms
        INA.setShuntConversion(8500);          // Maximum conversion time 8.244ms
        INA.setAveraging(128);                 // Average each reading n-times
        INA.setMode(INA_MODE_CONTINUOUS_BOTH); // Bus/shunt measured continuously
        //INA.AlertOnBusOverVoltage(true, 5000); // Trigger alert if over 5V on bus
        breathing_loop.getValvesController()->setupINA(&INA, devicesFound);
    }
    loop_start = loop_start_sum = micros();
}

void loop()
{
    breathing_loop.assignBreatheFSM();
    breathing_loop.doBreatheFSM();
    breathing_loop.doFillFSM(); // assignFillFSM() is in doBreatheFSM()

    alarm_loop.fireAlarms();

    ui_loop.reportFastReadings();
    ui_loop.reportReadbackValues();
    ui_loop.reportCycleReadings();
    ui_loop.reportAlarms();
    ui_loop.reportIVTReadings();
    ui_loop.reportDebugValues();  // data duplicated to fast and readback
    ui_loop.reportTargets();

    // per cycle receiver
    comms.receiver();
    // per cycle sender
    comms.sender();

    // // check any received payload
    ui_loop.receiveCommands();
    // run value readings
    breathing_loop.updateReadings();
    breathing_loop.updateRawReadings();
    breathing_loop.updateCycleReadings();
    breathing_loop.updateCalculations();
    breathing_loop.updateO2Concentration();
    // update alarm values
    // TODO assign more values
    alarm_loop.updateValues(breathing_loop.getReadingAverages(), breathing_loop.getCycleReadings());

    // check uC performance of past N cycles
    uint32_t duration = micros() - loop_start;
    status.loop_duration_max = duration > status.loop_duration_max ? duration : status.loop_duration_max;
    if (loop_count++ >= STATUS_CHECK_COUNTS) {
        Payload pl;
        status.timestamp = millis();
        status.loop_duration   = static_cast<float>(micros() - loop_start_sum) / (1000 * STATUS_CHECK_COUNTS); // send in ms
        status.loop_duration_max /= 1000; // in ms
        status.dropped_send    = comms.countDroppedSend();
        status.dropped_receive = comms.countDroppedReceive();
        status.buffer_alarm    = comms.countBufferSize(PRIORITY::ALARM_ADDR);
        status.buffer_cmd      = comms.countBufferSize(PRIORITY::CMD_ADDR);
        status.buffer_data     = comms.countBufferSize(PRIORITY::DATA_ADDR);
        pl.setPayload(PRIORITY::ALARM_ADDR, reinterpret_cast<void *>(&status), sizeof (status));
        comms.writePayload(pl);

        loop_start_sum = micros();
        loop_count = 0;
        status.loop_duration_max = 0;
    }
    loop_start = micros();
}
