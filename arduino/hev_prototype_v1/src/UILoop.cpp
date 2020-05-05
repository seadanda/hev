#include "UILoop.h"
// #include "BreathingLoop.h"

UILoop::UILoop(BreathingLoop *bl, AlarmLoop *al, CommsControl *comms)
{
    _breathing_loop = bl;
    _alarm_loop     = al;
    _comms          = comms;
    uint32_t tnow = static_cast<uint32_t>(millis());
    _fast_report_time = tnow;
    _readback_report_time = tnow;
    _cycle_report_time = tnow;

    _fast_report_timeout = 50;  //ms
    _readback_report_timeout = 300; 
    _cycle_report_timeout = 500;  // this should probably be based on fsm state

    _alarm_report_timeout = 1000; // max timeout to report, actual sending timeout is timeout/priority
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
    if (tnow - _fast_report_time > _fast_report_timeout)
    {

	    // TO SWITCH BETWEEN RAW AND MILLIBAR DATA UNCOMMENT BELOW
        readings<int16_t> readings = _breathing_loop->getReadingAverages();
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
    if (tnow - _readback_report_time > _readback_report_timeout)
    {
        bool vin_air, vin_o2, vpurge;
        uint8_t vinhale, vexhale;
        ValvesController *valves_controller = _breathing_loop->getValvesController();
        valves_controller->getValves(vin_air, vin_o2, vinhale, vexhale, vpurge);

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

        //_readback_data.valve_inhale_percent = 0;  //TODO
        //_readback_data.valve_exhale_percent = _breathing_loop->getPIDVariables().Kp * 1000;//0;  //TODO
        _readback_data.valve_inhale_percent  = valves_controller->getValveInhalePercent();
        _readback_data.valve_exhale_percent  = valves_controller->getValveInhalePercent();
        _readback_data.valve_air_in_enable   = valves_controller->valveAirInEnabled();
        _readback_data.valve_o2_in_enable    = valves_controller->valveO2InEnabled();
        _readback_data.valve_purge_enable    = valves_controller->valvePurgeEnabled();
        _readback_data.inhale_trigger_enable = valves_controller->inhaleTriggerEnabled();
        _readback_data.exhale_trigger_enable = valves_controller->exhaleTriggerEnabled();
        _readback_data.peep = _breathing_loop->getPEEP();
        _readback_data.inhale_exhale_ratio = _breathing_loop->getIERatio();

        _plSend.setPayload(PRIORITY::DATA_ADDR, reinterpret_cast<void *>(&_readback_data), sizeof(_readback_data));
        _comms->writePayload(_plSend);
        _readback_report_time = tnow;
    }
}

void UILoop::reportCycleReadings()
{
    uint32_t tnow = static_cast<uint32_t>(millis());
    if (tnow - _cycle_report_time > _cycle_report_timeout)
    {

        _cycle_data.timestamp =  tnow;

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
        if (_alarm_loop->getActive()[alarm_num]) {
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
        default:
            break;
    }
}

void UILoop::cmdSetDuration(cmd_format &cf) {
    setDuration(static_cast<CMD_SET_DURATION>(cf.cmd_code), _breathing_loop->getDurations(), cf.param);
}

void UILoop::cmdSetMode(cmd_format &cf) {
    _breathing_loop->setVentilationMode(static_cast<VENTILATION_MODE>(cf.cmd_code));
}

void UILoop::cmdSetPID(cmd_format &cf){

    setPID(static_cast<CMD_SET_PID>(cf.cmd_code), _breathing_loop->getPIDVariables(), cf.param);
}

// FIXME shouldn't these use setThresholdMin,Max ...?
void UILoop::cmdSetThresholdMin(cmd_format &cf) {
    setAlarm<uint32_t>(static_cast<ALARM_CODES>(cf.cmd_code), _alarm_loop->getThresholdsMin(), cf.param);
}

void UILoop::cmdSetThresholdMax(cmd_format &cf) {
    setAlarm<uint32_t>(static_cast<ALARM_CODES>(cf.cmd_code), _alarm_loop->getThresholdsMax(), cf.param);
}

void UILoop::cmdSetValve(cmd_format &cf) {
    setValveParam(static_cast<CMD_SET_VALVE>(cf.cmd_code), _breathing_loop->getValvesController(), cf.param);
}