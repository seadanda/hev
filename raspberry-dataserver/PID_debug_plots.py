#!/usr/bin/python3
import sys
import re
import queue
import time
import datetime

#import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

"""
2020-06-05 13:59:34,639 - WARNING - Received more than 20 sequence_receive mismatches, resetting
2020-06-05 13:59:34,648 - INFO - payload received: DataFormat(version=174, timestamp=1686098, payload_type=<PAYLOAD_TYPE.DATA: 1>, fsm_state=<BL_STATES.IDLE: 1>, pressure_air_supply=30, pressure_air_regulated=482.0126647949219, pressure_o2_supply=0, pressure_o2_regulated=484.6713562011719, pressure_buffer=247.3388671875, pressure_inhale=41.958984375, pressure_patient=63.873046875, temperature_buffer=659, pressure_diff_patient=6.836583137512207, ambient_pressure=0, ambient_temperature=0, airway_pressure=0.0, flow=0.0, volume=0.0)
2020-06-05 13:59:34,663 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:34,695 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:34,712 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:34,727 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:34,743 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:34,759 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:34,775 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:34,791 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:34,808 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:34,823 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:34,839 - INFO - payload received: DataFormat(version=174, timestamp=1686298, payload_type=<PAYLOAD_TYPE.DATA: 1>, fsm_state=<BL_STATES.IDLE: 1>, pressure_air_supply=35, pressure_air_regulated=482.15771484375, pressure_o2_supply=0, pressure_o2_regulated=484.9775390625, pressure_buffer=247.3388671875, pressure_inhale=42.1201171875, pressure_patient=64.01806640625, temperature_buffer=659, pressure_diff_patient=6.840445518493652, ambient_pressure=0, ambient_temperature=0, airway_pressure=0.0, flow=0.0, volume=0.0)
2020-06-05 13:59:34,854 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:34,869 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:34,885 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:34,902 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:34,917 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:34,934 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:34,950 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:34,990 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:35,006 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE
2020-06-05 13:59:35,022 - INFO -  PID 0.001000 0.000500 0.001000 -0.000922 0.019901 0.012144 0.548992 15.000000 15.921995 fsm BL_STATES.IDLE

"""

inputfile = sys.argv[1]

f = open(inputfile, "r")

all_matches = re.findall("(\d+-\d+-\d+ \d+:\d+:\d+),(\d+).+INFO.+PID (-?\d+.\d+) (-?\d+.\d+) (-?\d+.\d+) (-?\d+.\d+) (-?\d+.\d+) (-?\d+.\d+) (-?\d+.\d+) (-?\d+.\d+) (-?\d+.\d+) fsm BL_STATES.(\w+)", f.read())


(datetime, milliseconds, kp, ki, kd, P, I, D, PID_target, pwm_output, process_variable, fsm_state) = ([], [], [], [], [], [], [], [], [], [], [], [])

data_dict = {
        "datetime":[], 
        "milliseconds":[], 
        "kp":[], 
        "ki":[], 
        "kd":[], 
        "P":[], 
        "I":[],
        "D":[],
        "PID_target":[],
        "pwm_output":[],
        "process_variable":[],
        "fsm_state":[]
        }
 

for match in all_matches:
    "('2020-06-05 14:03:44', '673', '0.001000', '0.000500', '0.001000', '-0.000936', '0.026022', '0.030116', '0.555116', '15.000000', '15.936196', 'EXHALE')"

    #print(match)

    (_datetime, _milliseconds, _kp, _ki, _kd, _P, _I, _D, _pwm_output, _PID_target, _process_variable, _fsm_state) = match

    data_dict["datetime"].append(_datetime)

    data_dict["datetime"].append(_datetime)
    data_dict["milliseconds"].append(_milliseconds)
    data_dict["kp"].append(float(_kp))
    data_dict["ki"].append(float(_ki))
    data_dict["kd"].append(float(_kd))
    data_dict["P"].append(100*float(_P))
    data_dict["I"].append(100*float(_I))
    data_dict["D"].append(100*float(_D)*float(_kd))
    data_dict["PID_target"].append(float(_PID_target))
    data_dict["pwm_output"].append(100*(float(_pwm_output)-0.53))
    data_dict["process_variable"].append(float(_process_variable))
    data_dict["fsm_state"].append(_fsm_state)

plt.plot(data_dict["P"],                label="proportional",     linewidth = 3)
plt.plot(data_dict["I"],                label="Integral",         linewidth = 3)
plt.plot(data_dict["D"],                label="Derivative",       linewidth = 3)
plt.plot(data_dict["PID_target"],       label="PID_target",       linewidth = 3)
plt.plot(data_dict["pwm_output"],       label="pwm_output",       linewidth = 3)
plt.plot(data_dict["process_variable"], label="process_variable", linewidth = 3)

plt.title("PID P=%.1e I=%.1e D=%.1e" % (data_dict["kp"][-1], data_dict["ki"][-1], data_dict["kd"][-1] ) )

plt.legend()

plt.show()
