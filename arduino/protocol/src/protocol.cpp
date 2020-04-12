#include <Arduino.h>
#include "commsControl.h"

#define LED_BLUE   5
#define LED_GREEN  7
#define LED_RED    3

#define BTN 8

payload plReceive_;
payload plSend_;
commsControl comms_;
dataFormat data_;
alarmFormat alarm_;

int currentState_  = 0;
int previousState_ = 0;

int led_ = 0;
bool blue_ = false;
bool green_ = false;
bool red_ = false;

bool enabled_ = false;

uint32_t lastTime_ = 0;

uint32_t offset_ = 10;

// dirty function to switch one of the LEDs
void switchLED(int led) {
    int state = HIGH;
    switch (led) {
        case LED_BLUE:
            if (blue_)
                state = LOW;
            blue_ = !blue_;
            break;
        case LED_RED:
            if (red_)
                state = LOW;
            red_ = !red_;
            break;
        case LED_GREEN:
            if (green_)
                state = LOW;
            green_ = !green_;
        break;
    }
    digitalWrite(led, state);
}


void setup() {
    plSend_.setType(payloadType::payloadData);

    // initialize digital pin LED_BUILTIN as an output.
    pinMode(LED_BLUE, OUTPUT);
    pinMode(LED_GREEN, OUTPUT);
    pinMode(LED_RED, OUTPUT);

    pinMode(BTN, INPUT);

    // initialize comms connection
    comms_.beginSerial();
}

void loop() {

    // testing increase of values to be sent
    // will only increase the count on the button release (reasons)
    currentState_ = digitalRead(BTN);
    if ( currentState_ != previousState_) {
        if (currentState_ != HIGH) {
            switchLED(LED_BLUE);
            // counter increase on button press
            data_.fsm_state += 1;
            plSend_.setData(&data_);
            // register new data in comms
            comms_.writePayload(plSend_);
        }
        previousState_ = currentState_;
    }

    if (enabled_ & (millis() > (lastTime_ + offset_)))
    {
        lastTime_ = millis();

        plSend_.getData()->readback_valve_air_in = static_cast<uint8_t>((lastTime_ >> 24) & 0xFF);
        plSend_.getData()->readback_valve_o2_in  = static_cast<uint8_t>((lastTime_ >> 16) & 0xFF);
        plSend_.getData()->readback_valve_inhale = static_cast<uint8_t>((lastTime_ >> 8 ) & 0xFF);
        plSend_.getData()->readback_valve_exhale = static_cast<uint8_t>((lastTime_ >> 0 ) & 0xFF);

        switchLED(LED_BLUE);
        plSend_.setType(payloadType::payloadData);
        plSend_.getData()->fsm_state += 1;
        comms_.writePayload(plSend_);
    }

    // per cycle sender
    comms_.sender();
    // per cycle receiver
    comms_.receiver();

    if (comms_.readPayload(plReceive_)) {

        switch (plReceive_.getType()) {
            case payloadType::payloadCmd:
                if (plReceive_.getCmd()->cmdCode % 2 == 0) {
                    enabled_ = false;
                } else {
                    enabled_ = true;
                }
                offset_ = plReceive_.getCmd()->param;

                alarm_.alarmCode = plReceive_.getCmd()->cmdCode;
                alarm_.param     = millis() & 0xFFFFFFFF;
                plSend_.setAlarm(&alarm_);
                comms_.writePayload(plSend_);
                break;
            default:
                break;
        }

        plReceive_.setType(payloadType::payloadUnset);
    }
}
