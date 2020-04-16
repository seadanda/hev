
// Arduino Nano 33 IOT
#define BOARD "NANO33IOT"
    // digital pins
const int pin_valve_air_in     = 4;
const int pin_valve_o2_in      = 5;
const int pin_valve_purge      = 6;
const int pin_valve_atmosphere = 7;

    // pwm pins
const int pin_valve_inhale     = 2;  // formerly pin_valve_out
const int pin_valve_exhale     = 3;  // formerly pin_valve_scavenge

    // adcs
const int pin_p_air_supply     = A0;
const int pin_p_air_regulated  = A1;
const int pin_p_buffer         = A2;
const int pin_p_inhale         = A3;
const int pin_p_patient        = A4;
const int pin_temp             = A5;
const int pin_p_o2_supply      = A6;
// const int pin_p_o2_regulated   = A7;
// const int pin_p_diff_patient   = A8;

    // leds
const int pin_led_0          = 8;
const int pin_led_1          = 9;
const int pin_led_2          = 10;

    // buzzer
const int pin_buzzer         = 11;

    // buttons
const int pin_button_0       = 12;

const int pwm_resolution = 8; // 8 bit resolution; up to 12 possible
