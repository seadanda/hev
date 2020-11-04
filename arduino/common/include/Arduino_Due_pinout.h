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


// Arduino Due
#define BOARD "DUE"
#define HEV_FULL_SYSTEM
    // pwm pins
const int pin_valve_air_in     = 11;
const int pin_valve_o2_in      = 10;
const int pin_valve_inhale     = 6;  // formerly pin_valve_out
const int pin_valve_exhale     = 5;  // formerly pin_valve_scavenge
const int pin_valve_purge      = 3;
const int pin_o2_sensor = 4;

    // adcs
const int pin_pressure_air_supply   = A0;
const int pin_pressure_air_regulated= A1;
const int pin_pressure_buffer       = A2;
const int pin_pressure_inhale       = A3;
const int pin_pressure_patient      = A4;
const int pin_temperature_buffer    = A5;
const int pin_pressure_o2_supply    = A6; 
const int pin_pressure_o2_regulated = A7;
const int pin_pressure_diff_patient = A8;
    // leds
const int pin_led_green          = 0;
const int pin_led_yellow          = 1;
const int pin_led_red          = 2;

    // buzzer
const int pin_buzzer         = 9;

const int pin_spare_1       = 13;

    // lcd
const int pin_lcd_rs         = 22;
const int pin_lcd_en         = 24;
const int pin_lcd_d4         = 26;
const int pin_lcd_d5         = 28;
const int pin_lcd_d6         = 30;
const int pin_lcd_d7         = 32;

const int pwm_resolution = 12; // 8 bit resolution; up to 12 possible