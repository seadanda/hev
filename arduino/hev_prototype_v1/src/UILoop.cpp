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


#include "UILoop.h"

UILoop::UILoop(BreathingLoop *bl, AlarmLoop *al, CommsControl *comms)
{
    _breathing_loop = bl;
    _alarm_loop     = al;
    _comms          = comms;
    uint32_t tnow = static_cast<uint32_t>(millis());
    _fast_report_time = tnow;
    _readback_report_time = tnow;
    _cycle_report_time = tnow;
    _ivt_report_time = tnow;
    _debug_report_time = tnow;
    _target_report_time = tnow;
    _personal_report_time = tnow;

    _fast_report_timeout = 20;  //ms
    _readback_report_timeout = 300; 
    _cycle_report_timeout = 1000;  // this should probably be based on fsm state
    _alarm_report_timeout = 1000; // max timeout to report, actual sending timeout is timeout/priority
    _ivt_report_timeout = 2000;  // this should probably be based on fsm state
    _debug_report_timeout = 310; 
    _target_report_timeout = 1000;  
    _personal_report_timeout = 3000;  

}

UILoop::~UILoop()
{;}

void UILoop::receiveCommands()
{
    // check any received payload
    if(_comms->readPayload(_pl_receive)) {
        PAYLOAD_TYPE pl_type = *(reinterpret_cast<PAYLOAD_TYPE*>(_pl_receive.getInformation()) + 5);

        switch (pl_type) {
            case PAYLOAD_TYPE::CMD: {
                // apply received cmd to ui loop
                cmd_format cmd;
                _pl_receive.getPayload(reinterpret_cast<void*>(&cmd));
                doCommand(cmd);
                break;
            }
            case PAYLOAD_TYPE::BATTERY: {
                battery_data_format bat;
                _pl_receive.getPayload(reinterpret_cast<void*>(&bat));
                _alarm_loop->setBatteryAlarms(bat);
                // do what needs to be done with the battery information
                //logMsg("received battery dummy " + String(bat.dummy));
                break;
            }
            case PAYLOAD_TYPE::PERSONAL: {
                personal_data_format pers;
                _pl_receive.getPayload(reinterpret_cast<void*>(&pers));
                strcpy(_personal.name, pers.name);
                strcpy(_personal.patient_id, pers.patient_id);
                _personal.age = pers.age;
                _personal.sex = pers.sex;
                _personal.height = pers.height;
                _personal.weight = pers.weight;
                // do what needs to be done with the battery information
                //logMsg("received battery dummy " + String(bat.dummy));
		reportPersonal();
                break;
            }
            default:
                break;
        }

        // unset received type not to read it again
        _pl_receive.setType(PRIORITY::UNSET_ADDR);
    }
}

void UILoop::reportFastReadings()
{
    uint32_t tnow = static_cast<uint32_t>(millis());
    if (tnow - _fast_report_time >= _fast_report_timeout)
    {

	    // TO SWITCH BETWEEN RAW AND MILLIBAR DATA UNCOMMENT BELOW
        readings<float> readings = _breathing_loop->getReadingAverages();
        //readings<float> readings = _breathing_loop->getRawReadings();

        _fast_data.timestamp = static_cast<uint32_t>(readings.timestamp);
        _fast_data.fsm_state = _breathing_loop->getBreatheFSMState();

        _fast_data.pressure_air_supply    = readings.pressure_air_supply;
        _fast_data.pressure_air_regulated = readings.pressure_air_regulated;
        _fast_data.pressure_buffer        = readings.pressure_buffer;
        _fast_data.pressure_inhale        = readings.pressure_inhale;
        _fast_data.pressure_patient       = readings.pressure_patient;
        _fast_data.temperature_buffer     = readings.temperature_buffer;
        _fast_data.pressure_o2_supply     = readings.pressure_o2_supply;
        _fast_data.pressure_o2_regulated  = readings.pressure_o2_regulated;
        _fast_data.pressure_diff_patient  = readings.pressure_diff_patient;

        pid_variables &pid = _breathing_loop->getPIDVariables();
        _fast_data.proportional       = pid.proportional;
        _fast_data.integral           = pid.integral;
        _fast_data.derivative         = pid.derivative;
        _fast_data.target_pressure    = pid.target_pressure;
        _fast_data.process_pressure   = pid.process_pressure;
        _fast_data.valve_duty_cycle   = pid.valve_duty_cycle;


        calculations<float> calc = _breathing_loop->getCalculations();
        _fast_data.flow            = calc.flow;
        _fast_data.flow_calc       = calc.flow_calc;
        _fast_data.volume          = calc.volume;
        _fast_data.airway_pressure = calc.pressure_airway;

        _pl_send.setPayload(PRIORITY::DATA_ADDR, reinterpret_cast<void *>(&_fast_data), sizeof(_fast_data));
        _comms->writePayload(_pl_send);
        _fast_report_time = tnow;
    }
}

