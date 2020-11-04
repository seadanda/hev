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


import sys
import re
import queue
import time
import datetime

#import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def integral(ar_x, ar, trigger = 0., leak_correction = 0.): # array integral
    _result = 0.

    _ar_result = []

    sum_leak_correction = 0.

    for i in range(len(ar)):
        if type(trigger) != type(float(0.)) and trigger[i]:
            _result = 0.

        dt = 0.

        if i == 0: dt = 0.011
        else: dt = (ar_x[i]-ar_x[i-1])*0.001

        _result += ar[i]*dt - (1000.*dt*leak_correction)

        sum_leak_correction += dt*1000.*leak_correction

        print(sum_leak_correction)

        if type(trigger) != type(float(0.)) and trigger[i]:
            _result = 0.

        _ar_result.append(_result)

    print("integral: ",len(_ar_result))

    return np.array(_ar_result)

def DP2flow(DP): #has to be a numpy array input

    mp = 1172.9576458344243
    bp = 22.709191997369555

    mm = 1084.6514479521688 
    bm = -16.797482131038645

    temp_flow = []

    for i in range(len(DP)):

        _temp_flow = DP[i]

        if _temp_flow > 0.:
            temp_flow.append( mp*_temp_flow + bp )
        else:
            temp_flow.append( mm*_temp_flow + bm )

    print("length of flow: ",len(temp_flow))

    return np.array(temp_flow)

def linear_fit_derivative(xtime, ar, samplesfit):

    result = []

    for i in range(len(ar)):

            if i > samplesfit and i < len(ar)-samplesfit:

                (_dpbuff,offbuff) = np.polyfit(xtime[i-samplesfit:i+samplesfit]*1e-3,   ar[i-samplesfit:i+samplesfit], 1)

            else:

                (_dpbuff,offbuff) = (0,0)

            result.append(_dpbuff) 

    return np.array(result)

def euler_flow_calc(xtime, pbuff, pinhale, trigger = 0., vbuff = 10.*1000., vtube = 1.6*1000.):

    pinhale = pinhale   + 1013. # absolute pressure in mba
    pbuff   = pbuff     + 1013. # absolute pressure in mbar

    _vlung = 0.

    list_vlung = []
    list_buffer_flow = []

    dpbuff   = linear_fit_derivative(xtime, pbuff, 15) # already in seconds
    dpinhale = linear_fit_derivative(xtime, pinhale, 15) # already in seconds

    for i in range(len(pbuff)):

        print(i*1./len(pbuff))

        _buffer_flow = ((-1./pinhale[i]) * ( ( dpinhale[i] * vtube) + ( dpbuff[i] * vbuff + (_vlung)) ) ) - (0.75*4*(dpinhale[i]))
        list_buffer_flow.append(_buffer_flow)

        _vlung += _buffer_flow*0.011

        if type(trigger) != type(float(0.)) and trigger[i]:
            _vlung = 0.

        list_vlung.append(_vlung)

    return (np.array(list_vlung), np.array(list_buffer_flow)) 

