#!/bin/bash
curl -fsSL https://raw.githubusercontent.com/platformio/platformio-core-installer/master/get-platformio.py -o get-platformio.py
python3 get-platformio.py

PATH=$PATH:$HOME/.platformio/penv/bin

proj=$HOME/blink
mkdir -p $proj
cd $proj
pio project init -b nodemcu-32s 
cat << EOF > src/main.cpp
#include <Arduino.h>

// Set LED_BUILTIN if it is not defined by Arduino framework
// #define LED_BUILTIN 2

void setup()
{
  // initialize LED digital pin as an output.
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop()
{
  // turn the LED on (HIGH is the voltage level)
  digitalWrite(LED_BUILTIN, HIGH);
  // wait for a second
  delay(1000);
  // turn the LED off by making the voltage LOW
  digitalWrite(LED_BUILTIN, LOW);
   // wait for a second
  delay(1000);
}
EOF
pio lib  --global install 5516 #VariableTimedAction
pio lib  --global install 5390 # RingBuffer
pio lib  --global install 5418 # uCRC16Lib
pio lib  --global install 5574 # INA2xx
pio lib  --global install  820 # Adafruit MCP9808 
pio run 
pio run -t nobuild -t upload
