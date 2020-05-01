#!/usr/bin/env python3

# Communication protocol based on HDLC format
# author Peter Svihra <peter.svihra@cern.ch>
# adapted for async DM

import libscrc
import binascii
import logging
from typing import ClassVar

# Set up logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().setLevel(logging.DEBUG)


def commsFromBytes(byteArray):
    comms = CommsFormat()
    comms.copyBytes(byteArray)
    
    return comms

def generateAlarm(payload):
    comms = CommsFormat(info_size = payload.getSize(), address = 0xC0)
    comms.setInformation(payload.byteArray)
    return comms

def generateCmd(payload):
    comms = CommsFormat(info_size = payload.getSize(), address = 0x80)
    comms.setInformation(payload.byteArray)
    return comms

def generateData(payload):
    comms = CommsFormat(info_size = payload.getSize(), address = 0x40)
    comms.setInformation(payload.byteArray)
    return comms


# basic format based on HDLC
class CommsFormat:
    def __init__(self, info_size = 0, address = 0x00, control = [0x00, 0x00]):
        self._data = bytearray(7 + info_size)
        self._info_size = info_size
        self._crc = None
        
        self.assignBytes(self.getStart()  , bytes([0x7E])   , calc_crc = False)
        self.assignBytes(self.getAddress(), bytes([address]), calc_crc = False)
        self.assignBytes(self.getControl(), bytes(control)  , calc_crc = False)
        self.assignBytes(self.getStop()   , bytes([0x7E])   , calc_crc = False)
        
        self.generateCrc()
        
    def getStart(self):
        return 0
    def getAddress(self):
        return 1
    def getControl(self):
        return 2
    def getInformation(self):
        return 4
    def getFcs(self):
        return 4 + self._info_size
    def getStop(self):
        return 4 + self._info_size + 2
    
    def setAddress(self, address):
        self.assignBytes(self.getAddress(), bytes([address]), 1)
        
    def setControl(self, control):
        self.assignBytes(self.getControl(), bytes(control), 2)
    
    def setInformation(self, bytes_array):
        # convert provided value
        self.assignBytes(self.getInformation(), bytes_array)
        
    def setSequenceSend(self, value):
        # sequence sent valid only for info frames (not supervisory ACK/NACK)
        if (self._data[self.getControl() + 1] & 0x01) == 0:
            value = (value << 1) & 0xFE
            self.assignBytes(self.getControl() + 1, value.to_bytes(1, byteorder='little'), 1)

    def setSequenceReceive(self, value):
        value = (value << 1) & 0xFE
        self.assignBytes(self.getControl()    , value.to_bytes(1, byteorder='little'), 1)
        
    def getSequenceSend(self):
        # sequence sent valid only for info frames (not supervisory ACK/NACK)
        if (self._data[self.getControl() + 1] & 0x01) == 0:
            return (self._data[self.getControl() + 1] >> 1) & 0x7F
        else:
            return 0xFF
        
    def getSequenceReceive(self):
        return (self._data[self.getControl()] >> 1) & 0x7F
        
    def assignBytes(self, start, values, calc_crc = True):
        for idx in range(len(values)):
            self._data[start + idx] = values[idx]
        if calc_crc:
            self.generateCrc()
        
    # generate checksum
    def generateCrc(self, assign = True):
        self._crc = libscrc.x25(bytes(self._data[self.getAddress():self.getFcs()])).to_bytes(2, byteorder='little')
        if assign:
            self.assignBytes(self.getFcs(), self._crc, calc_crc = False)
            
    def compareCrc(self):
        self.generateCrc(False)
        fcs = self.getData()[self.getFcs():self.getFcs()+2]
        return self._crc in fcs
    
    
    def getData(self):
        return self._data

    def copyData(self, data_array):
        self.copyBytes(data_array.to_bytes(self._info_size, byteorder='little'))
        
    def copyBytes(self, bytes_array):
        self._info_size = len(bytes_array) - 7
        self._data     = bytes_array

    def encode(self):
        byteArray = self._data
    
        # prefix escape pattern for data bytes which happen to contain an escape pattern
        temp = b''
        temp += bytes([byteArray[0]])
        oldpos = 1 # start after flag byte and search until before stop byte
        if b'\x7D' in byteArray[oldpos:-1] or b'\x7E' in byteArray[oldpos:-1]:
            while b'\x7D' in byteArray[oldpos:-1] or b'\x7E' in byteArray[oldpos:-1]:
                print("changing")
                posd = byteArray.find(b'\x7D')
                pose = byteArray.find(b'\x7E')
                pos = posd if posd < pose else pose
                temp += bytes([byteArray[oldpos:pos]]) + b'\x7D' + bytes([byteArray[pos] ^ (1<<5)])
                oldpos = pos+1

            byteArray = temp + bytes([byteArray[-1]])

        print(byteArray)
        return byteArray

    # escape any 0x7D or 0x7E with 0x7D and swap bit 5
    def escapeByte(self, byte):
        if byte == 0x7D or byte == 0x7E:
            return [0x7D, byte ^ (1<<5)]
        else:
            return [byte]

    def encoder(self):
        data = self._data
        try:
            stream = [escaped for byte in data[1:-1] for escaped in self.escapeByte(byte)]
            result = bytearray([data[0]] + stream + [data[-1]])
            return result
        except:
            return None


class CommsPacket(object):
    separator: ClassVar[int] = bytes([0x7E])

    def __init__(self, data):
        self._data = data
        self._sequence = None
        self._address = None
        self._byteArray = None
        self._datavalid = False
        self._acked = None

    @property
    def byteArray(self):
        return self._byteArray
        
    @property
    def sequence(self):
        return self._sequence

    @property
    def address(self):
        return self._address

    @property
    def acked(self):
        return self._acked

    def decode(self):
        """Returns true for data, false for ack/nack"""
        byteArray = self._data
    
        # remove escape sequences for bytes containing escape patterns and convert back
        if b'\x7D' in byteArray:
            temp = b''
            oldpos = 0
            while b'\x7D' in byteArray[oldpos:]:
                pos = byteArray.find(b'\x7D')
                temp += byteArray[oldpos:pos] + bytes([byteArray[pos+1] ^ (1<<5)])
                oldpos = pos+2
            byteArray = temp

        # check checksum and control bytes
        tmp_comms = commsFromBytes(byteArray)
        if tmp_comms.compareCrc():
            control     = tmp_comms.getData()[tmp_comms.getControl()+1]
            self._sequence_receive = (tmp_comms.getData()[tmp_comms.getControl()] >> 1) & 0x7F
            
            # get type of packet
            ctrl_flag    = control & 0x0F
            if ctrl_flag == 0x05:
                # received NACK
                self._acked = False
                retval = True
            elif ctrl_flag == 0x01:
                # received ACK
                self._acked = True
                retval = False
            else:
                # received data
                self._sequence = ((control >> 1) & 0x7F) + 1
                self._address = tmp_comms.getData()[1]
                self._byteArray = tmp_comms.getData()[tmp_comms.getInformation():tmp_comms.getFcs()]
                retval = True
        
        return retval

# ACK specific formating
class CommsACK(CommsFormat):
    def __init__(self, address):
        super().__init__(control = [0x00, 0x01], address = address)
        
# NACK specific formating
class CommsNACK(CommsFormat):
    def __init__(self, address):
        super().__init__(control = [0x00, 0x05], address = address)