def buffer_flow_pbuff(xtime, pbuff, pinhale, vbuff = 10.*1000., vtube = 1.6*1000.):# inputs should be numpy arrays

    pinhale = pinhale   + 1013. # absolute pressure in mba
    pbuff   = pbuff     + 1013. # absolute pressure in mbar
    ptube   = pinhale   + 1013. # absolute pressure in mbar

    dpbuff = []
    dptube = []

    counter = 0.

    fooflow = 0.

    running_avg = []
    running_avg_tube = []

    for i in range(len(pbuff)):

        if counter == 0. :#or i >= len(pbuff)-2 :
            dpbuff.append(0.)
            dptube.append(0.)

        else:

            _dpbuff = (pbuff[i]   - pbuff[i-1]  ) #* 100. # mbar to Pa
            _dptube = (pinhale[i] - pinhale[i-1]) #* 100. # mbar to Pa
            dt      = (xtime[i]   - xtime[i-1])     * 1e-3 # ms to seconds 

            _dpbuff /= dt
            _dptube /= dt

            samplesfit = 10

            if i > samplesfit and i < len(pbuff)-samplesfit:

                (_dpbuff,offbuff) = np.polyfit(xtime[i-samplesfit:i+samplesfit]*1e-3,   pbuff[i-samplesfit:i+samplesfit], 1)
                (_dptube,offtube) = np.polyfit(xtime[i-samplesfit:i+samplesfit]*1e-3, pinhale[i-samplesfit:i+samplesfit], 1)

            else:

                (_dpbuff,offbuff) = (0,0)
                (_dptube,offtube) = (0,0)

            dpbuff.append(_dpbuff) 
            dptube.append(_dptube) 

        counter += 1.


    _buffer_flow = ((-1./pinhale) * ( ( np.array(dptube) * vtube) + ( np.array(dpbuff) * vbuff ) ) ) - (1.00*4*(np.array(dptube)))
    #Clear plastique correction from https://link.springer.com/article/10.1007/BF01709728
    #+ ( np.array(dptube) * vtube ) )

    avg_buffer_flow = []
    running_buffer_flow = []

    _temp_buffer_flow = 0.

    for i in range(len(_buffer_flow)):
        #running_buffer_flow.append(_buffer_flow[i])

        #if len(running_buffer_flow) > 1: del running_buffer_flow[0]

        #avg_buffer_flow.append(sum(running_buffer_flow)/1.)

        #_temp_buffer_flow = _temp_buffer_flow*0.6 + _buffer_flow[i]*0.3
        _temp_buffer_flow = _buffer_flow[i]

        avg_buffer_flow.append(_temp_buffer_flow)


    print(len(avg_buffer_flow))

    return np.array(avg_buffer_flow)

def buffer_flow_1225(xtime, pbuff, pinhale, vbuff = 11.0*1000., vtube = 2.*1000.):# inputs should be numpy arrays

    pinhale = pinhale + 1013. # absolute pressure in mba
    pbuff   = pbuff   + 1013. # absolute pressure in mbar
    ptube   = pbuff   + 1013. # absolute pressure in mbar

    avg_pinhale = []
    avg_pbuff   = []

    for i in range(len(pinhale)):
        if i == 0:
            avg_pinhale.append(pinhale*0.3)
            avg_pbuffer.append(pbuffer*0.3)
        else:
            avg_pinhale.append(avg_pinhale[-1]*0.6+pinhale*0.3)
            avg_pbuffer.append(avg_pbuffer[-1]*0.6+pbuffer*0.3)


    dpbuff = []
    dptube = []
    counter = 0.

    fooflow = 0.

    running_avg = []
    running_avg_tube = []

    for i in range(len(pbuff)):

        if counter == 0.:
            dpbuff.append(0.)
            dptube.append(0.)

        else:

            _dpbuff = (pbuff[i]   - pbuff[i-1]  ) #* 100. # mbar to Pa
            _dptube = (pinhale[i] - pinhale[i-1]) #* 100. # mbar to Pa
            dt      = (xtime[i]   - xtime[i-1])     * 1e-3 # ms to seconds 

            _dpbuff /= dt
            _dptube /= dt

            if i > 10 and i < len(pbuff)-10:

                (_dpbuff,offbuff) = np.polyfit(xtime, pbuff[i-10:i+10], 1)
                (_dptube,offtube) = np.polyfit(xtime, pbuff[i-10:i+10], 1)

            else:

                (_dpbuff,offbuff) = (0,0)
                (_dptube,offtube) = (0,0)


            #running_avg_dpbufftube.append(_flow)
            #running_avg_dptube.append(_flow)
            #if len(running_avg) > 5: 
            #    del running_avg[0]

            #fsum = sum(running_avg)

            #print(_flow)
            
            #fooflow = fsum/5.#_flow #fooflow + (0.1*_flow)

            #print(fooflow)

            dpbuff.append(_dpbuff) 
            dptube.append(_dptube) 

        counter += 1.

    _buffer_flow = (-1./2000) * ( ( np.array(dptube) * vtube ) + ( np.array(dpbuff) * vbuff ) )# + ( np.array(dptube) * vtube ) )

    avg_buffer_flow = []
    running_buffer_flow = []

    _temp_buffer_flow = 0.

    for i in range(len(_buffer_flow)):
        running_buffer_flow.append(_buffer_flow[i])

        if len(running_buffer_flow) > 1: del running_buffer_flow[0]

        avg_buffer_flow.append(sum(running_buffer_flow)/1.)

        #_temp_buffer_flow = _temp_buffer_flow*0.6 + _buffer_flow[i]*0.3

        #avg_buffer_flow.append(_temp_buffer_flow)

    #R = 8.31446261815324 # gas contact in SI units J.K-1 mol-1
    #T = 300              # ~ 25 degrees celsius

    #buffer_flow /= (R*T) # number of mols

    #buffer_flow *= 22.4 * 1000. * 1000.# conversion for mol to liter and from liter to ml

    print(len(avg_buffer_flow))

    return np.array(avg_buffer_flow)

