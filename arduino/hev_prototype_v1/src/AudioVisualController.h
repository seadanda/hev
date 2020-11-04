// © Copyright CERN, Riga Technical University and University of Liverpool 2020.
// All rights not expressly granted are reserved. 
// 
// This file is part of hev-sw.
// 
// hev-sw is free software: you can redistribute it and/or modify it under
// the terms of the GNU General Public Licence as published by the Free
// Software Foundation, either version 3 of the Licence, or (at your option)
// any later version.
// 
// hev-sw is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public Licence
// for more details.
// 
// You should have received a copy of the GNU General Public License along
// with hev-sw. If not, see <http://www.gnu.org/licenses/>.
// 
// The authors would like to acknowledge the much appreciated support
// of all those involved with the High Energy Ventilator project
// (https://hev.web.cern.ch/).


#ifndef AUDIOVISUALCONTROLLER_H
#define AUDIOVISUALCONTROLLER_H

#include <Arduino.h>

// ms, used to calculate update frequency
#define AV_STATE_DURATION  1000

enum AV_STATE : bool {
    OFF =  LOW,
    ON  = HIGH
};

enum AV_STYLE {
    PERM_OFF  =  1,
    OSCIL     =  2,
    PERM_ON   =  3
};

enum AV_FREQUENCY : uint32_t {
    SLOW        =  1,
    NORMAL      =  2,
    FAST        =  4,
    VERY_FAST   =  10
};

// simple struct to control state of the AV
struct av {
    int pin             = -1;
    AV_STATE state      = AV_STATE::OFF;
    AV_STYLE style      = AV_STYLE::PERM_OFF;
    AV_FREQUENCY freq   = AV_FREQUENCY::NORMAL;
    uint32_t freq_cntr  = 0;

    // calculates duration from the provided update frequency
    uint32_t duration() { return static_cast<uint32_t>(AV_STATE_DURATION / freq); }
    // apply state of the AV
    void applyState() { digitalWrite(pin, state); }
    // flip state of the AV
    void flipState()  { if (state == AV_STATE::OFF) {state = AV_STATE::ON; } else {state = AV_STATE::OFF; } }

    void update(uint32_t &tnow, uint32_t &vis_time) {
        uint32_t duration  = this->duration();
        uint32_t last_time = vis_time + (freq_cntr * duration);
        if (tnow - last_time > duration) {
            switch (style) {
                case AV_STYLE::PERM_OFF:
                    state = AV_STATE::OFF;
                    break;
                case AV_STYLE::OSCIL:
                    this->flipState();
                    break;
                case AV_STYLE::PERM_ON:
                    state = AV_STATE::ON;
                    break;
                default:
                    break;
            }
            this->applyState();
            ++freq_cntr %= freq;
        }
    }

};

class AudioVisualController {
public:
    AudioVisualController();
    ~AudioVisualController();

    void setStyles      (AV_STYLE style = AV_STYLE::PERM_OFF) { setAVs      (style, style, style, style); }
    void setStylesHigher(AV_STYLE style) { setAVsHigher(style, style, style, style); }
    void setAVs(AV_STYLE green = AV_STYLE::PERM_OFF, AV_STYLE yellow = AV_STYLE::PERM_OFF, AV_STYLE red = AV_STYLE::PERM_OFF, AV_STYLE buzzer = AV_STYLE::PERM_OFF) {
        setAV(_led_green , green );
        setAV(_led_yellow, yellow);
        setAV(_led_red   , red   );
        setAV(_buzzer    , buzzer);
    }
    void setAVsHigher(AV_STYLE green = AV_STYLE::PERM_OFF, AV_STYLE yellow = AV_STYLE::PERM_OFF, AV_STYLE red = AV_STYLE::PERM_OFF, AV_STYLE buzzer = AV_STYLE::PERM_OFF) {
        setAVHigher(_led_green , green );
        setAVHigher(_led_yellow, yellow);
        setAVHigher(_led_red   , red   );
        setAVHigher(_buzzer    , buzzer);
    }
    void getAVs(AV_STYLE &green, AV_STYLE &yellow, AV_STYLE &red, AV_STYLE &buzzer) {
        getAV(_led_green , green );
        getAV(_led_yellow, yellow);
        getAV(_led_red   , red   );
        getAV(_buzzer    , buzzer);
    }

    void setFreqs(AV_FREQUENCY freq = AV_FREQUENCY::NORMAL) { setAVsFreq(freq, freq, freq, freq); }
    void setAVsFreq(AV_FREQUENCY green, AV_FREQUENCY yellow, AV_FREQUENCY red, AV_FREQUENCY buzzer) {
        setAVFreq(_led_green , green );
        setAVFreq(_led_yellow, yellow);
        setAVFreq(_led_red   , red   );
        setAVFreq(_buzzer    , buzzer);
    }

    // AV updater, ran in loop
    void update() {
        uint32_t tnow = static_cast<uint32_t>(millis());
        _led_green .update(tnow, _vis_time);
        _led_yellow.update(tnow, _vis_time);
        _led_red   .update(tnow, _vis_time);
        _buzzer    .update(tnow, _vis_time);

        if (tnow - _vis_time > AV_STATE_DURATION) {
            _vis_time += AV_STATE_DURATION;
        }
    }

private:
    void setAVHigher(av &audio_visual, AV_STYLE &style) { audio_visual.style = (audio_visual.style > style) ? audio_visual.style : style; }
    void setAV(av &audio_visual, AV_STYLE &style) { audio_visual.style = style; }
    void getAV(av &audio_visual, AV_STYLE &style) { style = audio_visual.style; }

    void setAVFreq(av &audio_visual, AV_FREQUENCY &freq) {audio_visual.freq = freq; }

private:
    uint32_t _vis_time = 0;

    av _led_green;
    av _led_yellow;
    av _led_red;
    av _buzzer;
};

#endif // AUDIOVISUALCONTROLLER_H
