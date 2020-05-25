#include "SystemUtils.h"

SystemUtils::SystemUtils()
{
	_found_MCP9808 = false;
}

SystemUtils::~SystemUtils(){}

void SystemUtils::setupTempSensor(Adafruit_MCP9808 *tempsens, TwoWire *i2c)
{
    _temp_sensor = tempsens;
    int ntries = 3;
    while(!_temp_sensor->begin(0x18, i2c) && ntries > 0) {
        delay(1000); 
        ntries--;
    } 
    if (ntries > 0)
        _found_MCP9808 = true;
    if (_found_MCP9808){
        _temp_sensor->setResolution(3);
		_temp_sensor->wake();  //sensor on
    }
}

float SystemUtils::getSystemTemperature()
{
	if(_found_MCP9808 == true){
		//_temp_sensor->wake();  //sensor on
		float c = _temp_sensor->readTempC();
		//_temp_sensor->shutdown_wake(1); //sensor off
		return c;
	}
	return -273.15;
}
