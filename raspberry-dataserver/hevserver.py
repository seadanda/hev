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
import hevfromtxt
import commsControl
from commsConstants import PAYLOAD_TYPE, CMD_TYPE, CMD_GENERAL, CMD_SET_TIMEOUT, CMD_SET_MODE, ALARM_CODES, CMD_MAP, CommandFormat
from collections import deque
from serial.tools import list_ports
from typing import List
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class HEVPacketError(Exception):
    pass

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
        if payload_type == PAYLOAD_TYPE.ALARM:
            # Alarm is latched until acknowledged in GUI
            alarm_packet = payload.getDict()
            alarmCode = alarm_packet["alarmCode"]
            with self._dblock:
                try:
                    alarm = ALARM_CODES(alarmCode).name
                    if alarm not in self._alarms:
                        self._alarms.append(alarm)
                except ValueError as e:
                    # alarmCode does not exist in the enum, this is serious!
                    logging.error(e)
                    self._alarms.append("ARDUINO_FAIL") # assume Arduino is broken
            # let broadcast thread know there is data to send
            with self._dvlock:
                self._datavalid.set()
        elif payload_type == PAYLOAD_TYPE.DATA:
            # pass data to db
            with self._dblock:
                self._values = payload.getDict()
            # let broadcast thread know there is data to send
            with self._dvlock:
                self._datavalid.set()
        elif payload_type == PAYLOAD_TYPE.CMD:
            # ignore for the minute
            pass
        elif payload_type == PAYLOAD_TYPE.UNSET:
            # ignore for the minute
            pass
        else:
            # invalid packet, don't throw exception just log and pop
            logging.error("Received invalid packet, ignoring")

        # pop from lli queue
        self._lli.pop_payloadrecv()
            
    async def handle_request(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        # listen for queries on the request socket
        data = await reader.read(300)
        request = json.loads(data.decode("utf-8"))

        # logging
        addr = writer.get_extra_info("peername")
        logging.info(f"Answering request from {addr}")
        
        try:
            reqtype = request["type"]
            if reqtype == "cmd":
                reqcmd = request["cmd"]
                if reqcmd == "CMD_START" or reqcmd == "CMD_STOP":
                    # temporary, since CMD_START and CMD_STOP are now deprecated
                    reqcmdtype = "GENERAL" # fake a general command
                    logging.warning("CMD_START AND CMD_STOP are deprecated and will be removed in a future release.")
                    reqcmd = reqcmd.split("_")[1]
                else:
                    reqcmdtype = request["cmdtype"]
                reqparam = request["param"] if request["param"] is not None else 0

                command = CommandFormat(cmdType=CMD_TYPE[reqcmdtype].value,
                                        cmdCode=CMD_MAP[reqcmdtype].value[reqcmd].value,
                                        param=reqparam)

                self._lli.writePayload(command)

                # processed and sent to controller, send ack to GUI since it's in enum
                payload = {"type": "ack"}

            elif reqtype == "broadcast":
                # ignore for the minute
                pass
            elif reqtype == "alarm":
                # acknowledgement of alarm from gui
                try:
                    # delete alarm if it exists
                    with self._dblock:
                        self._alarms.remove(request["ack"])
                    payload = {"type": "ack"}
                except NameError as e:
                    raise HEVPacketError(f"Alarm could not be removed. May have been removed already. {e}")
            else:
                raise HEVPacketError(f"Invalid request type")

            packet = json.dumps(payload).encode()

            # send reply and close connection
            writer.write(packet)
            await writer.drain()
            writer.close()

        except (NameError, KeyError, HEVPacketError) as e:
            # invalid request: reject immediately
            logging.warning(f"Invalid packet: {e}")
            payload = {"type": "nack"}
            packet = json.dumps(payload).encode()
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
                # set timeout such that there is never pileup
                await asyncio.wait_for(self._datavalid.wait(), timeout=0.05)
            except asyncio.TimeoutError:
                continue
            # take lock of db and prepare packet
            with self._dblock:
                values: List[float] = self._values
                alarms = self._alarms if len(self._alarms) > 0 else None

            broadcast_packet = {}
            broadcast_packet["sensors"] = values
            broadcast_packet["alarms"] = alarms # add alarms key/value pair

            logging.debug(f"Send: {json.dumps(broadcast_packet,indent=4)}")

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
        b2 = self.serve_broadcast(LOCALHOST, 54322)  # NativeUI broadcast
        tasks = [b1, r1, b2]
        #tasks = [b1, r1]
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
        if args.inputFile[-1-3:] == '.txt':
            # assume sample.txt format
            lli = hevfromtxt.hevfromtxt(args.inputFile)
        else:
            # assume hex dump
            lli = svpi.svpi(args.inputFile)

        logging.info(f"Serving data from {args.inputFile}")
    else:
        # get arduino serial port
        for port in list_ports.comports():
            vidpid = ""
            if port.pid != None and port.vid != None:
                vidpid = f"{ port.vid:04x}:{port.pid:04x}".upper()
                logging.debug(vidpid)
            if port.manufacturer and "ARDUINO" in port.manufacturer.upper():
                port_device = port.device 
            elif vidpid == "10C4:EA60" :
                port_device = port.device 

        # initialise low level interface
        try:
            lli = commsControl.commsControl(port=port_device)
            logging.info(f"Serving data from device {port_device}")
        except NameError:
            logging.error("Arduino not connected")
            exit(1)

    hevsrv = HEVServer(lli)

    # serve forever
    while True:
        pass
