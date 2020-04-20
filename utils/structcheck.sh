#!/usr/bin/env bash
set -euo pipefail

for struct in data_format cmd_format alarm_format; do
    echo $struct;
    sed -e "/struct $struct/,/};/!d" -e "s/struct $struct.*/self._dataStruct = Struct(\"</" -e '/};/d' -e 's/enum \(.*\) {/class \1(Enum):/' -e 's/uint\(.*\)_t.*/\1/g' -e 's/.*8.*/B/g' -e 's/.*16.*/H/g' -e 's/.*32.*/I/g' ../arduino/common/lib/CommsControl/CommsCommon.h | sed -e ':a;N;$!ba;s/\n//g' -e 's/$/\")/';
done
