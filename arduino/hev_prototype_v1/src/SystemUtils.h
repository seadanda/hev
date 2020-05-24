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
