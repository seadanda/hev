#include <Arduino.h>
// #include <MemoryFree.h>

#include "commsControl.h"
#include "test_hw_loop.h"
#include "common.h"

int ventilation_mode = HEV_MODE_PS;

const uint16_t report_freq = 5 ; // in Hz
const uint16_t update_freq = 100 ; // in Hz

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
dataFormat data;
commsControl comms;
payload plReceive;
payload plSend;

bool start_fsm = false;

// calculations
float calc_tidal_volume()
{
    return inspiratory_minute_volume / respiratory_rate;
}

float calc_expiration_time()
{
    float total_respiratory_time = 60.0 / respiratory_rate;
    // total = expire + inspire + pause
    return (total_respiratory_time - inspiratory_time - pause_time);
}

float calc_expiratory_minute_volume()
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

    data.fsm_state = getFsmState();
    data.readback_mode = getLabCycleMode();
    data.pressure_buffer = analogRead(pin_pressure_buffer);
    data.pressure_inhale = analogRead(pin_pressure_inhale);

    bool vin_air, vin_o2, vpurge, vatmos;
    float vinhale, vexhale;
    getValves(vin_air, vin_o2, vinhale, vexhale, vpurge, vatmos);
    data.readback_valve_air_in = vin_air;
    data.readback_valve_o2_in = vin_o2;
    data.readback_valve_inhale = vinhale;
    data.readback_valve_exhale = vexhale;
    data.readback_valve_purge = vpurge;
    // data.pressure_o2_supply = freeMemory() & 0xFFFF;
    // data.pressure_o2_regulated = freeMemory() >> 16;
    // TODO ; add to dataFormat
    // data.readback_valve_atmosphere = vpurge;

    FSM_assignment();
    FSM_breath_cycle();

    report_cnt++;
    if(report_cnt % (update_freq/report_freq) == 0)
    {
        plSend.setType(payloadType::payloadData);
        plSend.setData(&data);
        comms.writePayload(plSend);
    }
    // per cycle sender
    comms.sender();
    // per cycle receiver
    
    comms.receiver();

    uint8_t cmdCode = 0;
    if(comms.readPayload(plReceive)){
      if (plReceive.getType() == payloadType::payloadCmd) {
          cmdCode = (plReceive.getCmd()->cmdCode);
          plReceive.setType(payloadType::payloadUnset);
      }
    }

    switch(cmdCode){
        case 0x1 : do_start(); 
        break;
        case 0x2 : do_stop(); 
        break;
        default:
        break;
    }
    delay(1000/update_freq);
}
