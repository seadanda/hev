#!/usr/bin/python3

# Simple UPS battery checker 
#
#   BAT: Battery power OK
#   OK: mains power OK
#   ALARM: Battery disconnected or failure
#   Ready to buffer: Battery available
#   Bat>85%: Battery is charged at >85% this value could not be changed.
#
#   DIP switches 4,5,6,7,8 must be enabled 

import RPi.GPIO as gpio
from time import sleep

pin_bat     = 5
pin_ok      = 6
pin_alarm   = 12
pin_rdy2buf = 13
pin_bat85   = 19

gpio.setmode(gpio.BCM)

gpio.setup(pin_bat     , gpio.IN)
gpio.setup(pin_ok      , gpio.IN)
gpio.setup(pin_alarm   , gpio.IN)
gpio.setup(pin_rdy2buf , gpio.IN)
gpio.setup(pin_bat85   , gpio.IN)

while True : 
    bat     = gpio.input(pin_bat    ) 
    ok      = gpio.input(pin_ok     ) 
    alarm   = gpio.input(pin_alarm  ) 
    rdy2buf = gpio.input(pin_rdy2buf) 
    bat85   = gpio.input(pin_bat85  ) 

    print(f"BAT={bat} OK={ok} ALARM={alarm} RDY2BUF={rdy2buf} BAT>85={bat85}")
    sleep(1)
