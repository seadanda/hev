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


// ESP32 HUZZAH
#define BOARD "HUZZAH32"
#define CHIP_ESP32
#define HEV_FULL_SYSTEM
    // digital pins
const int pin_valve_air_in     = 13;  // A12
const int pin_valve_o2_in      =  5;  // SCK
const int pin_valve_purge      = 18;  // MOSI
const int pin_o2_sensor = 12;  // A11 / OUTPUT ONLY

    // pwm pins
const int pin_valve_inhale     = 21;  // GPIO ONLY
const int pin_valve_exhale     = 19;  // MISO

    // adcs
const int pin_pressure_air_supply    = A4; // 36 / INPUT ONLY
const int pin_pressure_air_regulated = A3; // 39 / INPUT ONLY
const int pin_pressure_buffer        = A2; // 34 / INPUT ONLY
const int pin_pressure_inhale        = A0; // DAC2 / 26 ****
const int pin_pressure_patient       = A7; // 32
const int pin_temperature_buffer     = A9; // 33
const int pin_pressure_o2_supply     = A10; // 27 
const int pin_pressure_o2_regulated  = A6;  // 14
const int pin_pressure_diff_patient  = A5;  // 4

    // leds
const int pin_led_green          = 17; // TX
const int pin_led_yellow          = 16; // RX
const int pin_led_red          = 15; // A13 ****

    // buzzer
const int pin_buzzer         = 22; // I2C SDA

    // buttons
const int pin_spare_1       = 23; // I2C SCL

    // spare
// const int pin spare_adc    = A1; // 25 DAC1

// For ESP32 PWM needs an associated channel; Channel is manipulated not pin directly
// PWM channels
const int pwm_chan_inhale = 0;
const int pwm_chan_exhale = 1;
const int pwm_resolution = 16; // 8 bit resolution; up to 16 possible
const int pwm_frequency  = 900; // frequency in Hz