void UILoop::reportReadbackValues()
{
    uint32_t tnow = static_cast<uint32_t>(millis());
    if (tnow - _readback_report_time >= _readback_report_timeout)
    {
        bool vin_air, vin_o2, vpurge;
        uint8_t vinhale, vexhale;
        ValvesController *valves_controller = _breathing_loop->getValvesController();
        valves_controller->getValves(vin_air, vin_o2, vinhale, vexhale, vpurge);
        valve_params vparams = valves_controller->getValveParams();

        _readback_data.timestamp = static_cast<uint32_t>(tnow);
        states_durations durations = _breathing_loop->getDurations();
        _readback_data.duration_pre_calibration = durations.pre_calibration;
        _readback_data.duration_calibration = durations.calibration;
        _readback_data.duration_buff_purge  = durations.buff_purge;
        _readback_data.duration_buff_flush  = durations.buff_flush;
        _readback_data.duration_buff_prefill  = durations.buff_prefill;
        _readback_data.duration_buff_fill  = durations.buff_fill;
        // _readback_data.duration_buff_loaded  = durations.buff_loaded;
        _readback_data.duration_buff_pre_inhale  = durations.buff_pre_inhale;
        _readback_data.duration_inhale  = durations.inhale;
        _readback_data.duration_pause  = durations.pause;
        _readback_data.duration_exhale  = durations.exhale;
        // _readback_data.duration_exhale  = durations.exhale;

        _readback_data.valve_air_in = vin_air;
        _readback_data.valve_o2_in = vin_o2;
        _readback_data.valve_inhale = vinhale;
        _readback_data.valve_exhale = vexhale;
        _readback_data.valve_purge = vpurge;

        _readback_data.ventilation_mode = _breathing_loop->getVentilationMode();

        _readback_data.valve_inhale_percent  = 0;
        _readback_data.valve_exhale_percent  = 0;
        _readback_data.valve_air_in_enable   = vparams.valve_air_in_enable;
        _readback_data.valve_o2_in_enable    = vparams.valve_o2_in_enable;
        _readback_data.valve_purge_enable    = vparams.valve_purge_enable;
        _readback_data.inhale_trigger_enable = _breathing_loop->getTargetVariablesCurrent().inhale_trigger_enable;
        _readback_data.exhale_trigger_enable = _breathing_loop->getTargetVariablesCurrent().exhale_trigger_enable;
        _readback_data.peep = _breathing_loop->getPEEP();
        _readback_data.inhale_exhale_ratio = _breathing_loop->getIERatio();

        pid_variables &pid = _breathing_loop->getPIDVariables();
        _readback_data.kp = pid.Kp;
        _readback_data.ki = pid.Ki;
        _readback_data.kd = pid.Kd;
        _readback_data.pid_gain = pid.pid_gain;
        _readback_data.max_patient_pressure = pid.max_patient_pressure;

        _pl_send.setPayload(PRIORITY::CMD_ADDR, reinterpret_cast<void *>(&_readback_data), sizeof(_readback_data));
        _comms->writePayload(_pl_send);
        _readback_report_time = tnow;
    }
}