counter = 0

history_length = 5000

xtime = queue.Queue(history_length)
pressure_buffer = queue.Queue(history_length)
pressure_inhale = queue.Queue(history_length)
pressure_patient = queue.Queue(history_length)
pressure_diff_patient = queue.Queue(history_length)
PID_P = queue.Queue(history_length)
PID_I = queue.Queue(history_length)
PID_D = queue.Queue(history_length)

def derivative(l):
    result = []
    for i in range(len(l)):
        if i != 0 :
            result.append(l[i]-l[i-1])
        else:
            result.append(0)
    return result

def derivative_exp(l):
    _exp_mean = 0.
    result = []
    for i in range(len(l)):
        if i != 0 :
            _exp_mean = (0.7*_exp_mean) + (0.3*(l[i]-l[i-1]))
            result.append(_exp_mean)
        else:
            result.append(0)
    return result

def derivative_withthreshold(l, lmin):
    result = []
    for i in range(len(l)):
        if i != 0 :
            _result = (l[i]-l[i-1])
            if _result < lmin and _result > -1*lmin: _result = 0.
            if _result > lmin: _result -= lmin
            if _result < -1*lmin: _result += lmin
            result.append(_result)
        else:
            result.append(0)
    return result



for i in range(history_length):
    pressure_buffer.put(-1)
    pressure_inhale.put(-1)
    pressure_patient.put(-1)
    pressure_diff_patient.put(-50)
    PID_P.put(-1)
    PID_I.put(-1)
    PID_D.put(-1)
    xtime.put(-1)


#plt.ion()

#for i in range(10): pressure_inhale.put(-1)

fig = plt.figure()

ax3 = fig.add_subplot(221)
ax4 = fig.add_subplot(224)
h1, = ax3.plot([],[], "+-", label="buffer")


ax = fig.add_subplot(223)

h2, = ax.plot([],[], "+-", label="inhale")
h3, = ax4.plot([],[], "+-", label="Proportional")
h4, = ax4.plot([],[], "+-", label="Integral")

h6, = ax.plot([],[], "+-", label="Patient")

#plt.axes()
#an = []

#ai, = ax.plot(range(10), range(10))
#an.append(ai)

#fig.canvas.draw()
#plt.show(block=False)

x = 1
#plt.show()
#time.sleep(10)

#airway_pressure = Proportional
#volume = Integral
#flow = Derivative


logfile =open(sys.argv[1]) 
_data = logfile.readlines()

#try:
counter += 1.
#data = sys.stdin.readline()
#print("reading file "+sys.argv[1])
if not _data: sys.exit()
#print(data)

x0 = -99999

