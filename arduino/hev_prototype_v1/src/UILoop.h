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


#ifndef UI_LOOP_H
#define UI_LOOP_H

#include <Arduino.h>
#include "CommsFormat.h"
#include "CommsControl.h"
#include "BreathingLoop.h"
#include "AlarmLoop.h"
#include "common.h"

class UILoop
{

public:
    UILoop(BreathingLoop *bl, AlarmLoop *al, CommsControl *comms);
    ~UILoop();
    int doCommand(cmd_format &cf);

    void reportFastReadings();
    void reportReadbackValues();
    void reportDebugValues();
    void reportCycleReadings();
    void reportAlarms();
    void reportTargets();
    void reportTargetsNow(target_variables &targets, VENTILATION_MODE mode = VENTILATION_MODE::UNKNOWN);
    void reportPersonal();

    void reportIVTReadings();
    void receiveCommands();

private:
    void cmdGeneral(cmd_format &cf);
    void cmdSetDuration(cmd_format &cf);
    void cmdSetPID(cmd_format &cf);
    void cmdSetTarget(cmd_format &cf, VENTILATION_MODE mode);
    void cmdGetTarget(cmd_format &cf);
    void cmdSetMode(cmd_format &cf);
    void cmdSetThresholdMin(cmd_format &cf);
    void cmdSetThresholdMax(cmd_format &cf);
    void cmdGetThresholdMin(cmd_format &cf);
    void cmdGetThresholdMax(cmd_format &cf);
    void reportThresholdMin(ALARM_CODES alarm_code);
    void reportThresholdMax(ALARM_CODES alarm_code);
    void cmdSetValve(cmd_format &cf);
    void cmdSetPersonal(cmd_format &cf);

    BreathingLoop *_breathing_loop;
    AlarmLoop     *_alarm_loop    ;
    CommsControl  *_comms         ;

    Payload _pl_receive;
    Payload _pl_send;
    uint32_t _fast_report_time;
    uint32_t _readback_report_time;
    uint32_t _cycle_report_time;
    uint32_t _ivt_report_time;
    uint32_t _debug_report_time;
    uint32_t _target_report_time;
    uint32_t _personal_report_time;
    uint16_t _fast_report_timeout;
    uint16_t _readback_report_timeout;
    uint16_t _cycle_report_timeout;
    uint16_t _ivt_report_timeout;
    uint16_t _debug_report_timeout;
    uint16_t _target_report_timeout;
    uint16_t _personal_report_timeout;
    fast_data_format _fast_data;
    readback_data_format _readback_data;
    cycle_data_format _cycle_data;
    ivt_data_format _ivt_data;
    debug_data_format _debug_data;
    target_data_format _target_data;
    personal_data_format _personal_data;

    uint32_t _alarm_report_timeout;
    alarm_format _alarm;

    personal_details _personal;
};

#endif
