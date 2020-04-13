#!/usr/bin/env python3
# data server to manage comms between UIs and LLI
#
# Author: Dónal Murray <donal.murray@cern.ch>

import asyncio
import json
import time
import threading
import argparse
import svpi
import commsControl
from commsConstants import payloadType
from collections import deque
from serial.tools import list_ports
from typing import List
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class HEVServer(object):
    def __init__(self, lli):
        self._alarms = []
        self._values = None
        self._dblock = threading.Lock()  # make db threadsafe
        self._lli = lli
        self._lli.bind_to(self.polling)

        self._broadcasting = True
        self._datavalid = None           # something has been received from arduino. placeholder for asyncio.Event()
        self._dvlock = threading.Lock()  # make datavalid threadsafe
        self._dvlock.acquire()           # come up locked to wait for loop
        # start worker thread to send values in background
        worker = threading.Thread(target=self.serve_all, daemon=True)
        worker.start()

    def __repr__(self):
        with self._dblock:
            return f"Alarms: {self._alarms}.\nSensor values: {self._values}"

    def polling(self, payload):
        # get values when we get a callback from commsControl (lli)
        logging.debug(f"Payload received: {payload!r}")
        # check if it is data or alarm
        payload_type = payload.getType()
        if payload_type == payloadType.payloadData:
            # pass data to db
            with self._dblock:
                self._values = payload.getDict()
        elif payload_type == payloadType.payloadAlarm:
            alarm_map = {
                0: "manual",
                1: "gas supply",
                2: "apnea",
                3: "expired minute volume",
                4: "upper pressure limit",
                5: "power failure",
            }
            new_alarm = payload.getDict()
            param = new_alarm["param"]
            if new_alarm["alarmCode"] == 2:
                # alarm stop, delete from list
                with self._dblock:
                    self._alarms.remove(alarm_map[param])

            elif new_alarm["alarmCode"] == 1:
                # alarm start, add to list
                with self._dblock:
                    self._alarms.append(alarm_map[param])

        # let broadcast thread know there is data to send
        with self._dvlock:
            self._datavalid.set()

        # pop from lli queue
        self._lli.pop_payloadrecv()
            
    async def handle_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        # listen for queries on the request socket
        data = await reader.read(300)
        request = json.loads(data.decode("utf-8"))
        addr = writer.get_extra_info("peername")
        logging.info(f"Answering request from {addr}")
        payload = ""

        # three possible queries: set mode, set thresholds or both
        if request["type"] == "setmode":
            mode = request["mode"]
            logging.debug(f"{addr!r} requested to change to mode {mode!r}")

            # send via protocol and prepare reply
            if self._lli.setMode(mode):
                packet = f"""{{"type": "ackmode", "mode": \"{mode}\"}}""".encode()
            else:
                packet = f"""{{"type": "nack"}}""".encode()
        elif request["type"] == "setthresholds":
            thresholds = request["thresholds"]
            logging.debug(
                f"{addr!r} requested to set thresholds to {thresholds!r}")

            # send via protocol
            payload = self._lli.setThresholds(thresholds)
            # prepare reply
            packet = f"""{{"type": "ackthresholds", "thresholds": \"{payload}\"}}""".encode()
        elif request["type"] == "setup":
            mode = request["mode"]
            thresholds = request["thresholds"]
            logging.debug(f"{addr!r} requested to change to mode {mode!r}")
            logging.debug(
                f"{addr!r} requested to set thresholds to {thresholds!r}")

            # send via protocol and prepare reply
            if self._lli.setMode(mode):
                self._lli.setThresholds(thresholds)
                packet = f"""{{"type": "ack", "mode": \"{mode}\", "thresholds": \"{thresholds}\"}}""".encode()
            else:
                packet = f"""{{"type": "nack"}}""".encode()

        # send reply and close connection
        writer.write(packet)
        await writer.drain()
        writer.close()

    async def handle_broadcast(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        # log address
        addr = writer.get_extra_info("peername")
        logging.info(f"Broadcasting to {addr!r}")

        while self._broadcasting:
            # wait for data from serial port
            try:
                await asyncio.wait_for(self._datavalid.wait(), timeout=0.5) # set timeout such that there is never pileup
            except asyncio.TimeoutError:
                continue
            # take lock of db and prepare packet
            with self._dblock:
                values: List[float] = self._values
                alarms = self._alarms if len(self._alarms) > 0 else None

            broadcast_packet = {}
            broadcast_packet["sensors"] = values
            broadcast_packet["alarms"] = alarms # add alarms key/value pair

            logging.info(f"Send: {json.dumps(broadcast_packet,indent=4)}")

            try:
                writer.write(json.dumps(broadcast_packet).encode())
                await writer.drain()
            except (ConnectionResetError, BrokenPipeError):
                # Connection lost, stop trying to broadcast and free up socket
                logging.warning(f"Connection lost with {addr!r}")
                self._broadcasting = False
            # take control of datavalid and reset it
            with self._dvlock:
                self._datavalid.clear()

        self._broadcasting = True
        writer.close()

    async def serve_request(self, ip: str, port: int) -> None:
        server = await asyncio.start_server(
            self.handle_request, ip, port)

        # get address for log
        addr = server.sockets[0].getsockname()
        logging.info(f"Listening for requests on {addr}")

        async with server:
            await server.serve_forever()

    async def serve_broadcast(self, ip: str, port: int) -> None:
        server = await asyncio.start_server(
            self.handle_broadcast, ip, port)

        # get address for log
        addr = server.sockets[0].getsockname()
        logging.info(f"Serving on {addr}")

        async with server:
            await server.serve_forever()

    async def create_sockets(self) -> None:
        self._datavalid = asyncio.Event() # initially false
        self._dvlock.release()
        LOCALHOST = "127.0.0.1"
        b1 = self.serve_broadcast(LOCALHOST, 54320)  # WebUI broadcast
        r1 = self.serve_request(LOCALHOST, 54321)    # joint request socket
        #b2 = self.serve_broadcast(LOCALHOST, 54322)  # NativeUI broadcast
        #tasks = [b1, r1, b2]
        tasks = [b1, r1]
        await asyncio.gather(*tasks, return_exceptions=True)

    def serve_all(self) -> None:
        asyncio.run(self.create_sockets())


if __name__ == "__main__":
    #parser to allow us to pass arguments to hevserver
    parser = argparse.ArgumentParser(description='Arguments to run hevserver')
    parser.add_argument('--inputFile', type=str, default = '', help='a test file to load data')
    args = parser.parse_args()
    
    # check if input file was specified
    if args.inputFile != '':
        # initialise frond end generator from file
        lli = svpi.svpi(args.inputFile)
    else:
        # get arduino serial port
        for port in list_ports.comports():
            if port.manufacturer and "ARDUINO" in port.manufacturer.upper():
                port_device = port.device 

        # initialise low level interface
        try:
            lli = commsControl.commsControl(port=port_device)
        except NameError:
            print("Arduino not connected")
            exit(1)

    hevsrv = HEVServer(lli)

    # serve forever
    while True:
        pass
