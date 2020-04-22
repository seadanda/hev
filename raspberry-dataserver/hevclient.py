#!/usr/bin/env python3
# client side for the data server to manage comms between UIs and LLI
#
# Author: Dónal Murray <donal.murray@cern.ch>

import asyncio
import time
import json
import threading
from typing import List, Dict
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
        self._values = None  # db for sensor values
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
                data = await reader.read(600)
                if data[-1] == 0x00:
                    data = data[:-1]
                payload = json.loads(data.decode("utf-8"))
                if payload["type"] == "broadcast":
                    with self._lock:
                        self._values = payload["sensors"]
                        self._alarms = payload["alarms"]
                elif payload["type"] == "keepalive":
                    #Still alive
                    pass
                else:
                    raise HEVPacketError(f"Invalid packet type: {payload['type']}")
            except json.decoder.JSONDecodeError:
                logging.warning(f"Could not decode packet: {data}")

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
        elif reqtype == "alarm":
            payload = {
                "type": "alarm",
                "ack": alarm
            }

        logging.info(payload)
        packet = json.dumps(payload).encode()

        writer.write(packet)
        await writer.drain()

        # wait for acknowledge
        data = await reader.read(300)
        if data[-1] == 0x00:
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

    def send_cmd(self, cmdtype:str, cmd: str, param: str=None) -> bool:
        # send a cmd and wait to see if it's valid
        return asyncio.run(self.send_request("cmd", cmdtype=cmdtype, cmd=cmd, param=param))

    def ack_alarm(self, alarm: str) -> bool:
        # acknowledge alarm to remove it from the hevserver list
        return asyncio.run(self.send_request("alarm", alarm=alarm))

    def get_values(self) -> Dict:
        # get sensor values from db
        return self._values

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

    # send commands:
    time.sleep(1)
    print("This one will fail since foo is not in the CMD_GENERAL enum:")
    print(hevclient.send_cmd("GENERAL", "foo"))

    # print some more values
    for i in range(10):
        print(f"Values: {json.dumps(hevclient.get_values(), indent=4)}")
        print(f"Alarms: {hevclient.get_alarms()}")
        time.sleep(1)

    print(hevclient.send_cmd("GENERAL", "STOP"))
