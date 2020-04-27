#!/usr/bin/env python3

# simple txt filereader frontend for HEVserver
# currently dedicated to very specific file format matching victor's sample.txt
# author Dónal Murray <donal.murray@cern.ch>
import math
import random
import time
import threading
import CommsCommon
import time
import numpy as np
from typing import List
from collections import deque
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class HEVTestData:
    def __init__(self):
        # received queue and observers to be notified on update
        self._payloadrecv = deque(maxlen = 16)
        self._observers = []
        sendingWorker = threading.Thread(target=self.generate, daemon=True)
        sendingWorker.start()
        
    def generate(self) -> None:
        current_timestamp = int(time.time() * 1000) % 2**30

        logging.info("Running tests with unstable step intervals for 10 seconds")
        for i in range(100):
            current_timestamp += random.randint(-20, 100)
            self._send_message(current_timestamp)
            time.sleep(0.1)
        
        logging.info("Running tests with large jumps forward in time")
        for interval in [1_000, 10_000, 100_000, 1_000_000]:
            current_timestamp += interval
            self._send_message(current_timestamp)
            time.sleep(2)

        logging.info("Looping forever at a high rate")
        current_tick = 0
        while True:
            interval = 1
            self._send_message(current_timestamp + current_tick * interval)
            time.sleep(interval / 1000)
            current_tick += 1

    def _send_message(self, timestamp):
        # directly setting private member variables in this edge case
        payload = CommsCommon.DataFormat()
        payload._version = payload._RPI_VERSION
        payload._timestamp = timestamp
        payload._fsm_state = "IDLE"
        payload._pressure_air_supply = abs(math.sin((payload._timestamp/1000) * (math.pi)))* 0
        payload._pressure_air_regulated = abs(math.sin((payload._timestamp/1000) * (math.pi))) * 0
        payload._pressure_o2_supply = abs(math.sin((0.5 + payload._timestamp/1000) * (math.pi))) * 657
        payload._pressure_o2_regulated = abs(math.sin((1.0 + payload._timestamp/1000) * (math.pi))) * 653
        payload._pressure_buffer = abs(math.sin((1.5 + payload._timestamp/1000) * (math.pi))) * 496
        payload._pressure_inhale = abs(math.sin((2.0 + payload._timestamp/1000) * (math.pi))) * 481
        payload._pressure_patient = abs(math.sin((2.5 + payload._timestamp/1000) * (math.pi))) * 772
        payload._temperature_buffer = math.sin((3.0 + payload._timestamp/1000) * (math.pi)) * 1000
        payload._pressure_diff_patient = abs(math.sin((3.5 + payload._timestamp/1000) * (math.pi))) * 61
        payload._readback_valve_air_in = abs(math.sin((payload._timestamp/1000) * (math.pi))) * 0
        payload._readback_valve_o2_in = abs(math.sin((payload._timestamp/1000) * (math.pi))) * 0
        payload._readback_valve_inhale = abs(math.sin((payload._timestamp/1000) * (math.pi))) * 0
        payload._readback_valve_exhale = abs(math.sin((payload._timestamp/1000) * (math.pi))) * 0
        payload._readback_valve_purge = abs(math.sin((payload._timestamp/1000) * (math.pi))) * 0
        payload._readback_mode = abs(math.sin((payload._timestamp/1000) * (math.pi))) * 0
        self.payloadrecv = payload

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
