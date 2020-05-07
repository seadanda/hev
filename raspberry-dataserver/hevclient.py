#!/usr/bin/env python3
# client side for the data server to manage comms between UIs and LLI
#
# Author: Dónal Murray <donal.murray@cern.ch>

import asyncio
import time
import json
import threading
from typing import List, Dict, Union
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

polling = True
setflag = False

class HEVPacketError(Exception):
    pass

class HEVClient(object):
    def __init__(self):
        self._alarms = []  # db for alarms
        self._fastdata = None  # db for sensor values
        self._readback = None  # db for sensor values
        self._cycle = None  # db for sensor values
        self._thresholds = None  # db for sensor values
        self._thresholds = []  # db for threshold settings
        self._polling = True  # keep reading data into db
        self._lock = threading.Lock()  # lock for the database

        # start worker thread to update db in the background
        worker = threading.Thread(target=self.start_client, daemon=True)
        worker.start()

    async def polling(self) -> None:
        # open persistent connection with server
        reader, writer = await asyncio.open_connection("127.0.0.1", 54320)

        # grab data from the socket as soon as it is available and dump it in the db
        while self._polling:
            try:
                data = await reader.readuntil(separator=b'\0')
                data = data[:-1] # snip off nullbyte
                payload = json.loads(data.decode("utf-8"))
                if payload["type"] == "keepalive":
                    #Still alive
                    continue
                elif payload["type"] == "DATA":
                    with self._lock:
                        self._fastdata = payload["DATA"]
                elif payload["type"] == "READBACK":
                    with self._lock:
                        self._readback = payload["READBACK"]
                elif payload["type"] == "CYCLE":
                    with self._lock:
                        self._cycle = payload["CYCLE"]
                elif payload["type"] == "THRESHOLDS":
                    with self._lock:
                        self._thresholds = payload["THRESHOLDS"]
                else:
                    raise HEVPacketError("Invalid broadcast type")

                self._alarms = payload["alarms"]
            except json.decoder.JSONDecodeError:
                logging.warning(f"Could not decode packet: {data}")
            except KeyError:
                raise

        # close connection
        writer.close()
        await writer.wait_closed()

    def start_client(self) -> None:
        asyncio.run(self.polling())

    async def send_request(self, reqtype, cmdtype:str=None, cmd: str=None, param: str=None, alarm: str=None) -> bool:
        # open connection and send packet
        reader, writer = await asyncio.open_connection("127.0.0.1", 54321)
        if reqtype == "cmd":
            payload = {
                "type": "cmd",
                "cmdtype": cmdtype,
                "cmd": cmd,
                "param": param
            }
        elif reqtype == "ALARM":
            payload = {
                "type": "ALARM",
                "ack": alarm
            }
        else:
            raise HEVPacketError("Invalid packet type")

        logging.info(payload)
        packet = json.dumps(payload).encode() + b'\0'

        writer.write(packet)
        await writer.drain()

        # wait for acknowledge
        data = await reader.readuntil(separator=b'\0')
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

    def send_cmd(self, cmdtype:str, cmd: str, param: Union[float,int]=None) -> bool:
        # send a cmd and wait to see if it's valid
        return asyncio.run(self.send_request("cmd", cmdtype=cmdtype, cmd=cmd, param=param))

    def ack_alarm(self, alarm: str) -> bool:
        # acknowledge alarm to remove it from the hevserver list
        return asyncio.run(self.send_request("ALARM", alarm=alarm))

    def get_values(self) -> Dict:
        # get sensor values from db
        return self._fastdata

    def get_readback(self) -> Dict:
        # get readback from db
        return self._readback

    def get_cycle(self) -> Dict:
        # get cycle data from db
        return self._cycle

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
        values = hevclient.get_values() # returns a dict or None
        alarms = hevclient.get_alarms() # returns a list of alarms currently ongoing
        print(values)
        if values is None:
            i = i+1 if i > 0 else 0
        else:
            print(f"Values: {json.dumps(values, indent=4)}")
            print(f"Alarms: {alarms}")
        time.sleep(1)
    
    # acknowledge the oldest alarm
    try:
        hevclient.ack_alarm(alarms[0]) # blindly assume we have one after 40s
    except:
        logging.info("No alarms received")

    time.sleep(2)
    print(f"Alarms: {hevclient.get_alarms()}")

    # set a timeout
    hevclient.send_cmd("SET_TIMEOUT", "INHALE", 1111)

    # check for the readback
    for i in range(10):
        print(f"Readback: {json.dumps(hevclient.get_readback(), indent=4)}")
        print(f"Alarms: {hevclient.get_alarms()}")
        time.sleep(1)

    print(hevclient.send_cmd("GENERAL", "STOP"))
