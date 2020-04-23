#include "UILoop.h"
// #include "BreathingLoop.h"

UILoop::UILoop(BreathingLoop *bl, AlarmLoop *al)
{
    _breathing_loop = bl;
    _alarm_loop     = al;
}

UILoop::~UILoop()
{;}

int UILoop::doCommand(cmd_format *cf)
{
    switch(cf->cmd_type) {
        case CMD_TYPE::GENERAL:
            cmdGeneral(cf);
            break;
        case CMD_TYPE::SET_TIMEOUT:
            cmdSetTimeout(cf);
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

void UILoop::cmdGeneral(cmd_format *cf) {
    switch (cf->cmd_code) {
        case CMD_GENERAL::START : _breathing_loop->doStart();
            break;
        case CMD_GENERAL::STOP : _breathing_loop->doStop();
            break;
        default:
            break;
    }
}

void UILoop::cmdSetTimeout(cmd_format *cf) {
    setTimeout(static_cast<CMD_SET_TIMEOUT>(cf->cmd_code), _breathing_loop->getTimeouts(), cf->param);
}

void UILoop::cmdSetMode(cmd_format *cf) {
    ;
}

void UILoop::cmdSetThresholdMin(cmd_format *cf) {
    setThreshold(static_cast<ALARM_CODES>(cf->cmd_code), _alarm_loop->getThresholdsMin(), cf->param);
}

void UILoop::cmdSetThresholdMax(cmd_format *cf) {
    setThreshold(static_cast<ALARM_CODES>(cf->cmd_code), _alarm_loop->getThresholdsMax(), cf->param);
}


