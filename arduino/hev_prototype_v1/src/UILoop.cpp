#include "UILoop.h"
// #include "BreathingLoop.h"

UILoop::UILoop(BreathingLoop *bl)
{
    _breathing_loop = bl;
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
        case 0x1 : _breathing_loop->doStart();
            break;
        case 0x2 : _breathing_loop->doStop();
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
    setThreshold(static_cast<ALARM_CODES>(cf->cmd_code), alarm_threshold_min, cf->param);
}

void UILoop::cmdSetThresholdMax(cmd_format *cf) {
    setThreshold(static_cast<ALARM_CODES>(cf->cmd_code), alarm_threshold_max, cf->param);
}


