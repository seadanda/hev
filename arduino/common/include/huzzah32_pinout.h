// ESP32 HUZZAH
#define BOARD "HUZZAH32"
#define CHIP_ESP32
#define HEV_FULL_SYSTEM
    // digital pins
const int pin_valve_air_in     = 13;  // A12
const int pin_valve_o2_in      =  5;  // SCK
const int pin_valve_purge      = 18;  // MOSI
const int pin_valve_atmosphere = 12;  // A11 / OUTPUT ONLY

    // pwm pins
const int pin_valve_inhale     = 21;  // GPIO ONLY
const int pin_valve_exhale     = 19;  // MISO

    // adcs
const int pin_pressure_air_supply    = A4; // 36 / INPUT ONLY
const int pin_pressure_air_regulated = A3; // 39 / INPUT ONLY
const int pin_pressure_buffer        = A2; // 34 / INPUT ONLY
const int pin_pressure_inhale        = A0; // DAC2 / 26 ****
const int pin_pressure_patient       = A7; // 32
const int pin_temp            = A9; // 33
const int pin_p_o2_supply     = A10; // 27 
const int pin_p_o2_regulated  = A6;  // 14
const int pin_p_diff_patient  = A5;  // 4

    // leds
const int pin_led_0          = 17; // TX
const int pin_led_1          = 16; // RX
const int pin_led_2          = 15; // A13 ****

    // buzzer
const int pin_buzzer         = 22; // I2C SDA

    // buttons
const int pin_button_0       = 23; // I2C SCL

    // spare
// const int pin spare_adc    = A1; // 25 DAC1

// For ESP32 PWM needs an associated channel; Channel is manipulated not pin directly
// PWM channels
const int pwm_chan_inhale = 0;
const int pwm_chan_exhale = 1;
const int pwm_resolution = 8; // 8 bit resolution; up to 16 possible
const int pwm_frequency  = 900; // frequency in Hz