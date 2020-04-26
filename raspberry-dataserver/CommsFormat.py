#!/usr/bin/env python3

# Communication protocol based on HDLC format
# author Peter Svihra <peter.svihra@cern.ch>

import libscrc

def commsFromBytes(byteArray):
    comms = CommsFormat()
    comms.copyBytes(byteArray)
    
    return comms

def generateAlarm(payload):
    comms = CommsFormat(info_size = payload.getSize(), address = 0xC0)
    comms.setInformation(payload.getByteArray())
    return comms

def generateCmd(payload):
    comms = CommsFormat(info_size = payload.getSize(), address = 0x80)
    comms.setInformation(payload.getByteArray())
    return comms

def generateData(payload):
    comms = CommsFormat(info_size = payload.getSize(), address = 0x40)
    comms.setInformation(payload.getByteArray())
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

# ACK specific formating
class CommsACK(CommsFormat):
    def __init__(self, address):
        super().__init__(control = [0x00, 0x01], address = address)
        
# NACK specific formating
class CommsNACK(CommsFormat):
    def __init__(self, address):
        super().__init__(control = [0x00, 0x05], address = address)
