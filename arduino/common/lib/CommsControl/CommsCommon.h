#ifndef COMMSCONSTANTS_H
#define COMMSCONSTANTS_H

#include <Arduino.h>

#define CONST_TIMEOUT_ALARM 5
#define CONST_TIMEOUT_DATA  10
#define CONST_TIMEOUT_CMD   50

#define PAYLOAD_MAX_SIZE_BUFFER 64

// UNO struggles with the RAM size for ring buffers
#ifdef ARDUINO_AVR_UNO
#define COMMS_MAX_SIZE_RB_RECEIVING  1
#define COMMS_MAX_SIZE_RB_SENDING    1
#else
#define COMMS_MAX_SIZE_RB_RECEIVING 10
#define COMMS_MAX_SIZE_RB_SENDING    5
#endif

#define COMMS_MAX_SIZE_PACKET 64
#define COMMS_MAX_SIZE_BUFFER 128
#define COMMS_MIN_SIZE_PACKET 7

#define COMMS_FRAME_BOUNDARY 0x7E
#define COMMS_FRAME_ESCAPE   0x7D
#define COMMS_ESCAPE_BIT_SWAP 5

#define COMMS_CONTROL_INFORMATION 0x00
#define COMMS_CONTROL_SUPERVISORY 0x01

#define COMMS_CONTROL_TYPES 0x0F
#define COMMS_CONTROL_ACK   0x00 | COMMS_CONTROL_SUPERVISORY
#define COMMS_CONTROL_NACK  0x04 | COMMS_CONTROL_SUPERVISORY

#define PACKET_TYPE  0xC0
#define PACKET_ALARM 0xC0
#define PACKET_CMD   0x80
#define PACKET_DATA  0x40
#define PACKET_SET   0x20 //set vs get ?

// enum of all transfer types
enum PAYLOAD_TYPE {
    DATA,
    CMD,
    ALARM,
    UNSET
};

// payload consists of type and information
// type is set as address in the protocol
// information is set as information in the protocol
class Payload {
public:
    Payload(PAYLOAD_TYPE type = PAYLOAD_TYPE::UNSET)  {_type = type; }
    Payload(const Payload &other) {
        _type = other._type;
        _size = other._size;
        memcpy(_buffer, other._buffer, other._size);
    }
    Payload& operator=(const Payload& other) {
        _type = other._type;
        _size = other._size;
        memcpy(_buffer, other._buffer, other._size);
        return *this;
    }

    ~Payload() { unset(); }
    void unset() { memset( _buffer, 0, PAYLOAD_MAX_SIZE_BUFFER); _type = PAYLOAD_TYPE::UNSET; _size = 0;}

    void setType(PAYLOAD_TYPE type) { _type = type; }
    PAYLOAD_TYPE getType() {return _type; }

    void setSize(uint8_t size) { _size = size; }
    uint8_t getSize() { return _size; }

    bool setPayload(PAYLOAD_TYPE type, void* information, uint8_t size) {
        if (information == nullptr) {
            return false;
        }

        setType(type);
        setSize(size);
        setInformation(information);

        return true;
    }

    bool getPayload(void* information) {
        PAYLOAD_TYPE type;
        uint8_t size;
        return getPayload(information, type, size);
    }

    bool getPayload(void* information, PAYLOAD_TYPE &type, uint8_t &size) {
        if (information == nullptr) {
            return false;
        }

        type = getType();
        size = getSize();
        memcpy(information, getInformation(), _size);

        return true;
    }

    void setInformation(void* information) { memcpy(_buffer, information, _size); }
    void *getInformation() { return reinterpret_cast<void*>(_buffer); }

private:
    PAYLOAD_TYPE _type;
    uint8_t      _buffer[PAYLOAD_MAX_SIZE_BUFFER];
    uint8_t      _size;
};

#endif