for _entry in _data:
    data = re.split(",", _entry)
    #print(data)
    xtime.get()
    _time = data[0]
    #print(_time)
    x = time.strptime(_time,'%Y-%m-%d %H:%M:%S')
    #print(x)
    #print(time.mktime(x))
    #print(float(data[1][:3]))
    if x0 == -99999:
        x0 = time.mktime(x)*1000 + float(data[1][:3])
    x = time.mktime(x)*1000+float(data[1][:3])
    xtime.put(x)
    for entry in data:
        if "pressure_diff_patient" in entry and not "mean" in entry: 
            _diff_patient_p = float( entry.strip().split("=")[-1] )
            pressure_diff_patient.get()
            pressure_diff_patient.put(_diff_patient_p)
            #print(len(list(pressure_inhale.queue)))
            #fig.canvas.draw()
            #fig.canvas.flush_events()
            #plt.show()

        if "pressure_patient" in entry and not "mean" in entry: 
            _patient_p = float( entry.strip().split("=")[-1] )
            pressure_patient.get()
            pressure_patient.put(_patient_p)
            #print(len(list(pressure_inhale.queue)))
            #fig.canvas.draw()
            #fig.canvas.flush_events()
            #plt.show()

        if "pressure_inhale" in entry and not "mean" in entry: 
            _inhale_p = float( entry.strip().split("=")[-1] )
            pressure_inhale.get()
            pressure_inhale.put(_inhale_p)
            #print(len(list(pressure_inhale.queue)))
            #fig.canvas.draw()
            #fig.canvas.flush_events()
            #plt.show()

        if "pressure_buffer" in entry and not "mean" in entry: 
            _buffer_p = float( entry.strip().split("=")[-1] )
            pressure_buffer.get()
            pressure_buffer.put(_buffer_p)
            #print(len(list(pressure_inhale.queue)))
            #fig.canvas.draw()
            #fig.canvas.flush_events()
            #plt.show()

        if "airway_pressure" in entry and not "mean" in entry: 
            _PID_P = float( entry.strip().split("=")[-1] )
            PID_P.get()
            PID_P.put(_PID_P*100)
            #print(len(list(pressure_inhale.queue)))
            #fig.canvas.draw()
            #fig.canvas.flush_events()
            #plt.show()

        if "volume" in entry and ")" in entry: 
            _PID_I = float( entry.strip().split("=")[-1][:-1] )
            #print(_PID_I)
            PID_I.get()
            PID_I.put(_PID_I*100)
            #print(len(list(pressure_inhale.queue)))
            #fig.canvas.draw()
            #fig.canvas.flush_events()
            #plt.show()

        if "flow" in entry: 
            _PID_D = float( entry.strip().split("=")[-1] )
            PID_D.get()
            PID_D.put(_PID_D)
            #print(len(list(pressure_inhale.queue)))
            #fig.canvas.draw()
            #fig.canvas.flush_events()
            #plt.show()


#sys.stdout.write(data)
#sys.stdout.flush()
#if counter > 10: fig.savefig('test.png')
#except KeyboardInterrupt:
#    print('exiting')
#    sys.exit()

ar_xtime = np.array(list(xtime.queue))
#ar_xtime = np.flip(ar_xtime)

print(ar_xtime)

ar_xtime = ar_xtime - ar_xtime[0]

print(ar_xtime)

print(ar_xtime[-10:])

ar_pressure_buffer  = np.array(list(pressure_buffer.queue))
ar_pressure_inhlale = np.array(list(pressure_inhale.queue))
ar_pressure_patient = np.array(list(pressure_patient.queue))

ar_pressure_PID_P   = np.array(list(PID_P.queue))
ar_pressure_PID_I   = np.array(list(PID_I.queue))
ar_pressure_PID_D   = np.array(list(PID_D.queue))

ar_flow               = DP2flow(ar_pressure_PID_D)

h1.set_xdata(ar_xtime)
h1.set_ydata(ar_pressure_buffer)#list(pressure_inhale.queue))

plt.legend()

h2.set_xdata(ar_xtime)
h2.set_ydata(ar_pressure_inhlale)#list(pressure_buffer.queue))

