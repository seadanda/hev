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
    void reportCycleReadings();
    void reportIVTReadings();
    void receiveCommands();

private:
    void cmdGeneral(cmd_format &cf);
    void cmdSetDuration(cmd_format &cf);
    void cmdSetPID(cmd_format &cf);
    void cmdSetMode(cmd_format &cf);
    void cmdSetThresholdMin(cmd_format &cf);
    void cmdSetThresholdMax(cmd_format &cf);
    void cmdSetValve(cmd_format &cf);


    BreathingLoop *_breathing_loop;
    AlarmLoop     *_alarm_loop    ;
    CommsControl  *_comms         ;

    Payload _plReceive;
    Payload _plSend;
    uint32_t _fast_report_time;
    uint32_t _readback_report_time;
    uint32_t _cycle_report_time;
    uint32_t _ivt_report_time;
    uint16_t _fast_report_timeout;
    uint16_t _readback_report_timeout;
    uint16_t _cycle_report_timeout;
    uint16_t _ivt_report_timeout;
    fast_data_format _fast_data;
    readback_data_format _readback_data;
    cycle_data_format _cycle_data;
    ivt_data_format _ivt_data;

};

#endif
