#!/usr/bin/env python3

# simple txt filereader frontend for HEVserver
# currently dedicated to very specific file format matching victor's sample.txt
# author Dónal Murray <donal.murray@cern.ch>

import threading
import commsConstants
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
        h = np.loadtxt(inputFile,skiprows = 1, delimiter = ',')
        self._pressure = h[:,1].tolist()
        self._flow = h[:,2].tolist()
        self._volume = h[:,3].tolist()
        self._length = len(self._pressure)
        self._pos = 0 # position within sample
        self._delay = 0.2 # time period

        # received queue and observers to be notified on update
        self._payloadrecv = deque(maxlen = 16)
        self._observers = []
        sendingWorker = threading.Thread(target=self.generate, daemon=True)
        sendingWorker.start()
        
    def generate(self) -> None:
        while True:
            # grab next array from filedump
            increment = int(round(self._delay / 0.2))
            increment = 1 if increment < 1 else increment
            self._pos = self._pos + increment if self._pos + increment < self._length else 0
            payload = commsConstants.dataFormat()
            
            # directly setting private member variables in this edge case
            payload._version = payload._RPI_VERSION
            payload._pressure_buffer = self._pressure[self._pos]
            payload._pressure_inhale = self._volume[self._pos]
            payload._temperature_buffer = self._flow[self._pos]

            self.payloadrecv = payload
            time.sleep(self._delay)

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
        logging.info(payload)

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