// Arduino Yun
#define BOARD "YUN"
    // pwm pins
const int pin_valve_air_in     = 11;
const int pin_valve_o2_in      = 10;
const int pin_valve_inhale     = 6;  // formerly pin_valve_out
const int pin_valve_exhale     = 5;  // formerly pin_valve_scavenge
const int pin_valve_purge      = 3;
const int pin_valve_atmosphere = 4;

    // adcs
const int pin_p_air_supply     = A0;
const int pin_p_air_regulated  = A1;
const int pin_p_buffer         = A2;
const int pin_p_inhale         = A3;
const int pin_p_patient        = A4;
const int pin_temp             = A5;
// const int pin_p_o2_supply      = A6;
// const int pin_p_o2_regulated   = A7;
// const int pin_p_diff_patient   = A8;

    // leds
const int pin_led_0          = 0;
const int pin_led_1          = 1;
const int pin_led_2          = 2;

    // buzzer
const int pin_buzzer         = 9;

const int pin_button_0       = 13;

const int pwm_resolution = 8; // 8 bit resolution