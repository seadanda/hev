#include "AudioVisualController.h"
#include "common.h"

AudioVisualController::AudioVisualController()
{
    _led_green .pin = pin_led_green ;
    _led_yellow.pin = pin_led_yellow;
    _led_red   .pin = pin_led_red   ;
    _buzzer    .pin = pin_buzzer    ;
}

AudioVisualController::~AudioVisualController()
{ ; }