void UILoop::reportCycleReadings()
{
    uint32_t tnow = static_cast<uint32_t>(millis());
    if (tnow - _cycle_report_time >= _cycle_report_timeout)
    {

        _cycle_data.timestamp =  tnow;

        //_cycle_data.respiratory_rate = _breathing_loop->getRespiratoryRate();
        cycle_readings cr = _breathing_loop->getCycleReadings();
        _cycle_data.respiratory_rate          = cr.respiratory_rate;
        _cycle_data.tidal_volume              = cr.tidal_volume;
        _cycle_data.exhaled_minute_volume     = cr.exhaled_minute_volume;
        _cycle_data.inhaled_minute_volume     = cr.inhaled_minute_volume;
        _cycle_data.minute_volume             = cr.minute_volume;
        _cycle_data.exhaled_tidal_volume      = cr.exhaled_tidal_volume;
        _cycle_data.inhaled_tidal_volume      = cr.inhaled_tidal_volume;
        _cycle_data.lung_compliance           = cr.lung_compliance;
        _cycle_data.static_compliance         = cr.static_compliance;
        _cycle_data.inhalation_pressure       = cr.inhalation_pressure;
        _cycle_data.peak_inspiratory_pressure = cr.peak_inspiratory_pressure;
        _cycle_data.plateau_pressure          = cr.plateau_pressure;
        _cycle_data.mean_airway_pressure      = cr.mean_airway_pressure;
        _cycle_data.fiO2_percent              = cr.fiO2_percent;
        _cycle_data.apnea_index               = cr.apnea_index;
        _cycle_data.apnea_time                = cr.apnea_time;
        _cycle_data.mandatory_breath          = cr.mandatory_breath;
        _pl_send.setPayload(PRIORITY::DATA_ADDR, reinterpret_cast<void *>(&_cycle_data), sizeof(_cycle_data));
        _comms->writePayload(_pl_send);
        _cycle_report_time = tnow;
    }

}

void UILoop::reportAlarms()
{
    uint32_t tnow = static_cast<uint32_t>(millis());
    // loop all alarms
    for (uint8_t alarm_num = 0; alarm_num < ALARM_CODES::ALARMS_COUNT; alarm_num++) {
        // get active ones
        if (_alarm_loop->getActives()[alarm_num]) {
            ALARM_TYPE type = _alarm_loop->getTypes()[alarm_num];
            uint32_t *last_broadcast = &_alarm_loop->getLastBroadcasts()[alarm_num];
            // refresh on timeout
            if (tnow - (*last_broadcast) > static_cast<uint32_t>(_alarm_report_timeout / type)) {
                _alarm.timestamp  = tnow;
                _alarm.alarm_type = type;
                _alarm.alarm_code = alarm_num;
                _alarm.param      = _alarm_loop->getValues()[alarm_num];

                _pl_send.setPayload(PRIORITY::ALARM_ADDR, reinterpret_cast<void *>(&_alarm), sizeof(_alarm));
                _comms->writePayload(_pl_send);

                *last_broadcast = tnow;
            }
        }
    }
}
void UILoop::reportIVTReadings()
{
    uint32_t tnow = static_cast<uint32_t>(millis());
    if (tnow - _ivt_report_time >= _ivt_report_timeout)
    {

        _ivt_data.timestamp =  tnow;
        IV_readings<float>* iv = _breathing_loop->getValvesController()->getIVReadings(); 
	float sys_temp = getSystemUtils()->getSystemTemperature();
        _ivt_data.air_in_voltage = iv->air_in_voltage;
        _ivt_data.o2_in_voltage = iv->o2_in_voltage;
        _ivt_data.purge_voltage = iv->purge_voltage;
        _ivt_data.inhale_voltage = iv->inhale_voltage;
        _ivt_data.exhale_voltage = iv->exhale_voltage;
        _ivt_data.air_in_current = iv->air_in_current;
        _ivt_data.o2_in_current = iv->o2_in_current;
        _ivt_data.purge_current = iv->purge_current;
        _ivt_data.inhale_current = iv->inhale_current;
        _ivt_data.exhale_current = iv->exhale_current;
        _ivt_data.air_in_i2caddr = iv->air_in_i2caddr;
        _ivt_data.o2_in_i2caddr = iv->o2_in_i2caddr;
        _ivt_data.purge_i2caddr = iv->purge_i2caddr;
        _ivt_data.inhale_i2caddr = iv->inhale_i2caddr;
        _ivt_data.exhale_i2caddr = iv->exhale_i2caddr;
        _ivt_data.system_temp = sys_temp;
        _pl_send.setPayload(PRIORITY::DATA_ADDR, reinterpret_cast<void *>(&_ivt_data), sizeof(_ivt_data));
        _comms->writePayload(_pl_send);
        _ivt_report_time = tnow;
    }

}

