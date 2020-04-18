#include <Arduino.h>
// #include <MemoryFree.h>
#include <Wire.h>
#include <Adafruit_MCP9808.h>
#include <INA.h>
#include "CommsControl.h"
#include "BreathingLoop.h"
#include "ValvesController.h"
#include "UILoop.h"
#include "AlarmLoop.h"
#include "common.h"

int ventilation_mode = HEV_MODE_PS;

const uint16_t report_freq = 5 ; // in Hz
const uint16_t update_freq = 100 ; // in Hz

uint32_t report_time = 0;
uint32_t report_timeout = static_cast<uint32_t>(1000 * report_freq);

uint16_t report_cnt = 0;
 
float working_pressure = 1;             //?
float inspiratory_minute_volume = 6000; // ml/min
float respiratory_rate = 15;            //  10-40 +-1 ;aka breaths_per_min
float inspiratory_pressure = 10;        // 10-80 cmH2O +-1
//float tidal_volume = 200; // calc 200-1500ml +- 100
float inspiratory_time = 1.0; // 0.4-1.5s +-0.1
float pause_time = 1.0;       // range?
//float expiratory_time ; // calc
float expiratory_minute_volume; // calc?? same as inspiratory_minute_volume?
float trigger_sensitivity;

// comms
data_format data;
CommsControl comms;
Payload plReceive;
Payload plSend;

// loops
BreathingLoop breathing_loop;
UILoop        ui_loop(&breathing_loop);
AlarmLoop     alarm_loop;

bool start_fsm = false;

// calculations
float calcTidalVolume()
{
    return inspiratory_minute_volume / respiratory_rate;
}

float calcExpirationTime()
{
    float total_respiratory_time = 60.0 / respiratory_rate;
    // total = expire + inspire + pause
    return (total_respiratory_time - inspiratory_time - pause_time);
}

float calcExpiratoryMinuteVolume()
{
    // probably need to calculate this from readings
    return 0;
}

void setup()
{
#ifdef CHIP_ESP32
    ledcSetup(pwm_chan_inhale, pwm_frequency, pwm_resolution);
    ledcSetup(pwm_chan_exhale, pwm_frequency, pwm_resolution);
    ledcAttachPin(pin_valve_inhale , pwm_chan_inhale);  
    ledcAttachPin(pin_valve_exhale , pwm_chan_exhale);  
    pin_to_chan[pin_valve_inhale] = pwm_chan_inhale;
    pin_to_chan[pin_valve_exhale] = pwm_chan_exhale;

// map<int,int> pin_to_chan; // = { pin_valve_inhale : pwm_chan_inhale , pin_valve_exhale : pwm_chan_exhale};
#else
// NOTE defaults to whatever the frequency of the pin is for non-ESP32 boards.  Changing frequency is possible but complicated
    pinMode(pin_valve_inhale, OUTPUT);
    pinMode(pin_valve_exhale, OUTPUT);
#endif

    pinMode(pin_valve_air_in, OUTPUT);
    pinMode(pin_valve_o2_in, OUTPUT);
    pinMode(pin_valve_purge, OUTPUT);
    pinMode(pin_valve_atmosphere, OUTPUT);

    pinMode(pin_pressure_air_supply, INPUT);
    pinMode(pin_pressure_air_regulated, INPUT);
    pinMode(pin_pressure_buffer, INPUT);
    pinMode(pin_pressure_inhale, INPUT);
    pinMode(pin_pressure_patient, INPUT);
    pinMode(pin_temp, INPUT);
#ifdef HEV_FULL_SYSTEM
    pinMode(pin_p_o2_supply, INPUT);
    pinMode(pin_p_o2_regulated, INPUT);
    pinMode(pin_p_diff_patient, INPUT);
#endif

    pinMode(pin_led_0, OUTPUT);
    pinMode(pin_led_1, OUTPUT);
    pinMode(pin_led_2, OUTPUT);

    pinMode(pin_buzzer, OUTPUT);
    pinMode(pin_button_0, INPUT);

    while (!Serial) ;
    comms.beginSerial();

}

void loop()
{
    // buzzer
    // tone(pin, freq (Hz), duration);

    data.fsm_state = breathing_loop.getFsmState();
    data.readback_mode = breathing_loop.getLabCycleMode();
    data.pressure_buffer = analogRead(pin_pressure_buffer);
    data.pressure_inhale = analogRead(pin_pressure_inhale);

    bool vin_air, vin_o2, vpurge ;
    float vinhale, vexhale;
    ValvesController *valves_controller = breathing_loop.getValvesController();
    valves_controller->getValves(vin_air, vin_o2, vinhale, vexhale, vpurge);
    data.readback_valve_air_in = vin_air;
    data.readback_valve_o2_in = vin_o2;
    data.readback_valve_inhale = vinhale;
    data.readback_valve_exhale = vexhale;
    data.readback_valve_purge = vpurge;
    // data.pressure_o2_supply = freeMemory() & 0xFFFF;
    // data.pressure_o2_regulated = freeMemory() >> 16;
    // TODO ; add to dataFormat
    // data.readback_valve_atmosphere = vpurge;

    breathing_loop.FSM_assignment();
    breathing_loop.FSM_breathCycle();

    // writing data to sending ring buffer is defined by frequency
    // TODO: programmable changing of the report_timeout
    if (millis() > report_time + report_timeout) {
        plSend.setType(PAYLOAD_TYPE::DATA);
        plSend.setData(&data);
        comms.writePayload(plSend);
        report_time = static_cast<uint32_t>(millis());
    }
    // per cycle sender
    comms.sender();

    // per cycle receiver
    comms.receiver();
    if(comms.readPayload(plReceive)){
      if (plReceive.getType() == PAYLOAD_TYPE::CMD) {
          ui_loop.doCommand(plReceive.getCmd());
          plReceive.setType(PAYLOAD_TYPE::UNSET);
      }
    }

    breathing_loop.updatePressures(); //delay(1000/update_freq);
}
