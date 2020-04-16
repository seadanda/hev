// Node MCU 32s
#define BOARD "NODEMCU32S"
#define CHIP_ESP32
#define HEV_FULL_SYSTEM
    // digital pins
const int pin_valve_air_in        = 25;   // DAC1  // A18
const int pin_valve_o2_in         = 5;   // STRAPPING PIN (prefer as output / high-Z)
const int pin_valve_purge         = 18;
const int pin_valve_atmosphere    = 26;// DAC2;  // A19

    // pwm pins
const int pin_valve_inhale        = 21;  // formerly valve_out
const int pin_valve_exhale        = 19;  // formerly valve_scavenge

    // adcs
const int pin_p_air_supply       = A0; // IO36  // INPUT ONLY
const int pin_p_air_regulated    = A3; // IO39  // INPUT ONLY
const int pin_p_buffer           = A6; // IO34  // INPUT ONLY
const int pin_p_inhale           = A7; // IO35  // INPUT ONLY
const int pin_p_patient          = A4; // IO32
const int pin_temp               = A5; // IO33
const int pin_p_o2_supply       = A17; // IO27
const int pin_p_o2_regulated    = A16; // IO14 
const int pin_p_diff_patient    = A10;  // IO4

    // leds
const int pin_led_0          = 17;
const int pin_led_1          = 16;
const int pin_led_2          = 12; // A15// STRAPPING PIN (prefer as output / high-Z)

    // buzzer
const int pin_buzzer         =  2;   // STRAPPING PIN (prefer as output / High-Z)

    // buttons
const int pin_button_0       = 13;

    // SPARES - this and i2c and dac are spare
const int pin_spare_adc         = A13;  // IO15  // STRAPPING PIN (prefer as output / high-Z)
    // i2c
const int pin_scl = 23;
const int pin_sda = 22;

// For ESP32 PWM needs an associated channel; Channel is manipulated not pin directly
// PWM channels
const int pwm_chan_inhale = 0;
const int pwm_chan_exhale = 1;
const int pwm_resolution = 8; // 8 bit resolution; up to 16 possible
const int pwm_frequency  = 900; // frequency in Hz
