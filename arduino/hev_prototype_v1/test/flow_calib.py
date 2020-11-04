#!/usr/bin/python3
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



