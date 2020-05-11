import sys
import re
import queue
import time

#import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

counter = 0

history_length = 2000

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


#plt.ion()

#for i in range(10): pressure_inhale.put(-1)


fig = plt.figure()


ax = fig.add_subplot(111)

h1, = ax.plot([],[], "+-", label="buffer")
h2, = ax.plot([],[], "+-", label="inhale")
h3, = ax.plot([],[], "+-", label="Proportional")
h4, = ax.plot([],[], "+-", label="Integral")
h5, = ax.plot([],[], "+-", label="Derivative")

h6, = ax.plot([],[], "+-", label="Patient")
h7, = ax.plot([],[], "+-", label="DP_Patient")

h8, = ax.plot([],[], "+-", label="PID_error")

h9, = ax.plot([],[], "+-", label="inhale derivative")

h10, = ax.plot([],[], "+-", label="inhale derivative exp")
h11, = ax.plot([],[], "+-", label="inhale derivative threshold")
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

for _entry in _data:
    data = re.split(",", _entry)
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

#h1.set_xdata(np.array(range(history_length)))
#h1.set_ydata(list(pressure_buffer.queue))#list(pressure_inhale.queue))

h2.set_xdata(np.array(range(history_length)))
h2.set_ydata(list(pressure_inhale.queue))#list(pressure_buffer.queue))

#h3.set_xdata(np.array(range(history_length)))
#h3.set_ydata(list(PID_P.queue))#list(pressure_buffer.queue))
#
#h4.set_xdata(np.array(range(history_length)))
#h4.set_ydata(list(PID_I.queue))#list(pressure_buffer.queue))
#
h5.set_xdata(np.array(range(history_length)))
h5.set_ydata(np.array(list(PID_D.queue)))#list(pressure_buffer.queue))
#
#h6.set_xdata(np.array(range(history_length)))
#h6.set_ydata(list(pressure_patient.queue))#list(pressure_buffer.queue))
#
#h7.set_xdata(np.array(range(history_length)))
#h7.set_ydata(list(pressure_diff_patient.queue))#list(pressure_buffer.queue))
#
#h8.set_xdata(np.array(range(history_length)))
#h8.set_ydata(20.-np.array(list(pressure_inhale.queue)))#list(pressure_buffer.queue))

h9.set_xdata(np.array(range(history_length)))
h9.set_ydata(derivative(list(pressure_inhale.queue)))

h10.set_xdata(np.array(range(history_length)))
h10.set_ydata(derivative_exp(list(pressure_inhale.queue)))

h11.set_xdata(np.array(range(history_length)))
h11.set_ydata(derivative_withthreshold(list(pressure_inhale.queue), 2.0))


plt.legend()
#plt.ylim(-2,20)

ax.relim()
ax.autoscale_view(True,True,True)
#fig.canvas.draw()
#fig.canvas.flush_events()
plt.show()
#time.sleep(0.1)

logfile.seek(0)
logfile.close()
