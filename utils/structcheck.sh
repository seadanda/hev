#!/usr/bin/env bash
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
