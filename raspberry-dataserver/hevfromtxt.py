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
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class hevfromtxt():
    def __init__(self, inputFile):
        # use input file for testing
        self._full = False
        try:
            h = np.loadtxt(inputFile,skiprows = 1, delimiter = ',')
            self._airway_pressure = h[:,1].tolist()
            self._flow = h[:,2].tolist()
            self._volume = h[:,3].tolist()
        except ValueError:
            # X_Value P_Regulated_O2  P_Regulated_Air P_Buffer        P_inhale
            # PEEP    Flow    PID output      Flow no-scaled  FSMSateID
            # Air valve open  O2 valve open   P_patient
            h = np.loadtxt(inputFile,skiprows = 23, delimiter = '\t')
            self._full = True
            self._pressure_o2_regulated = h[:,1].tolist() # P_Regulated_O2
            self._pressure_air_regulated = h[:,2].tolist() # P_Regulated_Air
            self._pressure_buffer = h[:,3].tolist() # P_Buffer
            self._pressure_inhale = h[:,4].tolist() # P_inhale
            self._peep = h[:,5].tolist() # PEEP
            self._flow = h[:,6].tolist() # Flow
            self._TODO = h[:,7].tolist() # PID output?
            self._pressure_diff_patient = h[:,8].tolist() # Flow no-scaled
            self._fsm_state = h[:,9].tolist() # FSMSateID [sic]
            self._valve_air_in = h[:,10].tolist() # Air valve open?
            self._valve_o2_in = h[:,11].tolist() # O2 valve open?
            self._pressure_patient = h[:,12].tolist() # P_patient

        self._timestamp = h[:,0].tolist()

        self._length = len(self._timestamp)
        self._pos = 0 # position within sample
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

            data.timestamp     = int(time_offset + self._timestamp[self._pos] * 1000)
            readback.timestamp = int(time_offset + self._timestamp[self._pos] * 1000)

            if self._full:
                data.pressure_o2_regulated  = self._pressure_o2_regulated[self._pos]
                data.pressure_air_regulated = self._pressure_air_regulated[self._pos]
                data.pressure_buffer        = self._pressure_buffer[self._pos]
                data.pressure_inhale        = self._pressure_inhale[self._pos]
                data.flow                   = self._flow[self._pos]
                data.volume                 = self._TODO[self._pos] # FIXME
                data.pressure_diff_patient  = self._pressure_diff_patient[self._pos]
                data.fsm_state              = int(self._fsm_state[self._pos])
                data.pressure_patient       = self._pressure_patient[self._pos]
                readback.peep               = int(self._peep[self._pos])
                readback.valve_air_in       = self._valve_air_in[self._pos]
                readback.valve_o2_in        = self._valve_o2_in[self._pos]
            else:
                data.airway_pressure = self._airway_pressure[self._pos]
                data.volume = self._volume[self._pos]
                data.flow = self._flow[self._pos]

            if self._pos + self._increment < self._length:
                delay = self._timestamp[self._pos+self._increment] - self._timestamp[self._pos]
                self._pos = self._pos + self._increment
            else:
                delay = self._timestamp[self._pos] - self._timestamp[self._pos-self._increment]
                time_offset += (self._timestamp[self._pos] - self._timestamp[0]) * 1000
                self._pos = 0

            if self._full:
                self.payloadrecv = data
                time.sleep(delay / 2)
                self.payloadrecv = readback
                time.sleep(delay / 2)
            else:
                self.payloadrecv = data
                time.sleep(delay)

    # callback to dependants to read the received payload
    @property
    def payloadrecv(self):
        return self._payloadrecv

    @payloadrecv.setter
    def payloadrecv(self, payload):
        self._payloadrecv.append(payload)
        logging.debug(f"Pushed {payload} to FIFO")
        for callback in self._observers:
            # peek at the leftmost item, don't pop until receipt confirmed
            callback(self._payloadrecv[0])

    def writePayload(self, payload):
        logging.info(f"CMD received: {payload}")

    def bind_to(self, callback):
        self._observers.append(callback)

    def pop_payloadrecv(self):
        # from callback. confirmed receipt, pop value
        poppedval = self._payloadrecv.popleft()
        logging.debug(f"Popped {poppedval} from FIFO")
        if len(self._payloadrecv) > 0:
            # purge full queue if Dependant goes down when it comes back up
            for callback in self._observers:
                callback(self._payloadrecv[0])