h3.set_xdata(ar_xtime)
h3.set_ydata(ar_pressure_PID_P)#list(pressure_buffer.queue))
#
h4.set_xdata(ar_xtime)
h4.set_ydata(ar_pressure_PID_I)#list(pressure_buffer.queue))

plt.legend()
#
h6.set_xdata(ar_xtime)
h6.set_ydata(ar_pressure_patient)#list(pressure_buffer.queue))

plt.legend()

ax2 = fig.add_subplot(222)

h12, = ax2.plot([],[], "+-", label="calc buffer flow")

h13, = ax2.plot([],[], "+-", label="calc buffer volume")

h14, = ax2.plot([],[], "+-", label="calc volume measured")

h15, = ax2.plot([],[], "+-", label="calc volume Euler")
h16, = ax2.plot([],[], "+-", label="calc flow Euler")

h5, = ax2.plot([],[], "+-", label="Flow (DP sensor)")

b_flow = buffer_flow_pbuff(ar_xtime, 
        ar_pressure_buffer, 
        ar_pressure_inhlale)#, 
#        vbuff = 10.)# inputs should be numpy arrays

h12.set_xdata(ar_xtime)
h12.set_ydata(b_flow)

h13.set_xdata(ar_xtime)

reset_trigger = ( ar_flow < 0. )

(fbm,fbb) = np.polyfit(ar_xtime, integral(ar_xtime, b_flow, reset_trigger), 1)

print("Estimated leak rate (buff. calc.): %f ml/s" % (fbm*1000.))

#h13.set_ydata(integral(ar_xtime, b_flow, reset_trigger) - (ar_xtime*fbm) - fbb)

#
h5.set_xdata(ar_xtime)
h5.set_ydata(ar_flow)#list(pressure_buffer.queue))


h14.set_xdata(ar_xtime)

(fm,fb) = np.polyfit(ar_xtime, integral(ar_xtime, ar_flow, reset_trigger), 1)

#h14.set_ydata(integral(ar_xtime, ar_flow, reset_trigger) - (ar_xtime*fm) - fb)
h14.set_ydata(integral(ar_xtime, ar_flow, reset_trigger))

print("Estimated leak rate: %f ml/s" % (fm*1000.))

h13.set_ydata(integral(ar_xtime, b_flow, reset_trigger, fm))

(euler_volume, euler_flow) = euler_flow_calc(ar_xtime, ar_pressure_buffer, ar_pressure_inhlale, reset_trigger)

h15.set_xdata( ar_xtime )
h15.set_ydata( euler_volume )

h16.set_xdata( ar_xtime )
h16.set_ydata( euler_flow )

plt.legend()
#plt.ylim(-2,20)

ax.relim()
ax2.relim()
ax3.relim()
ax4.relim()

ax.autoscale_view(True,True,True)
ax2.autoscale_view(True,True,True)
ax3.autoscale_view(True,True,True)
ax4.autoscale_view(True,True,True)
#fig.canvas.draw()
#fig.canvas.flush_events()
plt.show()
#time.sleep(0.1)

print(np.cov(ar_pressure_buffer,ar_pressure_inhlale))

#plt.plot(ar_pressure_patient, ar_pressure_inhlale)
#plt.show()

plt.plot(ar_xtime, 2.0*ar_pressure_inhlale*4)
plt.show()

plt.plot(ar_xtime, euler_flow_calc(ar_xtime, ar_pressure_buffer, ar_pressure_inhlale, reset_trigger)-integral(ar_xtime, ar_flow, reset_trigger), label="euler flow error")
plt.plot(ar_xtime, integral(ar_xtime, b_flow, reset_trigger, fm)-integral(ar_xtime, ar_flow, reset_trigger), label="buf flow error")

plt.legend()

plt.show()


h15.set_xdata(ar_xtime)
h15.set_ydata( euler_flow_calc(ar_xtime, ar_pressure_buffer, ar_pressure_inhlale, reset_trigger) )

logfile.seek(0)
logfile.close()
