#ifndef COMMSFORMAT_H
#define COMMSFORMAT_H

// Communication protocol based on HDLC format
// author Peter Svihra <peter.svihra@cern.ch>

#include <Arduino.h>
#include <uCRC16Lib.h>

#include "CommsCommon.h"

///////////////////////////////////////////////////////////////////////////
// class to provide all needed control in data format
class CommsFormat {
public:
    CommsFormat(uint8_t infoSize = 0, uint8_t address = 0x00, uint16_t control = 0x0000);
    CommsFormat(const CommsFormat& other) {
        _crc        = other._crc;
        _packet_size = other._packet_size;
        _info_size   = other._info_size;
        memcpy(_data, other._data, CONST_MAX_SIZE_PACKET);
    }
    CommsFormat& operator=(const CommsFormat& other) {
        _crc        = other._crc;
        _packet_size = other._packet_size;
        _info_size   = other._info_size;
        memcpy(_data, other._data, CONST_MAX_SIZE_PACKET);

        return *this;
    }

    uint8_t* getData()    { return _data; }
    uint8_t  getSize()    { return _packet_size; }

    void setAddress(uint8_t* address) {assignBytes(getAddress(), address, 1); }
    void setControl(uint8_t* control) {assignBytes(getControl(), control, 2); }
    void setInformation(Payload *pl);

    void assignBytes(uint8_t* target, uint8_t* source, uint8_t size, bool calcCrc = true);

    void generateCrc(bool assign = true);
    bool compareCrc();

    // get data pointer of different parts
    uint8_t* getStart()       {return _data + 0;}                         // starting flag of the chain
    uint8_t* getAddress()     {return _data + 1;}                         // address where to send data, last bit is 8bit extension enable(0)/disable(1)
    uint8_t* getControl()     {return _data + 2;}                         // frame control commands
    uint8_t* getInformation() {return _data + 4;}                         // user information
    uint8_t* getFcs()         {return _data + 4 + _info_size;}            // checksum
    uint8_t* getStop()        {return _data + 4 + _info_size + 2;}        // ending flag of the chain

    uint8_t getInfoSize() { return _info_size; }

    void setSequenceSend   (uint8_t counter);
    void setSequenceReceive(uint8_t counter);

    uint8_t getSequenceSend   ();
    uint8_t getSequenceReceive();

    void copyData(uint8_t* payload, uint8_t dataSize);

    static CommsFormat* generateACK()   { return new CommsFormat(0, 0, COMMS_CONTROL_ACK  << 8); }
    static CommsFormat* generateNACK()  { return new CommsFormat(0, 0, COMMS_CONTROL_NACK << 8); }

    static CommsFormat* generateALARM(Payload *pl);
    static CommsFormat* generateCMD  (Payload *pl);
    static CommsFormat* generateDATA (Payload *pl);

private:
    uint8_t  _data[CONST_MAX_SIZE_PACKET];
    uint8_t  _packet_size;
    uint8_t  _info_size;
    uint16_t _crc;
};

#endif // COMMSFORMAT_H
