// Arduino Uno
#define BOARD "UNO"
    // pwm pins
const int pin_valve_air_in     = 11;
const int pin_valve_o2_in      = 10;
const int pin_valve_inhale     = 3;  // lab14
const int pin_valve_exhale     = 9;  // lab14
const int pin_valve_purge      = 6;
const int pin_spare_1 = 4;

    // adcs
const int pin_pressure_air_supply     = A2;
const int pin_pressure_air_regulated  = A0; //lab14
const int pin_pressure_buffer         = A1; //lab14
const int pin_pressure_inhale         = A3;
const int pin_pressure_patient        = A4;
const int pin_temperature_buffer      = A5;
// const int pin_pressure_o2_supply      = A6;
// const int pin_pressure_o2_regulated   = A7;
// const int pin_pressure_diff_patient   = A8;

    // leds
const int pin_led_green          = 0;
const int pin_led_yellow          = 1;
const int pin_led_red          = 2;

    // buzzer
const int pin_buzzer         = 5;

const int pin_button_0       = 13;

const int pwm_resolution = 8; // 8 bit resolution