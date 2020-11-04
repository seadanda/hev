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



// arduino MKR 4000 Vidor
#define BOARD "VIDOR"
    // pwm pins
const int pin_valve_air_in     = 1;
const int pin_valve_o2_in      = 2;
const int pin_valve_inhale     = 3;  // formerly pin_valve_out
const int pin_valve_exhale     = 4;  // formerly pin_valve_scavenge
const int pin_valve_purge      = 5;
const int pin_o2_sensor = 6;

    // adcs
// const int pin_pressure_air_supply     = A0;
// const int pin_pressure_o2_supply      = A6;
const int pin_pressure_air_regulated  = A0;
const int pin_pressure_buffer         = A1;
const int pin_pressure_inhale         = A2;
const int pin_pressure_patient        = A3;
const int pin_temperature_buffer      = A4;
const int pin_pressure_o2_regulated   = A5;
const int pin_pressure_diff_patient   = A6;

    // leds
const int pin_led_green          = 7;
const int pin_led_yellow          = 8;
const int pin_led_red          = 9;

    // buzzer
const int pin_buzzer         = 0;

    // buttons
const int pin_spare_1       = 14;

const int pwm_resolution = 8; // 8 bit resolution; up to 12 possible