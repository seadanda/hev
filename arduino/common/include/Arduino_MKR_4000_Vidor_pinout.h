
// arduino MKR 4000 Vidor
#define BOARD "VIDOR"
    // pwm pins
const int pin_valve_air_in     = 1;
const int pin_valve_o2_in      = 2;
const int pin_valve_inhale     = 3;  // formerly pin_valve_out
const int pin_valve_exhale     = 4;  // formerly pin_valve_scavenge
const int pin_valve_purge      = 5;
const int pin_valve_atmosphere = 6;

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
const int pin_led_0          = 7;
const int pin_led_1          = 8;
const int pin_led_2          = 9;

    // buzzer
const int pin_buzzer         = 0;

    // buttons
const int pin_button_0       = 14;

const int pwm_resolution = 8; // 8 bit resolution; up to 12 possible