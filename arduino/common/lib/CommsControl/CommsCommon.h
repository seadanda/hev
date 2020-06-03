#ifndef COMMSCONSTANTS_H
#define COMMSCONSTANTS_H

#include <Arduino.h>

#define COSNT_TIMEOUT_TRANSFER 5
#define CONST_PACKET_RETRIES 10
#define CONST_MISMATCH_COUNTER 20

#define PAYLOAD_MAX_SIZE_BUFFER 128

// UNO struggles with the RAM size for ring buffers
#ifdef ARDUINO_AVR_UNO
#define COMMS_MAX_SIZE_RB_RECEIVING  1
#define COMMS_MAX_SIZE_RB_SENDING    1
#else
#define COMMS_MAX_SIZE_RB_RECEIVING 10
#define COMMS_MAX_SIZE_RB_SENDING   15
#endif

#define COMMS_MAX_SIZE_PACKET 128
#define COMMS_MAX_SIZE_BUFFER 256
#define COMMS_MIN_SIZE_PACKET 7

#define COMMS_FRAME_BOUNDARY 0x7E
#define COMMS_FRAME_ESCAPE   0x7D
#define COMMS_ESCAPE_BIT_SWAP 5

#define COMMS_CONTROL_INFORMATION 0x00
#define COMMS_CONTROL_SUPERVISORY 0x01

#define COMMS_CONTROL_TYPES 0x0F
#define COMMS_CONTROL_ACK   (0x00 | COMMS_CONTROL_SUPERVISORY)
#define COMMS_CONTROL_NACK  (0x04 | COMMS_CONTROL_SUPERVISORY)

#define PACKET_TYPE  0xC0
#define PACKET_ALARM 0xC0
#define PACKET_CMD   0x80
#define PACKET_DATA  0x40
#define PACKET_SET   0x20 //set vs get ?

// enum of all transfer types
enum PRIORITY : uint8_t {
    DATA_ADDR  = PACKET_DATA,
    CMD_ADDR   = PACKET_CMD,
    ALARM_ADDR = PACKET_ALARM,
    UNSET_ADDR = 0x00
};

// payload consists of type and information
// type is set as address in the protocol
// information is set as information in the protocol
class Payload {
public:
    Payload(PRIORITY type = PRIORITY::UNSET_ADDR)  {_type = type; }
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
    void unset() { memset( _buffer, 0, PAYLOAD_MAX_SIZE_BUFFER); _type = PRIORITY::UNSET_ADDR; _size = 0;}

    void setType(PRIORITY type) { _type = type; }
    PRIORITY getType() {return _type; }

    void setSize(uint8_t size) { _size = size; }
    uint8_t getSize() { return _size; }

    bool setPayload(PRIORITY type, void* information, uint8_t size) {
        if (information == nullptr) {
            return false;
        }

        setType(type);
        setSize(size);
        setInformation(information);

        return true;
    }

    bool getPayload(void* information) {
        PRIORITY type;
        uint8_t size;
        return getPayload(information, type, size);
    }

    bool getPayload(void* information, PRIORITY &type, uint8_t &size) {
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
    PRIORITY _type;
    uint8_t      _buffer[PAYLOAD_MAX_SIZE_BUFFER];
    uint8_t      _size;
};

#endif
