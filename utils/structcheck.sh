#!/usr/bin/env bash
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


set -euo pipefail

for struct in fast_data_format readback_data_format cycle_data_format cmd_format alarm_format; do
    structtype=${struct%%_*}
    echo '@dataclass'
    sed -e "/struct $struct/,/};/!d" -e "/struct $struct/!d" -e "s/struct .* {/class ${structtype^}Format(BaseFormat):/" ../arduino/hev_prototype_v1/src/common.h;
    sed -e "/struct $struct/,/};/!d" -e "s/struct $struct.*/_dataStruct = Struct(\"</" -e '/};/d' -e 's/uint\(.*\)_t.*/\1/g' -e 's/.*8.*/B/g' -e 's/.*16.*/H/g' -e 's/.*32.*/I/g' -e 's/.*float.*/I/g' -e 's/\/\/.*//g' ../arduino/hev_prototype_v1/src/common.h | sed -e ':a;N;$!ba;s/\n//g' -e 's/^/    /' -e 's/$/\")/';
    echo "    _type = PAYLOAD_TYPE.${structtype^^}"
    sed -e "/struct $struct/,/};/!d" -e "/struct $struct/d" -e '/};/d' -e 's/struct \(.*\) {/class \1(BaseFormat):/' -e 's/uint8_t //g' -e 's/uint16_t//g' -e 's/uint32_t//g' -e 's/float//g' -e 's/\/\/.*//g' -e 's/::/./g' -e 's/;$//' -e 's/^[ \t]*/    /' ../arduino/hev_prototype_v1/src/common.h;
    echo
done
