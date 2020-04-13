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

# alarms: manual, gas supply, apnea, expired minute volume,
#         upper pressure limit, power failure


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
            data = await reader.read(500)
            payload = json.loads(data.decode("utf-8"))
            with self._lock:
                self._values = payload["sensors"]
                self._alarms = payload["alarms"]

        # close connection
        writer.close()
        await writer.wait_closed()

    def start_client(self) -> None:
        asyncio.run(self.polling())

    async def send_request(self, cmd: str, param: str=None) -> bool:
        # open connection and send packet
        reader, writer = await asyncio.open_connection("127.0.0.1", 54321)

        payload = {
            "type": "cmd",
            "cmd": cmd,
            "param": param
        }

        packet = json.dumps(payload).encode()

        writer.write(packet)
        await writer.drain()

        # wait for acknowledge
        data = await reader.read(300)
        data = json.loads(data.decode("utf-8"))

        # close connection to free up socket
        writer.close()
        await writer.wait_closed()

        # check that acknowledge is meaningful
        if data["type"] == "ack":
            logging.info(f"Command {cmd} sent successfully")
            return True
        else:
            logging.warning(f"Sending command {cmd} failed")
            return False

    def send_cmd(self, cmd: str, param: str=None) -> bool:
        # send a cmd and wait to see if it's valid
        return asyncio.run(self.send_request(cmd))

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


    # Play with sensor values and alarms
    for i in range(30):
        values = hevclient.get_values() # returns a dict or None
        alarms = hevclient.get_alarms() # returns a list of alarms currently ongoing
        if values is None:
            i = i+1 if i > 0 else 0
        else:
            print(f"Values: {json.dumps(values, indent=4)}")
            print(f"Alarms: {alarms}")
        time.sleep(1)

    # send commands:
    print(hevclient.send_cmd("CMD_START"))
    time.sleep(1)
    print("This one will fail since foo is not in the command_codes enum:")
    print(hevclient.send_cmd("foo"))

    # print some more values
    for i in range(10):
        print(f"Alarms: {hevclient.get_alarms()}")
        print(f"Values: {json.dumps(hevclient.get_values(), indent=4)}")
        print(f"Alarms: {hevclient.get_alarms()}")
        time.sleep(1)
