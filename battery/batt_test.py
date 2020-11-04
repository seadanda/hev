# © Copyright CERN, Riga Technical University and University of Liverpool 2020.
# All rights not expressly granted are reserved. 
# 
# This file is part of hev-sw.
# 
# hev-sw is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public Licence as published by the Free
# Software Foundation, either version 3 of the Licence, or (at your option)
# any later version.
# 
# hev-sw is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public Licence
# for more details.
# 
# You should have received a copy of the GNU General Public License along
# with hev-sw. If not, see <http://www.gnu.org/licenses/>.
# 
# The authors would like to acknowledge the much appreciated support
# of all those involved with the High Energy Ventilator project
# (https://hev.web.cern.ch/).


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
import datetime

pin_bat     = 5
pin_ok      = 6
pin_alarm   = 12
pin_rdy2buf = 13
pin_bat85   = 19
pin_prob_elec   = 7

gpio.setmode(gpio.BCM)

gpio.setup(pin_bat     , gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(pin_ok      , gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(pin_alarm   , gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(pin_rdy2buf , gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(pin_bat85   , gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(pin_prob_elec , gpio.IN, pull_up_down=gpio.PUD_DOWN)

log = open('batt.log', 'w')
while True : 
    bat     = gpio.input(pin_bat    ) 
    ok      = gpio.input(pin_ok     ) 
    alarm   = gpio.input(pin_alarm  ) 
    rdy2buf = gpio.input(pin_rdy2buf) 
    bat85   = gpio.input(pin_bat85  ) 
    prob_elec = gpio.input(pin_prob_elec  ) 
    
    dt = datetime.datetime.now()

    print(f"{dt} BAT={bat} OK={ok} ALARM={alarm} RDY2BUF={rdy2buf} BAT>85={bat85} PROB_ELEC={prob_elec}")
    
    log.write(f"{dt} BAT={bat} OK={ok} ALARM={alarm} RDY2BUF={rdy2buf} BAT>85={bat85} PROB_ELEC={prob_elec}\n")
    sleep(1)
