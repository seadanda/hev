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

    _fast_report_timeout = 10;  //ms
    _readback_report_timeout = 300; 
    _cycle_report_timeout = 1000;  // this should probably be based on fsm state

    _alarm_report_timeout = 1000; // max timeout to report, actual sending timeout is timeout/priority
    _ivt_report_timeout = 510;  // this should probably be based on fsm state
    _debug_report_timeout = 310; 
}

UILoop::~UILoop()
{;}

void UILoop::receiveCommands()
{

    // check any received payload
    if(_comms->readPayload(_plReceive)) {

      if (_plReceive.getType() == PRIORITY::CMD_ADDR) {
          // apply received cmd to ui loop
          cmd_format cmd;
          _plReceive.getPayload(reinterpret_cast<void*>(&cmd));
          doCommand(cmd);
      }

      // unset received type not to read it again
      _plReceive.setType(PRIORITY::UNSET_ADDR);
    }
}

void UILoop::reportFastReadings()
{
    uint32_t tnow = static_cast<uint32_t>(millis());
    if (tnow - _fast_report_time >= _fast_report_timeout)
    {

	    // TO SWITCH BETWEEN RAW AND MILLIBAR DATA UNCOMMENT BELOW
        readings<float> readings = _breathing_loop->getReadingAverages();
        //readings<int16_t> readings = _breathing_loop->getRawReadings();

        _fast_data.timestamp = static_cast<uint32_t>(readings.timestamp);
        _fast_data.fsm_state = _breathing_loop->getFsmState();

        _fast_data.pressure_air_supply    = readings.pressure_air_supply;
        _fast_data.pressure_air_regulated = readings.pressure_air_regulated;
        _fast_data.pressure_buffer        = readings.pressure_buffer;
        _fast_data.pressure_inhale        = readings.pressure_inhale;
        _fast_data.pressure_patient       = readings.pressure_patient;
        _fast_data.temperature_buffer     = readings.temperature_buffer;
        _fast_data.pressure_o2_supply     = readings.pressure_o2_supply;
        _fast_data.pressure_o2_regulated  = readings.pressure_o2_regulated;
        _fast_data.pressure_diff_patient  = readings.pressure_diff_patient;

        _fast_data.flow = _breathing_loop->getFlow();
        _fast_data.volume= _breathing_loop->getVolume();
        _fast_data.airway_pressure= _breathing_loop->getAirwayPressure();

        _plSend.setPayload(PRIORITY::DATA_ADDR, reinterpret_cast<void *>(&_fast_data), sizeof(_fast_data));
        _comms->writePayload(_plSend);
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
        _readback_data.duration_calibration = durations.calibration;
        _readback_data.duration_buff_purge  = durations.buff_purge;
        _readback_data.duration_buff_flush  = durations.buff_flush;
        _readback_data.duration_buff_prefill  = durations.buff_prefill;
        _readback_data.duration_buff_fill  = durations.buff_fill;
        _readback_data.duration_buff_loaded  = durations.buff_loaded;
        _readback_data.duration_buff_pre_inhale  = durations.buff_pre_inhale;
        _readback_data.duration_inhale  = durations.inhale;
        _readback_data.duration_pause  = durations.pause;
        _readback_data.duration_exhale_fill  = durations.exhale_fill;
        _readback_data.duration_exhale  = durations.exhale;

        _readback_data.valve_air_in = vin_air;
        _readback_data.valve_o2_in = vin_o2;
        _readback_data.valve_inhale = vinhale;
        _readback_data.valve_exhale = vexhale;
        _readback_data.valve_purge = vpurge;

        _readback_data.ventilation_mode = static_cast<uint8_t>(_breathing_loop->getVentilationMode());

        _readback_data.valve_inhale_percent  = 0;
        _readback_data.valve_exhale_percent  = 0;
        _readback_data.valve_air_in_enable   = vparams.valve_air_in_enable;
        _readback_data.valve_o2_in_enable    = vparams.valve_o2_in_enable;
        _readback_data.valve_purge_enable    = vparams.valve_purge_enable;
        _readback_data.inhale_trigger_enable = vparams.inhale_trigger_enable;
        _readback_data.exhale_trigger_enable = vparams.exhale_trigger_enable;
        _readback_data.peep = _breathing_loop->getPEEP();
        _readback_data.inhale_exhale_ratio = _breathing_loop->getIERatio();

        //_plSend.setPayload(PRIORITY::DATA_ADDR, reinterpret_cast<void *>(&_readback_data), sizeof(_readback_data));
        _plSend.setPayload(PRIORITY::CMD_ADDR, reinterpret_cast<void *>(&_readback_data), sizeof(_readback_data));
        _comms->writePayload(_plSend);
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
        _plSend.setPayload(PRIORITY::DATA_ADDR, reinterpret_cast<void *>(&_cycle_data), sizeof(_cycle_data));
        _comms->writePayload(_plSend);
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

                _plSend.setPayload(PRIORITY::ALARM_ADDR, reinterpret_cast<void *>(&_alarm), sizeof(_alarm));
                _comms->writePayload(_plSend);

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
        _plSend.setPayload(PRIORITY::DATA_ADDR, reinterpret_cast<void *>(&_ivt_data), sizeof(_ivt_data));
        _comms->writePayload(_plSend);
        _ivt_report_time = tnow;
    }

}

