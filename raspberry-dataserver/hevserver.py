#!/usr/bin/env python3
# data server to manage comms between UIs and LLI
#
# Author: Dónal Murray <donal.murray@cern.ch>

import copy
import asyncio
import json
import time
import threading
import argparse
import svpi
import hevfromtxt
import os
import psutil
from pathlib import Path
from hevtestdata import HEVTestData
from CommsLLI import CommsLLI
from BatteryLLI import BatteryLLI
from CommsCommon import PAYLOAD_TYPE, CMD_TYPE, CMD_GENERAL, CMD_SET_DURATION, VENTILATION_MODE, ALARM_TYPE, ALARM_CODES, CMD_MAP, CommandFormat, AlarmFormat, PersonalFormat
from collections import deque
from serial.tools import list_ports
from typing import List
from struct import error as StructError
import logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.INFO)

class HEVPacketError(Exception):
    pass

class HEVAlreadyRunning(Exception):
    pass

class HEVServer(object):
    def __init__(self, comms_lli, battery_lli):
        self._alarms = []
        self._dblock = threading.Lock()  # make alarms db threadsafe
        self._comms_lli = comms_lli
        self._battery_lli = battery_lli

        self._broadcasts = []
        self._broadcasting = True

    def push_to(self, queue, payload) -> None:
        try:
            queue.put_nowait(payload)
        except asyncio.queues.QueueFull:
            # if the queue is full, dump the oldest element and put again
            queue.get_nowait()
            queue.task_done()
            queue.put_nowait(payload)

    async def polling(self):
        while True:
            payload = await self._comms_lli._payloadrecv.get()
            logging.debug(f"Payload received: {payload}")
            # check if it is data or alarm
            payload_type = payload.getType()
            whitelist = [
                PAYLOAD_TYPE.DATA,
                PAYLOAD_TYPE.READBACK,
                PAYLOAD_TYPE.CYCLE,
                PAYLOAD_TYPE.TARGET,
                PAYLOAD_TYPE.THRESHOLDS,
                PAYLOAD_TYPE.ALARM,
                PAYLOAD_TYPE.DEBUG,
                PAYLOAD_TYPE.IVT,
                PAYLOAD_TYPE.PERSONAL,
                PAYLOAD_TYPE.CMD
            ]
            if payload_type in whitelist:
                # fork data to broadcast threads
                for queue in self._broadcasts:
                    self.push_to(queue, payload)

                #if payload_type == PAYLOAD_TYPE.PERSONAL : print("PERSONAL")
            elif payload_type in PAYLOAD_TYPE:
                # valid payload but ignored
                pass
            else:
                # invalid packet, don't throw exception just log and pop
                logging.error(f"Received invalid packet, ignoring: {payload}")

    
    async def handle_battery(self) -> None:
        while True:
            try:
                # wait for a new battery state from the batterylli
                payload = await self._battery_lli.queue.get()
                logging.debug(f"Payload received: {payload}")
                self._battery_lli.queue.task_done() # consume entry
                if payload.getType() != PAYLOAD_TYPE.BATTERY:
                    raise HEVPacketError("Battery state invalid")

                # fork data to broadcast threads
                for queue in self._broadcasts:
                    self.push_to(queue, payload)

                # send to uC
                self._comms_lli.writePayload(payload)
            except HEVPacketError as e:
                logging.error(e)
            

    async def handle_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        # listen for queries on the request socket
        data = await reader.readuntil(separator=b'\0')
        data = data[:-1] # snip off nullbyte
        request = json.loads(data.decode("utf-8"))

        # logging
        addr = writer.get_extra_info("peername")
        logging.info(f"Answering request from {addr}")
        
        try:
            reqtype = request["type"]
            if reqtype == "CMD":
                reqcmd = request["cmd"]
                reqcmdtype = request["cmdtype"]
                reqparam = request["param"] if request["param"] is not None else 0

                command = CommandFormat(cmd_type=CMD_TYPE[reqcmdtype].value,
                                        cmd_code=CMD_MAP[reqcmdtype].value[reqcmd].value,
                                        param=reqparam)

                #print('***sending cmd ') 
                #print(command)
                self._comms_lli.writePayload(command)

                # processed and sent to controller, send ack to GUI since it's in enum
                payload = {"type": "ack"}

            elif reqtype == "DATA":
                # ignore for the minute
                pass
            elif reqtype == "READBACK":
                # ignore for the minute
                pass
            elif reqtype == "CYCLE":
                # ignore for the minute
                pass
            elif reqtype == "TARGET":
                # ignore for the minute
                pass
            elif reqtype == "PERSONAL":
                # ignore for the minute
                name   = request["name"].encode()
                age    = int(request["age"])
                sex    = request["sex"].encode()
                height = int(request["height"])
                weight = int(request["weight"])
                pfmt = PersonalFormat(name=name, age=age, sex=sex, height=height, weight=weight)
                self._comms_lli.writePayload(pfmt)
                payload = {"type": "ack"}
                pass
            elif reqtype == "IVT":
                # ignore for the minute
                pass
            elif reqtype == "DEBUG":
                # ignore for the minute
                pass
            elif reqtype == "ALARM":
                # acknowledgement of alarm from gui
                reqalarm_type = request["alarm_type"]
                reqalarm_code = ALARM_CODES[request["alarm_code"]]
                reqparam = request["param"] if request["param"] is not None else 0

                alarm_to_ack = AlarmFormat(alarm_type=ALARM_TYPE[reqalarm_type],
                                           alarm_code=reqalarm_code,
                                           param=reqparam)
                try:
                    # delete alarm if it exists
                    with self._dblock:
                        for alarm in self._alarms:
                            if alarm == alarm_to_ack:
                                self._alarms.remove(alarm)
                    payload = {"type": "ack"}
                except NameError as e:
                    raise HEVPacketError(f"Alarm could not be removed. May have been removed already. {e}")
            else:
                raise HEVPacketError(f"Invalid request type")
        except (NameError, KeyError, HEVPacketError) as e:
            # invalid request: reject immediately
            logging.warning(f"Invalid packet: {e}")
            payload = {"type": "nack"}
        except Exception as e:
            logging.critical(e)
            exit(1)

        # send reply and close connection
        packet = json.dumps(payload).encode() + b'\0'
        writer.write(packet)
        await writer.drain()
        writer.close()

    async def handle_broadcast(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        # log address
        addr = writer.get_extra_info("peername")
        logging.info(f"Broadcasting to {addr!r}")

        self._broadcasts[addr[1]] = asyncio.Queue(maxsize=16) # append new queue

        while self._broadcasting:
            # wait for data from queue
            payload = await self._broadcasts[addr[1]].get()
            # Alarm is latched until acknowledged in GUI
            if payload.getType() == PAYLOAD_TYPE.ALARM:
                if payload not in self._alarms:
                    self._alarms.append(payload)
                else:
                    # update param and timestamp
                    idx = self._alarms.index(payload)
                    self._alarms[idx] = payload

            alarms = self._alarms if len(self._alarms) > 0 else None

            data_type = payload.getType().name
            broadcast_packet = {"type": data_type}

            broadcast_packet[data_type] = payload.getDict()

            broadcast_packet["alarms"] = [alarm.getDict() for alarm in alarms] if alarms is not None else []
            self._broadcasts[addr[1]].task_done()

            logging.info(f"Send data for timestamp: {broadcast_packet[data_type]['timestamp']}")
            logging.debug(f"Send: {json.dumps(broadcast_packet,indent=4)}")

            try:
                writer.write(json.dumps(broadcast_packet).encode() + b"\0")
                await writer.drain()
            except (ConnectionResetError, BrokenPipeError):
                # Connection lost, stop trying to broadcast and free up socket
                logging.warning(f"Connection lost with {addr!r}")
                self._broadcasting = False
                continue

        self._broadcasting = True
        writer.close()
        del self._broadcasts[addr[1]]

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
        logging.debug(f"Serving on {addr}")

        async with server:
            await server.serve_forever()

    async def main(self) -> None:
        self._datavalid = threading.Event() # initially false
        LOCALHOST = "127.0.0.1"
        b1 = self.serve_broadcast(LOCALHOST, 54320)  # WebUI broadcast
        r1 = self.serve_request(LOCALHOST, 54321)    # joint request socket
        b2 = self.serve_broadcast(LOCALHOST, 54322)  # NativeUI broadcast
        battery = self.handle_battery()              # Battery status
        poll = self.polling()                        # Battery status
        tasks = [b1, r1, b2, poll, battery]
        await asyncio.gather(*tasks, return_exceptions=True)

def getArduinoPort():
    # get arduino serial port
    port_device = None
    for port in list_ports.comports():
        vidpid = ""
        if port.pid != None and port.vid != None:
            vidpid = f"{ port.vid:04x}:{port.pid:04x}".upper()
            logging.debug(vidpid)
        if port.manufacturer and "ARDUINO" in port.manufacturer.upper():
            port_device = port.device 
        elif vidpid == "10C4:EA60" :
            port_device = port.device 
    if port_device is None:
        logging.critical(f"Arduino disconnected")
        exit(1)
    return port_device


async def arduinoConnected():
    # TODO make this smarter and only run when no data has been seen for a while
    # TODO make a version to check the arduino emulator - low priority
    while True:
        await asyncio.sleep(1)
        getArduinoPort()


if __name__ == "__main__":
    tasks = [] # asyncio tasks
    loop = asyncio.get_event_loop()
    try:
        #parser to allow us to pass arguments to hevserver
        parser = argparse.ArgumentParser(description='Arguments to run hevserver')
        parser.add_argument('-i', '--inputFile', type=str, default = '', help='Load data from file')
        parser.add_argument('-d', '--debug', action='count', default=0, help='Show debug output')
        parser.add_argument('--use-test-data', action='store_true', help='Use test data source')
        parser.add_argument('--use-dump-data', action='store_true', help='Use dump data source')
        parser.add_argument('--dump', type=int, default=0, help='Dump NUM raw data packets to file')
        parser.add_argument('-o', '--dumpfile', type=str, default = '', help='File to dump to')
        args = parser.parse_args()
        if args.debug == 0:
            logging.getLogger().setLevel(logging.WARNING)
        elif args.debug == 1:
            logging.getLogger().setLevel(logging.INFO)
        else:
            logging.getLogger().setLevel(logging.DEBUG)
    
        # check if hevserver is running
        pidfile = "/dev/shm/hevpid"
        mypid = os.getpid()
        if os.path.exists(pidfile):
            with open(pidfile, "r") as f:
                try:
                    pid = int(f.read())
                except (OSError, ValueError):
                    pass
                else:
                    if psutil.pid_exists(pid):
                        raise HEVAlreadyRunning(f"hevserver is already running. To kill it run:\n $ kill {pid}")
        
        with open(pidfile, 'w') as f:
            f.write(str(mypid))

        if args.use_test_data:
            comms_lli = HEVTestData()
            logging.info(f"Using test data source")
        elif args.inputFile != '':
            if args.inputFile[-1-3:] == '.txt':
                # just ignore actual filename and read from both valid inputfiles
                comms_lli = hevfromtxt.hevfromtxt()
            else:
                comms_lli = svpi.svpi(args.inputFile)
        else:
            # initialise low level interface
            try:
                if args.use_dump_data:
                    port_device = '/dev/shm/ttyEMU0'
                else:
                    port_device = getArduinoPort()
                    connected = arduinoConnected()
                    tasks.append(connected)
                # setup serial device and init server
                if args.dump == 0:
                    comms_lli = CommsLLI(loop)
                elif args.dump > 0:
                    if args.dumpfile == '':
                        logging.critical("No dump file specified")
                        raise KeyboardInterrupt # fake ctrl+c
                    logging.warning(f"Dumping {args.dump} packets to {args.dumpfile}")
                    comms_lli = CommsLLI(loop, file=args.dumpfile, number=args.dump)
                else:
                    logging.critical("Invalid number of packets to dump")
                    raise KeyboardInterrupt # fake ctrl+c
                comms = comms_lli.main(port_device, 115200)
                tasks.append(comms)
                logging.info(f"Serving data from device {port_device}")
            except NameError:
                logging.critical("Arduino not connected")
                exit(1)

        if args.dump:
            battery_lli = BatteryLLI(dump=True)
        else:
            battery_lli = BatteryLLI()
        battery = battery_lli.main()
        tasks.append(battery)

        # create tasks
        hevsrv = HEVServer(comms_lli, battery_lli)
        server = hevsrv.main()
        tasks.append(server)

        # run tasks
        asyncio.gather(*tasks, return_exceptions=True)
        loop.run_forever()
    except asyncio.CancelledError:
        pass
    except HEVAlreadyRunning as e:
        logging.critical(e)
    except KeyboardInterrupt:
        logging.info("Server stopped")
    except StructError:
        logging.error("Failed to parse packet")
