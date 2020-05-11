#!/usr/bin/env python3

# Communication protocol between rasp and arduino based on HDLC format
# author Peter Svihra <peter.svihra@cern.ch>

import serial
from serial.tools import list_ports

import threading
import time
import copy

import CommsFormat
import CommsCommon
from collections import deque

import binascii
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# communication class that governs talking between devices
class CommsControl():
    def __init__(self, port, baudrate = 115200, queueSizeReceive = 16, queueSizeSend = 16):
        
        self._serial = None
        self.openSerial(port, baudrate)

        # send queues are FIFO ring-buffers of the defined size
        self._alarms   = deque(maxlen = queueSizeSend)
        self._commands = deque(maxlen = queueSizeSend)
        self._data     = deque(maxlen = queueSizeSend)
        self._dw_lock  = threading.Lock()   # data write lock
        
        # received queue and observers to be notified on update
        self._payloadrecv = deque(maxlen = queueSizeReceive)
        self._observers = []
        self._dr_lock  = threading.Lock()   # data read lock
        
        # needed to find packet frames
        self._received = []
        self._receivedStart = 0
        self._foundStart = False
        self._timeLastTransmission = int(round(time.time() * 1000))
        
        # packet counter checker
        self._sequence_send    = 0
        self._sequence_receive = 0
        
        # initialize of the multithreading
        self._lock_serial = threading.Lock()
        self._receiving = True
        threading.Thread(target=self.receiver, daemon=True).start()
        
        self._sending   = True
        self._datavalid = threading.Event()  # callback for send process
        threading.Thread(target=self.sender, daemon=True).start()
    
    # open serial port
    def openSerial(self, port, baudrate = 115200, timeout = 2):
        if port is not None:
            self._serial = serial.Serial(port = port, baudrate=baudrate, timeout = timeout, dsrdtr = True)
        else:
            try:
                self._serial.close()
            except:
                logging.warning("Serial device not open")
            self._serial = None
        
    def sender(self):
        while self._sending:
            self._datavalid.wait()
            if self._serial is not None:
                self.sendQueue(self._alarms  ,  10)
                self.sendQueue(self._commands,  50)
                self.sendQueue(self._data    , 200)
            if self.finishedSending():
                self._datavalid.clear()
                    
    def finishedSending(self):
        with self._dw_lock:
            try:
                if (len(self._alarms) + len(self._data) + len(self._commands)) > 0:
                    return False
                else:
                    return True
            except:
                return True

    def receiver(self):
        while self._receiving:
            # sleep 1 ms in order not to ramp the CPU to 100%
            # - safe since arduino sends data in O(10ms) steps
            # - 1 ms due to prompt catch of the ACK/NACK
            time.sleep(0.001)
            if self._serial is not None:
                if self._serial.in_waiting > 0:
                    data = []
                    with self._lock_serial:
                        logging.debug("Receiving data...")
                        data = self._serial.read(self._serial.in_waiting)
                    self.processPacket(data)

    def sendQueue(self, queue, timeout):
        with self._dw_lock:
            if len(queue) > 0:
                logging.debug(f'Queue length: {len(queue)}')
                current_time = int(round(time.time() * 1000))
                if current_time > (self._timeLastTransmission + timeout):
                    self._timeLastTransmission = current_time
                    queue[0].setSequenceSend(self._sequence_send)
                    self.sendPacket(queue[0])
                    
    def getQueue(self, payload_type):
        if   payload_type == CommsCommon.PAYLOAD_TYPE.ALARM:
            return self._alarms
        elif payload_type == CommsCommon.PAYLOAD_TYPE.CMD:
            return self._commands
        elif payload_type == CommsCommon.PAYLOAD_TYPE.DATA:
            return self._data
        else:
            return None
    
    def getInfoType(self, address):
        address &= 0xC0
        if address == 0xC0:
            return CommsCommon.PAYLOAD_TYPE.ALARM
        elif address == 0x80:
            return CommsCommon.PAYLOAD_TYPE.CMD
        elif address == 0x40:
            return CommsCommon.PAYLOAD_TYPE.DATA
        else:
            return CommsCommon.PAYLOAD_TYPE.UNSET

    def processPacket(self, data):
        for byte in data:
            byte = bytes([byte])
            # TODO: this could be written in more pythonic way
            # force read byte by byte
            self._received.append(byte)
