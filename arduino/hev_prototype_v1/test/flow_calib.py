#!/usr/bin/python3

# from Oscar's excel sheet

import math
import pandas as pd


df=pd.read_csv('oscar.txt')
vdd_oscar = 5.0

for i in range(len(df)): 
    # dp_raw = Aout/VDD (according to pdf)
    #dp_raw = _readings_avgs.pressure_diff_patient / 4096.0 # assuming 12bit ADC
    dp_raw = df.voltage[i]/vdd_oscar

    sign = 0.0
    if (dp_raw -0.5) < 0 : sign = -1 
    else : sign = 1

    dp = 100. * sign*math.pow(((dp_raw/0.4)-1.25),2) * 5.25
    print(dp, df.flow[i], df.flow[i]/dp)



