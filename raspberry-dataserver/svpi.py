#!/usr/bin/env python3

# Front end generator for HEV raspberry pi data server
# author Dónal Murray <donal.murray@cern.ch>

import time
import numpy as np
import argparse
from collections import deque
import commsFormat
import threading
import commsConstants
from typing import List, Dict
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class svpi():
    def __init__(self, inputFile):
        # use input file for testing
        self._input = open(inputFile, 'rb')
        # dump file to variable
        self._bytestore = bytearray(self._input.read())
        self._pos = 0 # position inside bytestore
        self._currentAlarm = None
        # received queue and observers to be notified on update
        self._payloadrecv = deque(maxlen = 16)
        self._observers = []
        sendingWorker = threading.Thread(target=self.generate, daemon=True)
        sendingWorker.start()
        
    def generate(self) -> None:
        while True:
            # check for an alarm
            alarm = self.getAlarms()
            if alarm is not None:
                byteArray = alarm
                payload = commsConstants.alarmFormat()
            else:
                # grab next array from filedump
                fullArray = self._bytestore[0+self._pos*27:27+self._pos*27]
                # current byte dump (20200411) has wrong format 27 bytes, new format expects 26. snip out second byte
                byteArray = fullArray[:1] + fullArray[2:]
                # go to next byte array. if at the end, loop
                self._pos = self._pos + 1 if self._pos < 99 else 0
                payload = commsConstants.dataFormat()
            
            payload.fromByteArray(byteArray)
            self.payloadrecv = payload
            time.sleep(1)

    def getAlarms(self) -> List[str]:
        # give/cancel a random alarm a twentieth of the time
        #alarms = {
        #    0: "manual",
        #    1: "gas supply",
        #    2: "apnea",
        #    3: "expired minute volume",
        #    4: "upper pressure limit",
        #    5: "power failure",
        #}
        if np.random.randint(0, 20) == 0:
            if self._currentAlarm is None:
                # send alarm
                alarm = np.random.randint(0, 6)
                self._currentAlarm = alarm
                return bytearray((0xA0,0x01,alarm,0x00,0x00,0x00))
            else:
                # stop previous alarm
                alarm = self._currentAlarm
                self._currentAlarm = None
                return bytearray((0xA0,0x02,alarm,0x00,0x00,0x00))
        return None

    def getThresholds(self) -> List[float]:
        # All thresholds 32 bit floats
        thresholds: List[float] = np.random.uniform(0.0, 1000.0, 3).tolist()
        return thresholds

    def setMode(self, mode: str) -> bool:
        # setting a mode - just print it
        if mode in ("PRVC", "SIMV-PC", "CPAP"):
            logging.info(f"Setting mode {mode}")
            return True
        else:
            logging.error(f"Requested mode {mode} does not exist")
            return False

    def setThresholds(self, thresholds: List[float]) -> str:
        # setting thresholds - just print them
        logging.info(f"Setting thresholds {thresholds}")
        return thresholds

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


if __name__ == "__main__":
    #parser to allow us to pass arguments to hevserver
    parser = argparse.ArgumentParser(description='Arguments to run hevserver')
    parser.add_argument('--inputFile', type=str, default = '', help='a test file to load data')
    args = parser.parse_args()

    generator = svpi(args.inputFile)
    while True:
        pass
