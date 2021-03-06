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


#ifndef SYSTEMUTILS_H
#define SYSTEMUTILS_H

#include <Arduino.h>
#include <Adafruit_MCP9808.h>
#include <Wire.h>

class SystemUtils
{
	public:
		SystemUtils();
		~SystemUtils();
		void  setupTempSensor(Adafruit_MCP9808 *tempsens, TwoWire *i2c);
		float getSystemTemperature();
	private:
		Adafruit_MCP9808 *_temp_sensor;
		bool _found_MCP9808 ;
};
#endif