#             logging.info(byte)
            # find starting flag of the packet
            if byte == bytes([0x7E]) and ((len(self._received) < self._receivedStart + 6) or not self._foundStart ):
                self._foundStart    = True
                self._receivedStart = len(self._received)
            # find ending flag of the packet
            elif byte == bytes([0x7E]) :
                decoded = self.decoder(self._received, self._receivedStart)
                if decoded is not None:
                    logging.debug(binascii.hexlify(decoded))
                    tmp_comms = CommsFormat.commsFromBytes(decoded)
                    if tmp_comms.compareCrc():
                        control     = tmp_comms.getData()[tmp_comms.getControl()+1]
                        self._sequence_receive = (tmp_comms.getData()[tmp_comms.getControl()] >> 1) & 0x7F
                        
                        # get type of payload and corresponding queue
                        payload_type = self.getInfoType(tmp_comms.getData()[tmp_comms.getAddress()])
                        queue        = self.getQueue(payload_type)

                        # get type of packet
                        ctrl_flag    = control & 0x0F
                        if ctrl_flag == 0x05:
                            logging.debug("Received NACK")
                            # received NACK
                        elif ctrl_flag == 0x01:
                            logging.debug("Received ACK")
                            # received ACK
                            self.finishPacket(queue)
                        else:
                            sequence_receive = ((control >> 1) & 0x7F) + 1
                            address = tmp_comms.getData()[tmp_comms.getAddress():tmp_comms.getControl()]
                            
                            if self.receivePacket(payload_type, tmp_comms):
                                logging.debug("Preparing ACK")
                                comms_response = CommsFormat.CommsACK(address = address[0])
                            else:
                                logging.debug("Preparing NACK")
                                comms_response = CommsFormat.CommsNACK(address = address[0])
                            comms_response.setSequenceReceive(sequence_receive)
                            self.sendPacket(comms_response)
                    
                self._received.clear()
                
                self._foundStart    = False
                self._receivedStart = -1
        
    def writePayload(self, payload):
        payload_type = payload.getType()
        if   payload_type == CommsCommon.PAYLOAD_TYPE.ALARM:
            tmp_comms = CommsFormat.generateAlarm(payload)
        elif payload_type == CommsCommon.PAYLOAD_TYPE.CMD:
            tmp_comms = CommsFormat.generateCmd(payload)
        elif payload_type == CommsCommon.PAYLOAD_TYPE.DATA:
            tmp_comms = CommsFormat.generateData(payload)
        else:
            return False
        
        with self._dw_lock:
            queue = self.getQueue(payload_type)
            queue.append(tmp_comms)
            self._datavalid.set() # executes callback
            
        return True
        
    def sendPacket(self, comms):
        with self._lock_serial:
            logging.debug("Sending data...")
            logging.debug(binascii.hexlify(self.encoder(comms.getData())))
            self._serial.write(self.encoder(comms.getData()))
    
    def finishPacket(self, queue):
        try:
            with self._dw_lock:
                if len(queue) > 0:
                    # 0x7F to deal with possible overflows (0 should follow after 127)
                    if ((queue[0].getSequenceSend() + 1) & 0x7F) == self._sequence_receive:
                        self._sequence_send = (self._sequence_send + 1) % 128
                        queue.popleft()
        except:
            logging.debug("Queue is probably empty")
            
    # WIP: will be reworked
    def receivePacket(self, payload_type, comms_packet):
        if   payload_type == CommsCommon.PAYLOAD_TYPE.ALARM:
            payload = CommsCommon.AlarmFormat()
        elif payload_type == CommsCommon.PAYLOAD_TYPE.CMD:
            payload = CommsCommon.CommandFormat()
        elif payload_type == CommsCommon.PAYLOAD_TYPE.DATA:
            # decode data type
            data_type = comms_packet.getData()[comms_packet.getInformation() + 5]
            if data_type == CommsCommon.PAYLOAD_TYPE.DATA:
                payload = CommsCommon.DataFormat()
            elif data_type == CommsCommon.PAYLOAD_TYPE.READBACK:
                payload = CommsCommon.ReadbackFormat()
            elif data_type == CommsCommon.PAYLOAD_TYPE.CYCLE:
                payload = CommsCommon.CycleFormat()
            elif data_type == CommsCommon.PAYLOAD_TYPE.IVT:
                payload = CommsCommon.IVTFormat()
            elif data_type == CommsCommon.PAYLOAD_TYPE.DEBUG:
                payload = CommsCommon.DebugFormat()
            elif data_type == CommsCommon.PAYLOAD_TYPE.THRESHOLDS:
                # FIXME: nothing yet defined, TBD!!
                return False
            else:
                return False
        else:
            return False
        
        try:
            payload.fromByteArray(comms_packet.getData()[comms_packet.getInformation():comms_packet.getFcs()])
        except Exception:
            raise
        else:
            self.payloadrecv = payload
            return True
        return False

    # escape any 0x7D or 0x7E with 0x7D and swap bit 5
    def escapeByte(self, byte):
        if byte == 0x7D or byte == 0x7E:
            return [0x7D, byte ^ (1<<5)]
        else:
            return [byte]

    # encoding data according to the protocol - escape any 0x7D or 0x7E with 0x7D and swap 5 bit
    def encoder(self, data):
        try:
            stream = [escaped for byte in data[1:-1] for escaped in self.escapeByte(byte)]
            result = bytearray([data[0]] + stream + [data[-1]])
            return result
        except:
            return None
    
    # decoding data according to the defined protocol - escape any 0x7D or 0x7E with 0x7D and swap 5 bit
    def decoder(self, data, start):
        try:
            packets = data[start:-1]

            indRemove = [idx for idx in range(len(packets)) if packets[idx] == bytes([0x7D])]
            indChange = [idx+1 for idx in indRemove]

            stream = [packets[idx][0] ^ (1<<5) if idx in indChange else packets[idx][0] for idx in range(len(packets)) if idx not in indRemove]
            result = bytearray([data[start - 1][0]] + stream + [data[-1][0]])
            return result
        except:
            return None
        
    # callback to dependants to read the received payload
    @property
    def payloadrecv(self):
        with self._dr_lock:
            return self._payloadrecv

    @payloadrecv.setter
    def payloadrecv(self, payload):
        with self._dr_lock:
            self._payloadrecv.append(payload)
            payloadrecv = list(self._payloadrecv)
        logging.debug(f"Pushed {payload} to FIFO")
        for callback in self._observers:
            # peek at the leftmost item, don't pop until receipt confirmed
            callback(payloadrecv[0])

    def bind_to(self, callback):
        self._observers.append(callback)

    def pop_payloadrecv(self):
        # from callback. confirmed receipt, pop value
        with self._dr_lock:
            poppedval = self._payloadrecv.popleft()
            payloadrecv = list(self._payloadrecv)
        logging.debug(f"Popped {poppedval} from FIFO")
        if len(payloadrecv) > 0:
            # purge full queue if Dependant goes down when it comes back up
            for callback in self._observers:
                callback(payloadrecv[0])
        
# start as interactive session to be able to send and receive
if __name__ == "__main__" :
    # example dependant
    class Dependant(object):
        def __init__(self, lli):
            self._llipacket = None
            self._lli = lli
            self._lli.bind_to(self.update_llipacket)

        def update_llipacket(self, payload):
            if payload.getType() == CommsCommon.PAYLOAD_TYPE.DATA:
                logging.info(f"payload received: {payload.fsm_state}")

            self._llipacket = payload
            # pop from queue - protects against Dependant going down and not receiving packets
            self._lli.pop_payloadrecv()

    # get port number for arduino, mostly for debugging
    for port in list_ports.comports():
        try:
            if "ARDUINO" in port.manufacturer.upper():
                port = port.device
        except:
            pass

    comms   = CommsControl(port = port)
    example = Dependant(comms)
    
    cmd = CommsCommon.CommandFormat(cmd_type = CommsCommon.CMD_TYPE.GENERAL.value, cmd_code = CommsCommon.CMD_GENERAL.START.value, param=0)
    time.sleep(4)
    comms.writePayload(cmd)
    print('sent cmd start')
    print(cmd)