void UILoop::reportDebugValues()
{

    uint32_t tnow = static_cast<uint32_t>(millis());
    if (tnow - _debug_report_time >= _debug_report_timeout)
    {

        _debug_data.timestamp = static_cast<uint32_t>(tnow);
        pid_variables &pid = _breathing_loop->getPIDVariables();
        _debug_data.kp = pid.Kp;
        _debug_data.ki = pid.Ki;
        _debug_data.kd = pid.Kd;

        _debug_data.proportional       = pid.proportional;
        _debug_data.integral           = pid.integral;
        _debug_data.derivative         = pid.derivative;
        _debug_data.target_pressure    = pid.target_pressure;
        _debug_data.process_pressure   = pid.process_pressure;
        _debug_data.valve_duty_cycle   = pid.valve_duty_cycle;

        _pl_send.setPayload(PRIORITY::DATA_ADDR, reinterpret_cast<void *>(&_debug_data), sizeof(_debug_data));
        _comms->writePayload(_pl_send);
        _debug_report_time = tnow;
    }
}

void UILoop::reportTargets()
{
    uint32_t tnow = static_cast<uint32_t>(millis());
    if (tnow - _target_report_time >= _target_report_timeout)
    {
        reportTargetsNow(_breathing_loop->getTargetVariablesCurrent(), VENTILATION_MODE::CURRENT);
        _target_report_time = tnow;
    }
}

void UILoop::reportTargetsNow(target_variables &targets, VENTILATION_MODE mode)
{

    uint32_t tnow = static_cast<uint32_t>(millis());
    
    _target_data.timestamp = tnow;

    if (mode != VENTILATION_MODE::UNKNOWN) {
        _target_data.mode = mode;
    } else {
        _target_data.mode = targets.mode;
    }
    _target_data.inspiratory_pressure = targets.inspiratory_pressure;
    _target_data.ie_ratio = targets.ie_ratio;
    _target_data.volume = targets.volume;
    _target_data.respiratory_rate = targets.respiratory_rate;
    _target_data.peep = targets.peep;
    _target_data.fiO2_percent = targets.fiO2_percent;
    _target_data.inhale_time = static_cast<float>(targets.inhale_time)/1000.0;  // stored in ms, report in s
    _target_data.inhale_trigger_enable    = targets.inhale_trigger_enable ;
    _target_data.exhale_trigger_enable    = targets.exhale_trigger_enable ; 
    _target_data.volume_trigger_enable    = targets.volume_trigger_enable ; 
    _target_data.inhale_trigger_threshold = targets.inhale_trigger_threshold; 
    _target_data.exhale_trigger_threshold = 100.0*targets.exhale_trigger_threshold;  
    _target_data.buffer_lower_pressure = targets.buffer_lower_pressure;
    _target_data.buffer_upper_pressure = targets.buffer_upper_pressure;
    //_target_data.pid_gain              = targets.pid_gain;
    _pl_send.setPayload(PRIORITY::CMD_ADDR, reinterpret_cast<void *>(&_target_data), sizeof(_target_data));
    _comms->writePayload(_pl_send);

}

void UILoop::reportPersonal()
{
    uint32_t tnow = static_cast<uint32_t>(millis());
    if (tnow - _personal_report_time >= _personal_report_timeout)
    {
        _personal_data.timestamp = static_cast<uint32_t>(tnow);

        strcpy(_personal_data.name, _personal.name);
        strcpy(_personal_data.patient_id, _personal.patient_id);
        _personal_data.age    = _personal.age   ;
        _personal_data.sex    = _personal.sex   ;
        _personal_data.height = _personal.height;
        _personal_data.weight = _personal.weight;

        _pl_send.setPayload(PRIORITY::DATA_ADDR, reinterpret_cast<void *>(&_personal_data), sizeof(_personal_data));
        _comms->writePayload(_pl_send);
        _personal_report_time = tnow;
    }
}


