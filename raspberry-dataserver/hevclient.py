#!/usr/bin/env python3
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


# client side for the data server to manage comms between UIs and LLI
#
# Author: Dónal Murray <donal.murray@cern.ch>

import asyncio
import time
import json
import threading
from typing import List, Dict, Union
from CommsCommon import PayloadFormat, PAYLOAD_TYPE
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# use /dev/shm (in memory tmpfs) to hold the data, should be stable over Flask shenanigans when restaring scripts
import mmap
import pickle
import os

mmFileName = "/dev/shm/HEVClient_lastData.mmap"


class HEVPacketError(Exception):
    pass


class HEVClient(object):
    def __init__(self, polling=True):
        super(HEVClient, self).__init__()
        self._alarms = []  # db for alarms
        self._personal = None  # db for personal data
        self._fastdata = None  # db for sensor values
        self._readback = None  # db for sensor values
        self._cycle = None  # db for sensor values
        self._target = None  # db for sensor values
        self._logmsg = None  # db for sensor values
        self._thresholds = None  # db for sensor values
        self._thresholds = []  # db for threshold settings
        self._polling = polling  # keep reading data into db
        self._lock = threading.Lock()  # lock for the database

        self._mmFile = None
        if os.access(mmFileName, os.F_OK):
            self._mmFile = open(mmFileName, "a+b")
        else:
            self._mmFile = open(mmFileName, "x+b")
            self._mmFile.write(b"0" * 10000)  # ~10kb is enough I hope for one event
        self._mmMap = mmap.mmap(self._mmFile.fileno(), 0)  # Map to in memory object
        self._mmMap.seek(0)
        self._mmMap.write(
            pickle.dumps("Data not yet set")
        )  # ensure no old or unset data in file
        self._mmMap.flush()

        # start polling in another thread unless told otherwise
        if self._polling:
            self.start_polling()

    def __del__(self):
        self._mmMap.close()
        self._mmFile.close()

    def start_polling(self):
        """start worker thread to update db in the background"""
        worker = threading.Thread(target=self.start_client, daemon=True)
        worker.start()

    def start_client(self) -> None:
        asyncio.run(self.polling())

    async def polling(self) -> None:
        """open persistent connection with server"""
        while True:
            try:
                reader, writer = await asyncio.open_connection("127.0.0.1", 54320)

                # grab data from the socket as soon as it is available and dump it in the db
                while self._polling:
                    try:
                        data = await reader.readuntil(separator=b"\0")
                        data = data[:-1]  # snip off nullbyte
                        payload = json.loads(data.decode("utf-8"))
                        if payload["type"] == "keepalive":
                            # Still alive
                            continue
                        elif payload["type"] == "DATA":
                            with self._lock:
                                self._fastdata = payload["DATA"]
                                self._mmMap.seek(0)
                                self._mmMap.write(pickle.dumps(self._fastdata))
                                self._mmMap.flush()
                        elif payload["type"] == "READBACK":
                            with self._lock:
                                self._readback = payload["READBACK"]
                        elif payload["type"] == "CYCLE":
                            with self._lock:
                                self._cycle = payload["CYCLE"]
                        elif payload["type"] == "TARGET":
                            with self._lock:
                                self._target = payload["TARGET"]
                        elif payload["type"] == "PERSONAL":
                            with self._lock:
                                self._personal = payload["PERSONAL"]
                        elif payload["type"] == "LOGMSG":
                            with self._lock:
                                self._logmsg = payload["LOGMSG"]
                        elif payload["type"] == "THRESHOLDS":
                            with self._lock:
                                self._thresholds = payload["THRESHOLDS"]
                        elif payload["type"] == "ALARM":
                            with self._lock:
                                self._alarms = payload["ALARM"]
                        elif payload["type"] in [pt.name for pt in PAYLOAD_TYPE]:
                            # payload type is a valid payload type
                            pass
                        else:
                            raise HEVPacketError("Invalid broadcast type")

                        self._alarms = payload["alarms"]
                        # self._personal = payload["personal"]
                        self.get_updates(payload)  # callback function to be overridden
                    except json.decoder.JSONDecodeError:
                        logging.warning(f"Could not decode packet: {data}")
                    except KeyError:
                        raise

                # close connection
                writer.close()
                await writer.wait_closed()
            except ConnectionRefusedError as e:
                logging.error(str(e) + " - is the microcontroller running?")
                await asyncio.sleep(2)
            except Exception as e:
                # warn and reopen connection
                logging.error(e)
                await asyncio.sleep(2)

    def get_updates(self, payload) -> None:
        """Overrideable function called after receiving data from the socket, with that data as an argument"""
        pass

    async def send_request(
        self,
        reqtype,
        cmdtype: str = None,
        cmd: str = None,
        param: str = None,
        alarm: str = None,
        personal: str = None,
    ) -> bool:
        # open connection and send packet
        reader, writer = await asyncio.open_connection("127.0.0.1", 54321)
        payload = {"type": reqtype}
        if reqtype == "CMD":
            payload["cmdtype"] = cmdtype
            payload["cmd"] = cmd
            payload["param"] = param
        elif reqtype == "ALARM":
            payload["alarm_type"] = alarm["alarm_type"]
            payload["alarm_code"] = alarm["alarm_code"]
            payload["param"] = param
        elif reqtype == "PERSONAL":
            payload["name"] = personal["name"]
            payload["age"] = int(personal["age"])
            payload["sex"] = personal["sex"]
            payload["height"] = int(personal["height"])
            payload["weight"] = int(personal["weight"])
        else:
            raise HEVPacketError("Invalid packet type")

        logging.info(payload)
        packet = json.dumps(payload).encode() + b"\0"

        writer.write(packet)
        await writer.drain()

        # wait for acknowledge
        data = await reader.readuntil(separator=b"\0")
        data = data[:-1]
        try:
            data = json.loads(data.decode("utf-8"))
        except json.decoder.JSONDecodeError:
            logging.warning(f"Could not decode packet: {data}")

        # close connection to free up socket
        writer.close()
        await writer.wait_closed()

        # check that acknowledge is meaningful
        if data["type"] == "ack":
            logging.info(f"Request type {reqtype} sent successfully")
            return True
        else:
            logging.warning(f"Request type {reqtype} failed")
            return False

    def send_cmd(self, cmdtype: str, cmd: str, param: Union[float, int] = None) -> bool:
        # send a cmd and wait to see if it's valid
        # print(cmdtype, cmd, param)
        try:
            return asyncio.run(
                self.send_request("CMD", cmdtype=cmdtype, cmd=cmd, param=param)
            )
        except ConnectionRefusedError as error:
            logging.error(str(error) + " - is the microcontroller running?")

    def ack_alarm(self, alarm: str) -> bool:
        # acknowledge alarm to remove it from the hevserver list
        return asyncio.run(self.send_request("ALARM", alarm=alarm))

    # def send_personal(self, personal: Dict[str, str]=None ) -> bool:
    def send_personal(self, personal: str) -> bool:
        # acknowledge alarm to remove it from the hevserver list
        return asyncio.run(self.send_request("PERSONAL", personal=personal))

    def get_values(self) -> Dict:
        # get sensor values from db
        self._mmFile.seek(0)
        try:
            fastdata = pickle.load(self._mmFile)
        except pickle.UnpicklingError as e:
            logging.warning(f"Unpicking error {e}")
            return None
        if type(fastdata) is dict:
            return fastdata
        else:
            logging.warning("Missing fastdata")
            return None

    def get_readback(self) -> Dict:
        # get readback from db
        return self._readback

    def get_cycle(self) -> Dict:
        # get cycle data from db
        return self._cycle

    def get_personal(self) -> Dict:
        # get personal data from db
        return self._personal

    def get_logmsg(self) -> Dict:
        # get logmsg data from db
        return self._logmsg

    def get_target(self) -> Dict:
        # get target data from db
        return self._target

    def get_thresholds(self) -> Dict:
        # get threshold data from db
        return self._thresholds

    def get_alarms(self) -> List[str]:
        # get alarms from db
        return self._alarms


if __name__ == "__main__":
    # example implementation
    # just import hevclient and do something like the following
    hevclient = HEVClient()

    time.sleep(2)
    print(hevclient.send_cmd("GENERAL", "START"))
    # Play with sensor values and alarms
    for i in range(20):
        values = hevclient.get_values()  # returns a dict or None
        alarms = hevclient.get_alarms()  # returns a list of alarms currently ongoing
        print(values)
        if values is None:
            i = i + 1 if i > 0 else 0
        else:
            print(f"Values: {json.dumps(values, indent=4)}")
            print(f"Alarms: {alarms}")
        time.sleep(1)

    # acknowledge the oldest alarm
    try:
        hevclient.ack_alarm(alarms[0])  # blindly assume we have one after 40s
    except:
        logging.info("No alarms received")

    time.sleep(2)
    print(f"Alarms: {hevclient.get_alarms()}")

    # set a timeout
    hevclient.send_cmd("SET_DURATION", "INHALE", 1111)

    # check for the readback
    for i in range(10):
        print(f"Readback: {json.dumps(hevclient.get_readback(), indent=4)}")
        print(f"Alarms: {hevclient.get_alarms()}")
        time.sleep(1)

    print(hevclient.send_cmd("GENERAL", "STOP"))
