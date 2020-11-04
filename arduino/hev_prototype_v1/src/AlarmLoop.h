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


#ifndef ALARM_LOOP_H
#define ALARM_LOOP_H

#include <Arduino.h>
#include "common.h"
#include "CommsFormat.h"
#include "AudioVisualController.h"

class AlarmLoop {

public:
    AlarmLoop();
    ~AlarmLoop();

    void fireAlarms();
    void updateValues(readings<float> fast_data, cycle_readings cr);

    float *getValues       () { return _alarms.values        ; }
    float *getThresholdsMin() { return _alarms.thresholds_min; }
    float *getThresholdsMax() { return _alarms.thresholds_max; }

    uint32_t *getLastBroadcasts() { return _alarms.last_broadcasts; }

    ALARM_TYPE  getHighestType() { return _type; }
    ALARM_TYPE *getTypes()       { return _alarms.priorities; }
    bool       *getActives()     { return _alarms.actives; }
    void setBatteryAlarms(battery_data_format &bat);

private:
    ALARM_TYPE checkThresholds();
    void setBatteryThresholds();


private:
    AudioVisualController _av_controller;

    ALARM_TYPE _type = ALARM_TYPE::ALARM_TYPE_UNKNOWN;
    alarms _alarms;
};

#endif
