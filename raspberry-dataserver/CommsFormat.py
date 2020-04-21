#!/usr/bin/env python3

# Communication protocol based on HDLC format
# author Peter Svihra <peter.svihra@cern.ch>

import libscrc

def commsFromBytes(byteArray):
    comms = CommsFormat()
    comms.copyBytes(byteArray)
    
    return comms

def generateAlarm(payload):
    comms = CommsFormat(infoSize = payload.getSize(), address = 0xC0)
    comms.setInformation(payload)
    return comms

def generateCmd(payload):
    comms = CommsFormat(infoSize = payload.getSize(), address = 0x80)
    comms.setInformation(payload)
    return comms

def generateData(payload):
    comms = CommsFormat(infoSize = payload.getSize(), address = 0x40)
    comms.setInformation(payload)
    return comms


# basic format based on HDLC
class CommsFormat:
    def __init__(self, infoSize = 0, address = 0x00, control = [0x00, 0x00]):
        self._data = bytearray(7 + infoSize)
        self._infoSize = infoSize
        self._crc = None
        
        self.assignBytes(self.getStart()  , bytes([0x7E])   , calcCrc = False)
        self.assignBytes(self.getAddress(), bytes([address]), calcCrc = False)
        self.assignBytes(self.getControl(), bytes(control)  , calcCrc = False)
        self.assignBytes(self.getStop()   , bytes([0x7E])   , calcCrc = False)
        
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
        return 4 + self._infoSize
    def getStop(self):
        return 4 + self._infoSize + 2
    
    def setAddress(self, address):
        self.assignBytes(self.getAddress(), bytes([address]), 1)
        
    def setControl(self, control):
        self.assignBytes(self.getControl(), bytes(control), 2)
    
    def setInformation(self, payload):
        # convert provided value
        self.assignBytes(self.getInformation(), payload.byteArray)
        
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
        
    def assignBytes(self, start, values, calcCrc = True):
        for idx in range(len(values)):
            self._data[start + idx] = values[idx]
        if calcCrc:
            self.generateCrc()
        
    # generate checksum
    def generateCrc(self, assign = True):
        self._crc = libscrc.x25(bytes(self._data[self.getAddress():self.getFcs()])).to_bytes(2, byteorder='little')
        if assign:
            self.assignBytes(self.getFcs(), self._crc, calcCrc = False)
            
    def compareCrc(self):
        self.generateCrc(False)
        fcs = self.getData()[self.getFcs():self.getFcs()+2]
        return self._crc in fcs
    
    
    def getData(self):
        return self._data

    def copyData(self, dataArray):
        self.copyBytes(dataArray.to_bytes(self._infoSize, byteorder='little'))
        
    def copyBytes(self, bytesArray):
        self._infoSize = len(bytesArray) - 7
        self._data     = bytesArray

# ACK specific formating
class CommsACK(CommsFormat):
    def __init__(self, address):
        super().__init__(control = [0x00, 0x01], address = address)
        
# NACK specific formating
class CommsNACK(CommsFormat):
    def __init__(self, address):
        super().__init__(control = [0x00, 0x05], address = address)
