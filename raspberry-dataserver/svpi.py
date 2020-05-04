#!/usr/bin/env python3

# Front end generator for HEV raspberry pi data server
# author Dónal Murray <donal.murray@cern.ch>

import time
import numpy as np
import argparse
from collections import deque
import CommsFormat
import threading
import CommsCommon
from CommsCommon import ALARM_CODES
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
        # received queue and observers to be notified on update
        self._payloadrecv = deque(maxlen = 16)
        self._observers = []
        self._delay = 1
        sendingWorker = threading.Thread(target=self.generate, daemon=True)
        sendingWorker.start()
        
    def generate(self) -> None:
        while True:
            # check for an alarm
            alarm = self.getAlarms()
            if alarm is not None:
                byteArray = alarm
            else:
                # grab next array from filedump
                fullArray = self._bytestore[0+self._pos*27:27+self._pos*27]
                # currently (20200426) the byte dump has the wrong format of 27 bytes, expects 41. snip out second byte and add four more bytes for zeroed timestamp
                byteArray = b'\xa3' + fullArray[-1-3:] + bytearray((0x01,0x01)) + fullArray[2:] + fullArray[-1-20:]
                # go to next byte array. if at the end, loop
                self._pos = self._pos + 1 if self._pos < 99 else 0
            
            payload = CommsCommon.PayloadFormat.fromByteArray(byteArray)
            self.payloadrecv = payload

            time.sleep(self._delay)

    def getAlarms(self) -> List[str]:
        # give/cancel a random alarm a twentieth of the time
        if np.random.randint(0, 20) == 0:
            # send alarm
            alarm = 1 + np.random.randint(0, len(ALARM_CODES))
            # give all simulated alarms low priority for the minute
            return bytearray((0xA3,0x00,0x00,0x00,0x00,0x06,0x01,alarm,0x00,0x00,0x00,0x00))
        return None

    # callback to dependants to read the received payload
    @property
    def payloadrecv(self):
        return self._payloadrecv

    @payloadrecv.setter
    def payloadrecv(self, payload):
        for callback in self._observers:
            callback(payload)

    def writePayload(self, payload):
        logging.info(payload)

    def bind_to(self, callback):
        self._observers.append(callback)

if __name__ == "__main__":
    #parser to allow us to pass arguments to hevserver
    parser = argparse.ArgumentParser(description='Arguments to run hevserver')
    parser.add_argument('--inputFile', type=str, default = '', help='a test file to load data')
    args = parser.parse_args()

    generator = svpi(args.inputFile)
    while True:
        time.sleep(60)
