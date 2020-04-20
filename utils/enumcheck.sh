#!/usr/bin/env bash
set -euo pipefail

for enum in CMD_TYPE CMD_GENERAL CMD_SET_TIMEOUT CMD_SET_MODE ALARM_TYPE ALARM_CODES; do
    sed -e "/enum $enum/,/};/!d" -e '/};/d' -e 's/,$//g' -e 's/,\([[:blank:]]*\)\/\/\(.*\)/\1 #\2/g' -e 's@//@#@g' -e "s/enum \([[:graph:]]*\) .*{/class \1(Enum):/" ../arduino/hev_prototype_v1/src/common.h;
    echo;
done

