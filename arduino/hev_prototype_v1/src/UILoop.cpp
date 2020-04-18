#include "UILoop.h"
// #include "BreathingLoop.h"

UILoop::UILoop(BreathingLoop *bl)
{
    _breathing_loop = bl;
}

UILoop::~UILoop()
{;}

int UILoop::doCommand(cmdFormat *cf)
{
    
    switch(cf->cmdCode){
        case 0x1 : _breathing_loop->doStart(); 
        break;
        case 0x2 : _breathing_loop->doStop(); 
        break;
        default:
        break;
    }
    return 0;
}