void UILoop::reportDebugValues()
{

    uint32_t tnow = static_cast<uint32_t>(millis());
    if (tnow - _debug_report_time >= _debug_report_timeout)
    {

        _debug_data.timestamp = static_cast<uint32_t>(tnow);
        pid_variables pid = _breathing_loop->getPIDVariables();
        _debug_data.kp = pid.Kp;
        _debug_data.ki = pid.Ki;
        _debug_data.kd = pid.Kd;

        _debug_data.proportional       = pid.proportional;
        _debug_data.integral           = pid.integral;
        _debug_data.derivative         = pid.derivative;
        _debug_data.target_pressure    = pid.target_pressure;
        _debug_data.process_pressure   = pid.process_pressure;
        _debug_data.valve_duty_cycle   = pid.valve_duty_cycle;

        _plSend.setPayload(PRIORITY::DATA_ADDR, reinterpret_cast<void *>(&_debug_data), sizeof(_debug_data));
        _comms->writePayload(_plSend);
        _debug_report_time = tnow;
    }
}

void UILoop::reportTargets(target_variables targets)
{

    uint32_t tnow = static_cast<uint32_t>(millis());
    
    _target_data.timestamp = tnow;
    _target_data.mode = targets.mode;
    _target_data.inspiratory_pressure = targets.inspiratory_pressure;
    _target_data.ie_ratio = targets.ie_ratio;
    _target_data.volume = targets.volume;
    _target_data.respiratory_rate = targets.respiratory_rate;
    _target_data.peep = targets.peep;
    _target_data.fiO2 = targets.fiO2;
    _target_data.inhale_time = targets.inhale_time;
    //_plSend.setPayload(PRIORITY::DATA_ADDR, reinterpret_cast<void *>(&_target_data), sizeof(_target_data));
    _plSend.setPayload(PRIORITY::CMD_ADDR, reinterpret_cast<void *>(&_target_data), sizeof(_target_data));
    _comms->writePayload(_plSend);

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

void UILoop::cmdSetTarget(cmd_format &cf, int8_t mode){
    //logMsg("cmdSetTarget "+String(mode));
    switch(mode){

        case VENTILATION_MODE::PC_AC : 
            setTarget(static_cast<CMD_SET_TARGET>(cf.cmd_code), _breathing_loop->getTargetVariablesPC_AC(), cf.param);
            break;
        case VENTILATION_MODE::PC_AC_PRVC: 
            setTarget(static_cast<CMD_SET_TARGET>(cf.cmd_code), _breathing_loop->getTargetVariablesPC_AC_PRVC(), cf.param);
            break;
        case VENTILATION_MODE::PC_PSV : 
            setTarget(static_cast<CMD_SET_TARGET>(cf.cmd_code), _breathing_loop->getTargetVariablesPC_PSV(), cf.param);
            break;
        case VENTILATION_MODE::CPAP : 
            setTarget(static_cast<CMD_SET_TARGET>(cf.cmd_code), _breathing_loop->getTargetVariablesCPAP(), cf.param);
            break;
        case VENTILATION_MODE::TEST : 
            setTarget(static_cast<CMD_SET_TARGET>(cf.cmd_code), _breathing_loop->getTargetVariablesTest(), cf.param);
            break;
        case VENTILATION_MODE::CURRENT: 
            setTarget(static_cast<CMD_SET_TARGET>(cf.cmd_code), _breathing_loop->getTargetVariablesCurrent(), cf.param);
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
            reportTargets(_breathing_loop->getTargetVariablesPC_AC());
            break;
        case VENTILATION_MODE::PC_AC_PRVC: 
            reportTargets(_breathing_loop->getTargetVariablesPC_AC_PRVC());
            break;
        case VENTILATION_MODE::PC_PSV : 
            reportTargets(_breathing_loop->getTargetVariablesPC_PSV());
            break;
        case VENTILATION_MODE::CPAP : 
            reportTargets(_breathing_loop->getTargetVariablesCPAP());
            break;
        case VENTILATION_MODE::TEST : 
            reportTargets(_breathing_loop->getTargetVariablesTest());
            break;
        case VENTILATION_MODE::CURRENT: 
            reportTargets(_breathing_loop->getTargetVariablesCurrent());
            break;
        default: 
            break;
    }
}
// FIXME shouldn't these use setThresholdMin,Max ...?
void UILoop::cmdSetThresholdMin(cmd_format &cf) {
    setAlarm<float>(static_cast<ALARM_CODES>(cf.cmd_code), _alarm_loop->getThresholdsMin(), cf.param);
}

void UILoop::cmdSetThresholdMax(cmd_format &cf) {
    setAlarm<float>(static_cast<ALARM_CODES>(cf.cmd_code), _alarm_loop->getThresholdsMax(), cf.param);
}

void UILoop::cmdSetValve(cmd_format &cf) {
    setValveParam(static_cast<CMD_SET_VALVE>(cf.cmd_code), _breathing_loop->getValvesController()->getValveParams(), cf.param);
}
