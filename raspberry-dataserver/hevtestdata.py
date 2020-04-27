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
        self.current_timestamp = int(time.time() * 1000)
        sendingWorker = threading.Thread(target=self.generate, daemon=True)
        sendingWorker.start()

    @property
    def current_timestamp(self):
        return self._current_timestamp

    @current_timestamp.setter
    def current_timestamp(self, timestamp):
        self._current_timestamp = timestamp

    def generate(self) -> None:
        logging.critical("Running tests with unstable step intervals for 10 seconds")
        self.current_timestamp = 0
        self._send_message(self.current_timestamp)
        time.sleep(2)
        while self.current_timestamp < 5_000 or self.current_timestamp > 2**30:
            interval = random.randint(-20, 50)
            self._send_message(self.current_timestamp + interval)
            if interval > 0:
                self.current_timestamp += interval
                time.sleep(interval / 1_000)

        logging.critical("Running tests with large jumps forward in time")
        time.sleep(2)
        for interval in [1_000, 10_000, 100_000, 1_000_000]:
            self.current_timestamp += interval
            self._send_message(self.current_timestamp)
            time.sleep(2)

        logging.critical("Running tests for overflow with stable steps for 10 seconds")
        time.sleep(2)
        self.current_timestamp = 2**32 - 5_000
        self._send_message(self.current_timestamp)
        interval = 50
        for i in range(0, 10_000, interval):
            self.current_timestamp += interval
            self._send_message(self.current_timestamp)
            time.sleep(interval / 1_000)

        logging.critical("Running tests with device being reset 10 times with 2 seconds of unstable running inbetween")
        time.sleep(2)
        for i in range(10):
            self.current_timestamp = 0
            self._send_message(self.current_timestamp)
            while self.current_timestamp < 2_000:
                interval = random.randint(-20, 50)
                self._send_message(self.current_timestamp + interval)
                if interval > 0:
                    self.current_timestamp += interval
                    time.sleep(interval / 1_000)

        logging.critical("Running tests for overflow with unstable steps for 10 seconds")
        time.sleep(2)
        self.current_timestamp = 2**32 - 5_000
        self._send_message(self.current_timestamp)
        while self.current_timestamp < 2**32 + 5_000:
            interval = random.randint(-100, 50)
            self._send_message(self.current_timestamp + interval)
            if interval > 0:
                self.current_timestamp += interval
                time.sleep(interval / 1_000)

        logging.critical("Looping forever at a high rate")
        time.sleep(2)
        current_tick = 0
        while True:
            interval = 1
            self._send_message(self.current_timestamp + current_tick * interval)
            time.sleep(interval / 1000)
            current_tick += 1

    def _send_message(self, timestamp):
        # directly setting private member variables in this edge case
        payload = CommsCommon.DataFormat()
        payload._version = payload._RPI_VERSION
        payload._timestamp = timestamp % 2**32
        payload._fsm_state = "IDLE"
        payload._pressure_air_supply = abs(math.sin((timestamp/1000) * (math.pi)))* 0
        payload._pressure_air_regulated = abs(math.sin((timestamp/1000) * (math.pi))) * 0
        payload._pressure_o2_supply = abs(math.sin((0.5 + timestamp/1000) * (math.pi))) * 657
        payload._pressure_o2_regulated = abs(math.sin((1.0 + timestamp/1000) * (math.pi))) * 653
        payload._pressure_buffer = abs(math.sin((1.5 + timestamp/1000) * (math.pi))) * 496
        payload._pressure_inhale = abs(math.sin((2.0 + timestamp/1000) * (math.pi))) * 481
        payload._pressure_patient = abs(math.sin((2.5 + timestamp/1000) * (math.pi))) * 772
        payload._temperature_buffer = math.sin((3.0 + timestamp/1000) * (math.pi)) * 1000
        payload._pressure_diff_patient = abs(math.sin((3.5 + timestamp/1000) * (math.pi))) * 61
        payload._readback_valve_air_in = abs(math.sin((timestamp/1000) * (math.pi))) * 0
        payload._readback_valve_o2_in = abs(math.sin((timestamp/1000) * (math.pi))) * 0
        payload._readback_valve_inhale = abs(math.sin((timestamp/1000) * (math.pi))) * 0
        payload._readback_valve_exhale = abs(math.sin((timestamp/1000) * (math.pi))) * 0
        payload._readback_valve_purge = abs(math.sin((timestamp/1000) * (math.pi))) * 0
        payload._readback_mode = abs(math.sin((timestamp/1000) * (math.pi))) * 0
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
