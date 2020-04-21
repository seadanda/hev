#ifndef COMMSCONSTANTS_H
#define COMMSCONSTANTS_H

#include <Arduino.h>

#define CONST_TIMEOUT_ALARM 5
#define CONST_TIMEOUT_DATA  10
#define CONST_TIMEOUT_CMD   50


#define CONST_MAX_SIZE_RB_RECEIVING 2
#define CONST_MAX_SIZE_RB_SENDING 2
#define CONST_MAX_SIZE_PACKET 64
#define CONST_MAX_SIZE_BUFFER 128
#define CONST_MIN_SIZE_PACKET 7

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

#define HEV_FORMAT_VERSION 0xA1

// struct for all data sent
#pragma pack(1)
struct data_format {
    uint8_t  version                = HEV_FORMAT_VERSION;
    uint32_t timestamp              = 0;
    uint8_t  fsm_state              = 0;
    uint16_t pressure_air_supply    = 0;
    uint16_t pressure_air_regulated = 0;
    uint16_t pressure_o2_supply     = 0;
    uint16_t pressure_o2_regulated  = 0;
    uint16_t pressure_buffer        = 0;
    uint16_t pressure_inhale        = 0;
    uint16_t pressure_patient       = 0;
    uint16_t temperature_buffer     = 0;
    uint16_t pressure_diff_patient  = 0;
    uint8_t  readback_valve_air_in  = 0;
    uint8_t  readback_valve_o2_in   = 0;
    uint8_t  readback_valve_inhale  = 0;
    uint8_t  readback_valve_exhale  = 0;
    uint8_t  readback_valve_purge   = 0;
    uint8_t  readback_mode          = 0;
};
#pragma pack()

#pragma pack(1)
struct cmd_format {
    uint8_t  version   = HEV_FORMAT_VERSION;
    uint32_t timestamp = 0;
    uint8_t  cmd_type  = 0;
    uint8_t  cmd_code  = 0;
    uint32_t param     = 0;
};
#pragma pack()

#pragma pack(1)
struct alarm_format {
    uint8_t  version    = HEV_FORMAT_VERSION;
    uint32_t timestamp  = 0;
    uint8_t  alarm_type = 0;
    uint8_t  alarm_code = 0;
    uint32_t param      = 0;
};
#pragma pack()

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
    Payload(PAYLOAD_TYPE type = PAYLOAD_TYPE::UNSET)  {_type = type; } //data_ = nullptr; cmd_ = nullptr; alarm_ = nullptr; }
    Payload(const Payload &other) {
        _type = other._type;
        memcpy(& _data, &other. _data, sizeof( data_format));
        memcpy(&  _cmd, &other.  _cmd, sizeof(  cmd_format));
        memcpy(&_alarm, &other._alarm, sizeof(alarm_format));
    }
    Payload& operator=(const Payload& other) {
        _type = other._type;
        memcpy(& _data, &other. _data, sizeof( data_format));
        memcpy(&  _cmd, &other.  _cmd, sizeof(  cmd_format));
        memcpy(&_alarm, &other._alarm, sizeof(alarm_format));
        return *this;
    }

    ~Payload() { unsetAll(); }

    void setType(PAYLOAD_TYPE type) { _type = type; }
    PAYLOAD_TYPE getType() {return _type; }

    // requires argument as new struct
    void setData (data_format   *data) { _type = PAYLOAD_TYPE::DATA;  memcpy(& _data,  data, sizeof( data_format)); }
    void setCmd  (cmd_format     *cmd) { _type = PAYLOAD_TYPE::CMD;   memcpy(&  _cmd,   cmd, sizeof(  cmd_format)); }
    void setAlarm(alarm_format *alarm) { _type = PAYLOAD_TYPE::ALARM; memcpy(&_alarm, alarm, sizeof(alarm_format)); }

    // get pointers to particular payload types
    data_format  *getData () {return & _data; }
    cmd_format   *getCmd  () {return &  _cmd; }
    alarm_format *getAlarm() {return &_alarm; }

    void unsetAll()   { unsetData(); unsetAlarm(); unsetCmd(); _type = PAYLOAD_TYPE::UNSET; }
    void unsetData()  { memset(& _data, 0, sizeof( data_format)); }
    void unsetCmd()   { memset(&  _cmd, 0, sizeof(  cmd_format)); }
    void unsetAlarm() { memset(&_alarm, 0, sizeof(alarm_format)); }

    void setPayload(PAYLOAD_TYPE type, void* information) {
        setType(type);
        setInformation(information);
    }

    void setInformation(void* information) {
        switch (_type) {
            case PAYLOAD_TYPE::DATA:
                setData (reinterpret_cast< data_format*>(information));
                break;
            case PAYLOAD_TYPE::CMD:
                setCmd  (reinterpret_cast<  cmd_format*>(information));
                break;
            case PAYLOAD_TYPE::ALARM:
                setAlarm(reinterpret_cast<alarm_format*>(information));
                break;
            default:
                break;
        }
    }

    // returns void pointer, in case you know what to do with data or dont care what the format is
    void *getInformation() {
        switch (_type) {
            case PAYLOAD_TYPE::DATA:
                return reinterpret_cast<void*>(getData ());
            case PAYLOAD_TYPE::CMD:
                return reinterpret_cast<void*>(getCmd  ());
            case PAYLOAD_TYPE::ALARM:
                return reinterpret_cast<void*>(getAlarm());
            default:
                return nullptr;
        }
    }

    // returns payload information size
    uint8_t getSize()  {
        switch (_type) {
            case PAYLOAD_TYPE::DATA:
                return static_cast<uint8_t>(sizeof( data_format));
            case PAYLOAD_TYPE::CMD:
                return static_cast<uint8_t>(sizeof(  cmd_format));
            case PAYLOAD_TYPE::ALARM:
                return static_cast<uint8_t>(sizeof(alarm_format));
            default:
                return 0;
        }
    }

private:
    PAYLOAD_TYPE _type;

    data_format   _data;
    cmd_format     _cmd;
    alarm_format _alarm;
};

#endif
