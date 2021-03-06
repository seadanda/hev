#!/bin/bash
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



sketch=Multiloop_skeleton

arduino-cli config init
arduino-cli core update-index
arduino-cli board list
arduino-cli core install arduino:avr
arduino-cli core install arduino:samd

arduino-cli lib install VariableTimedAction
port=$(arduino-cli board list | grep 'arduino:' | head -1 | sed 's/ .*//')
fqbn=$(arduino-cli board list --format=json | sed 's/"//g' | grep 'FQBN' | head -1 | awk '{ print $2 }')

arduino-cli compile --fqbn $fqbn  $sketch
arduino-cli upload -p $port --fqbn $fqbn $sketch

# to run serial console 
# minicom -D $port -b 9600 # or whatever the baud is set to
# to quit > enter, ctrl-a, q, enter

