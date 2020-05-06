#!/usr/bin/env python3

# simple txt filereader frontend for HEVserver
# currently dedicated to very specific file format matching victor's sample.txt
# author Dónal Murray <donal.murray@cern.ch>

import threading
import CommsCommon
import time
import numpy as np
from typing import List
from collections import deque
import logging
import os.path
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class hevfromtxt():
    def __init__(self):
        # use input file for testing
        h = np.loadtxt(os.path.dirname(__file__)+"/share/sample.txt",skiprows = 1, delimiter = ',')
        h2 = np.loadtxt(os.path.dirname(__file__)+"/share/testdummy.txt",skiprows = 23, delimiter = '\t')
        # share/sample.txt - take values to be plotted
        self._timestamp = h[:,0].tolist()
        self._airway_pressure = h[:,1].tolist()
        self._flow = h[:,2].tolist()
        self._volume = h[:,3].tolist()
        # share/testdummy.txt
        # X_Value P_Regulated_O2  P_Regulated_Air P_Buffer        P_inhale
        # PEEP    Flow    PID output      Flow no-scaled  FSMSateID
        # Air valve open  O2 valve open   P_patient
        self._full = True
        self._pressure_o2_regulated = h2[:,1].tolist() # P_Regulated_O2
        self._pressure_air_regulated = h2[:,2].tolist() # P_Regulated_Air
        self._pressure_buffer = h2[:,3].tolist() # P_Buffer
        self._pressure_inhale = h2[:,4].tolist() # P_inhale
        self._peep = h2[:,5].tolist() # PEEP
        #self._flow = h2[:,6].tolist() # Flow - take from sample.txt instead
        self._pid_output = h2[:,7].tolist() # PID output?
        self._pressure_diff_patient = h2[:,8].tolist() # Flow no-scaled
        self._fsm_state = h2[:,9].tolist() # FSMSateID [sic]
        self._valve_air_in = h2[:,10].tolist() # Air valve open?
        self._valve_o2_in = h2[:,11].tolist() # O2 valve open?
        self._pressure_patient = h2[:,12].tolist() # P_patient

        # keep track of position within sample file
        self._length = len(self._timestamp)
        self._pos = 0
        # position within testdummy file - only about a fifth of the size
        self._length2 = len(self._pressure_o2_regulated)
        self._pos2 = 0
        self._increment = 1

        # received queue and observers to be notified on update
        self._payloadrecv = deque(maxlen = 16)
        self._observers = []
        sendingWorker = threading.Thread(target=self.generate, daemon=True)
        sendingWorker.start()
        
    def generate(self) -> None:
        time_offset = 0
        while True:
            data = CommsCommon.DataFormat()
            readback = CommsCommon.ReadbackFormat()

            data.timestamp       = int(time_offset + self._timestamp[self._pos] * 1000)
            readback.timestamp   = int(time_offset + self._timestamp[self._pos] * 1000)
            data.airway_pressure = self._airway_pressure[self._pos]
            data.volume          = self._volume[self._pos]
            data.flow            = self._flow[self._pos]

            # add the other values from the testdummy file
            data.pressure_o2_regulated  = self._pressure_o2_regulated[self._pos2]
            data.pressure_air_regulated = self._pressure_air_regulated[self._pos2]
            data.pressure_buffer        = self._pressure_buffer[self._pos2]
            data.pressure_inhale        = self._pressure_inhale[self._pos2]
            data.pressure_diff_patient  = self._pressure_diff_patient[self._pos2]
            data.fsm_state              = int(self._fsm_state[self._pos2])
            data.pressure_patient       = self._pressure_patient[self._pos2]
            readback.peep               = int(self._peep[self._pos2])
            readback.valve_air_in       = self._valve_air_in[self._pos2]
            readback.valve_o2_in        = self._valve_o2_in[self._pos2]

            if self._pos + self._increment < self._length:
                delay = self._timestamp[self._pos+self._increment] - self._timestamp[self._pos]
                self._pos = self._pos + self._increment
            else:
                delay = self._timestamp[self._pos] - self._timestamp[self._pos-self._increment]
                time_offset += (self._timestamp[self._pos] - self._timestamp[0]) * 1000
                self._pos = 0
            
            if self._pos2 + self._increment < self._length2:
                self._pos2 += 1
            else:
                self._pos2 = 0

            self.payloadrecv = data
            time.sleep(delay / 2)
            self.payloadrecv = readback
            time.sleep(delay / 2)

    # callback to dependants to read the received payload
    @property
    def payloadrecv(self):
        return self._payloadrecv

    @payloadrecv.setter
    def payloadrecv(self, payload):
        for callback in self._observers:
            callback(payload)

    def writePayload(self, payload):
        logging.info(f"CMD received: {payload}")

    def bind_to(self, callback):
        self._observers.append(callback)
