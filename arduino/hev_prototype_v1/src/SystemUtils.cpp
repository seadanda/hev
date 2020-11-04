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