int UILoop::doCommand(cmd_format &cf)
{
    switch(cf.cmd_type) {
        case CMD_TYPE::GENERAL:
            cmdGeneral(cf);
            break;
        case CMD_TYPE::SET_DURATION:
            cmdSetDuration(cf);
            break;
        case CMD_TYPE::SET_MODE:
            cmdSetMode(cf);
            break;
        case CMD_TYPE::SET_THRESHOLD_MIN :
            cmdSetThresholdMin(cf);
            break;
        case CMD_TYPE::SET_THRESHOLD_MAX :
            cmdSetThresholdMax(cf);
            break;
        case CMD_TYPE::SET_VALVE:
            cmdSetValve(cf);
            break;
        case CMD_TYPE::SET_PID: 
            cmdSetPID(cf);
            break;
        case CMD_TYPE::SET_TARGET_PC_AC: 
            cmdSetTarget(cf, VENTILATION_MODE::PC_AC);
            break;
        case CMD_TYPE::SET_TARGET_PC_AC_PRVC: 
            cmdSetTarget(cf, VENTILATION_MODE::PC_AC_PRVC);
            break;
        case CMD_TYPE::SET_TARGET_PC_PSV: 
            cmdSetTarget(cf, VENTILATION_MODE::PC_PSV);
            break;
        case CMD_TYPE::SET_TARGET_CPAP:
            cmdSetTarget(cf, VENTILATION_MODE::CPAP);
            break;
        case CMD_TYPE::SET_TARGET_TEST: 
            cmdSetTarget(cf, VENTILATION_MODE::TEST);
            break;
        case CMD_TYPE::SET_TARGET_CURRENT:
            cmdSetTarget(cf, VENTILATION_MODE::CURRENT);
            break;
        case CMD_TYPE::GET_TARGETS:
            cmdGetTarget(cf);
            break;
        // case CMD_TYPE::SET_PERSONAL:
        //     cmdSetPersonal(cf);
        //     break;
        case CMD_TYPE::GET_THRESHOLD_MIN :
            cmdGetThresholdMin(cf);
            break;
        case CMD_TYPE::GET_THRESHOLD_MAX :
            cmdGetThresholdMax(cf);
            break;
        default:
            break;
    }
    return 0;
}

void UILoop::cmdGeneral(cmd_format &cf) {
    switch (cf.cmd_code) {
        case CMD_GENERAL::START : _breathing_loop->doStart();
            break;
        case CMD_GENERAL::STOP  : _breathing_loop->doStop();
            break;
        case CMD_GENERAL::RESET : _breathing_loop->doReset();
            break;
        case CMD_GENERAL::STANDBY : _breathing_loop->doStandby();
            break;
        case CMD_GENERAL::GET_PERSONAL: reportPersonal();
            break;
        default:
            break;
    }
}

void UILoop::cmdSetDuration(cmd_format &cf) {
    setDuration(static_cast<CMD_SET_DURATION>(cf.cmd_code), _breathing_loop->getDurations(), static_cast<uint32_t>(cf.param));
}

void UILoop::cmdSetMode(cmd_format &cf) {
    _breathing_loop->setVentilationMode(static_cast<VENTILATION_MODE>(cf.cmd_code));
}

void UILoop::cmdSetPID(cmd_format &cf){
    setPID(static_cast<CMD_SET_PID>(cf.cmd_code), _breathing_loop->getPIDVariables(), cf.param);
}

void UILoop::cmdSetTarget(cmd_format &cf, VENTILATION_MODE mode){
    switch(mode){
        case VENTILATION_MODE::PC_AC : 
            setTarget(static_cast<CMD_SET_TARGET>(cf.cmd_code), _breathing_loop->getTargetVariablesPC_AC(), cf.param);
	    reportTargetsNow(_breathing_loop->getTargetVariablesPC_AC());
            break;
        case VENTILATION_MODE::PC_AC_PRVC: 
            setTarget(static_cast<CMD_SET_TARGET>(cf.cmd_code), _breathing_loop->getTargetVariablesPC_AC_PRVC(), cf.param);
	    reportTargetsNow(_breathing_loop->getTargetVariablesPC_AC_PRVC());
            break;
        case VENTILATION_MODE::PC_PSV : 
            setTarget(static_cast<CMD_SET_TARGET>(cf.cmd_code), _breathing_loop->getTargetVariablesPC_PSV(), cf.param);
	    reportTargetsNow(_breathing_loop->getTargetVariablesPC_PSV());
            break;
        case VENTILATION_MODE::CPAP : 
            setTarget(static_cast<CMD_SET_TARGET>(cf.cmd_code), _breathing_loop->getTargetVariablesCPAP(), cf.param);
	    reportTargetsNow(_breathing_loop->getTargetVariablesCPAP());
            break;
        case VENTILATION_MODE::TEST : 
            setTarget(static_cast<CMD_SET_TARGET>(cf.cmd_code), _breathing_loop->getTargetVariablesTest(), cf.param);
	    reportTargetsNow(_breathing_loop->getTargetVariablesTest());
            break;
        case VENTILATION_MODE::CURRENT: 
            setTarget(static_cast<CMD_SET_TARGET>(cf.cmd_code), _breathing_loop->getTargetVariablesCurrent(), cf.param);
	    reportTargetsNow(_breathing_loop->getTargetVariablesCurrent());
            break;
        default: 
            break;
    }
}


