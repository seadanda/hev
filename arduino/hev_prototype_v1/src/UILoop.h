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
    void reportTargetsNow(target_variables &targets);
    void reportPersonal();

    void reportIVTReadings();
    void receiveCommands();

private:
    void cmdGeneral(cmd_format &cf);
    void cmdSetDuration(cmd_format &cf);
    void cmdSetPID(cmd_format &cf);
    void cmdSetTarget(cmd_format &cf, int8_t mode);
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
