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
}

UILoop::~UILoop()
{;}

void UILoop::receiveCommands()
{

    // check any received payload
    if(_comms->readPayload(_plReceive)) {

      if (_plReceive.getType() == PAYLOAD_TYPE::CMD) {
          // apply received cmd to ui loop
          cmd_format cmd;
          _plReceive.getPayload(reinterpret_cast<void*>(&cmd));
          doCommand(cmd);
      }

      // unset received type not to read it again
      _plReceive.setType(PAYLOAD_TYPE::UNSET);
    }
}

void UILoop::reportFastReadings()
{
    uint32_t tnow = static_cast<uint32_t>(millis());
    if (tnow - _fast_report_time > _fast_report_timeout)
    {

        readings<uint16_t> readings_avgs = _breathing_loop->getReadingAverages();
        _fast_data.timestamp = static_cast<uint32_t>(readings_avgs.timestamp);
        _fast_data.fsm_state = _breathing_loop->getFsmState();
        _fast_data.pressure_air_supply = readings_avgs.pressure_air_supply;
        _fast_data.pressure_air_regulated = readings_avgs.pressure_air_regulated;
        _fast_data.pressure_buffer = readings_avgs.pressure_buffer;
        _fast_data.pressure_inhale = readings_avgs.pressure_inhale;
        _fast_data.pressure_patient = readings_avgs.pressure_patient;
        _fast_data.temperature_buffer = readings_avgs.temperature_buffer;
        _fast_data.pressure_o2_supply = readings_avgs.pressure_o2_supply;
        _fast_data.pressure_o2_regulated = readings_avgs.pressure_o2_regulated;
        _fast_data.pressure_diff_patient = readings_avgs.pressure_diff_patient;

        _plSend.setPayload(PAYLOAD_TYPE::DATA, reinterpret_cast<void *>(&_fast_data), sizeof(_fast_data));
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
        float vinhale, vexhale;
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

        _readback_data.ventilation_mode = _breathing_loop->getVentilationMode();

        _readback_data.valve_inhale_percent = 0;  //TODO
        _readback_data.valve_exhale_percent = 0;  //TODO
        _readback_data.valve_inhale_percent = _breathing_loop->getValveInhalePercent();
        _readback_data.valve_exhale_percent = _breathing_loop->getValveInhalePercent();
        _readback_data.valve_air_in_enable  = _breathing_loop->valveAirInEnabled();
        _readback_data.valve_o2_in_enable  = _breathing_loop->valveO2InEnabled();
        _readback_data.valve_purge_enable  = _breathing_loop->valvePurgeEnabled();
        _readback_data.inhale_trigger_enable = _breathing_loop->inhaleTriggerEnabled();
        _readback_data.exhale_trigger_enable = _breathing_loop->exhaleTriggerEnabled();
        // _readback_data.peep = _breathing_loop->peep();
        _readback_data.inhale_exhale_ratio = _breathing_loop->getIERatio();

        _plSend.setPayload(PAYLOAD_TYPE::DATA, reinterpret_cast<void *>(&_readback_data), sizeof(_readback_data));
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

        _plSend.setPayload(PAYLOAD_TYPE::DATA, reinterpret_cast<void *>(&_cycle_data), sizeof(_cycle_data));
        _comms->writePayload(_plSend);
        _cycle_report_time = tnow;
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
        default:
            break;
    }
}

void UILoop::cmdSetDuration(cmd_format &cf) {
    setDuration(static_cast<CMD_SET_DURATION>(cf.cmd_code), _breathing_loop->getDurations(), cf.param);
}

void UILoop::cmdSetMode(cmd_format &cf) {
    ;
}

void UILoop::cmdSetThresholdMin(cmd_format &cf) {
    setThreshold(static_cast<ALARM_CODES>(cf.cmd_code), _alarm_loop->getThresholdsMin(), cf.param);
}

void UILoop::cmdSetThresholdMax(cmd_format &cf) {
    setThreshold(static_cast<ALARM_CODES>(cf.cmd_code), _alarm_loop->getThresholdsMax(), cf.param);
}