void UILoop::cmdGetTarget(cmd_format &cf){

    VENTILATION_MODE mode = static_cast<VENTILATION_MODE>(cf.cmd_code);
    //logMsg(" **cmdGetTarget "+String(mode));
    switch(mode){

        case VENTILATION_MODE::PC_AC : 
            reportTargetsNow(_breathing_loop->getTargetVariablesPC_AC());
            break;
        case VENTILATION_MODE::PC_AC_PRVC: 
            reportTargetsNow(_breathing_loop->getTargetVariablesPC_AC_PRVC());
            break;
        case VENTILATION_MODE::PC_PSV : 
            reportTargetsNow(_breathing_loop->getTargetVariablesPC_PSV());
            break;
        case VENTILATION_MODE::CPAP : 
            reportTargetsNow(_breathing_loop->getTargetVariablesCPAP());
            break;
        case VENTILATION_MODE::TEST : 
            reportTargetsNow(_breathing_loop->getTargetVariablesTest());
            break;
        case VENTILATION_MODE::CURRENT: 
            reportTargetsNow(_breathing_loop->getTargetVariablesCurrent());
            break;
        default: 
            break;
    }
}

// FIXME shouldn't these use setThresholdMin,Max ...?
void UILoop::cmdSetThresholdMin(cmd_format &cf) {
    ALARM_CODES alarm_code = static_cast<ALARM_CODES>(cf.cmd_code);
    setAlarm<float>(alarm_code, _alarm_loop->getThresholdsMin(), cf.param);
    reportThresholdMin(alarm_code);
}

void UILoop::cmdSetThresholdMax(cmd_format &cf) {
    ALARM_CODES alarm_code = static_cast<ALARM_CODES>(cf.cmd_code);
    setAlarm<float>(alarm_code, _alarm_loop->getThresholdsMax(), cf.param);
    reportThresholdMax(alarm_code);
}

void UILoop::cmdGetThresholdMin(cmd_format &cf) {
    ALARM_CODES alarm_code = static_cast<ALARM_CODES>(cf.cmd_code);
    reportThresholdMin(alarm_code);
}

void UILoop::cmdGetThresholdMax(cmd_format &cf) {
    ALARM_CODES alarm_code = static_cast<ALARM_CODES>(cf.cmd_code);
    reportThresholdMax(alarm_code);
}

void UILoop::cmdSetValve(cmd_format &cf) {
    setValveParam(static_cast<CMD_SET_VALVE>(cf.cmd_code), _breathing_loop->getValvesController()->getValveParams(), cf.param);
}

void UILoop::reportThresholdMin(ALARM_CODES alarm_code)
{
    cmd_format response;
    response.timestamp = millis();
    response.cmd_type = CMD_TYPE::GET_THRESHOLD_MIN;
    response.cmd_code = alarm_code;
    response.param = _alarm_loop->getThresholdsMin()[alarm_code];
    _pl_send.setPayload(PRIORITY::DATA_ADDR, reinterpret_cast<void *>(&response), sizeof(response));
    _comms->writePayload(_pl_send);

}
void UILoop::reportThresholdMax(ALARM_CODES alarm_code)
{
    cmd_format response;
    response.timestamp = millis();
    response.cmd_type = CMD_TYPE::GET_THRESHOLD_MAX;
    response.cmd_code = alarm_code;
    response.param = _alarm_loop->getThresholdsMax()[alarm_code];
    _pl_send.setPayload(PRIORITY::DATA_ADDR, reinterpret_cast<void *>(&response), sizeof(response));
    _comms->writePayload(_pl_send);
}
