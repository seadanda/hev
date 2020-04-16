#ifndef COMMSCONSTANTS_H
#define COMMSCONSTANTS_H

#include <Arduino.h>

#define CONST_TIMEOUT_ALARM 5
#define CONST_TIMEOUT_DATA  10
#define CONST_TIMEOUT_CMD   50


#define CONST_MAX_SIZE_RB_RECEIVING 10
#define CONST_MAX_SIZE_RB_SENDING 5
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

#define HEV_FORMAT_VERSION 0xA0

enum command_codes {CMD_START = 1,
                    CMD_STOP  = 2};

// Taken from safety doc. Correct as of 1400 on 20200416
enum alarm_codes {APNEA                          = 1,   // HP
                  CHECK_VALVE_EXHALE             = 2,   // HP
                  CHECK_P_PATIENT                = 3,   // HP
                  EXPIRATION_SENSE_FAULT_OR_LEAK = 4,   //  MP
                  EXPIRATION_VALVE_Leak          = 5,   //  MP
                  HIGH_FIO2                      = 6,   //  MP
                  HIGH_PRESSURE                  = 7,   // HP
                  HIGH_RR                        = 8,   //  MP
                  HIGH_VTE                       = 9,   //  MP
                  LOW_VTE                        = 10,  //  MP
                  HIGH_VTI                       = 11,  //  MP
                  LOW_VTI                        = 12,  //  MP
                  INTENTIONAL_STOP               = 13,  // HP
                  LOW_BATTERY                    = 14,  // HP (LP) if AC power isn't (is) connected
                  LOW_FIO2                       = 15,  // HP
                  OCCLUSION                      = 16,  // HP
                  HIGH_PEEP                      = 17,  // HP
                  LOW_PEEP                       = 18,  // HP
                  AC_POWER_DISCONNECTION         = 19,  //  MP
                  BATTERY_FAULT_SRVC             = 20,  //  MP
                  BATTERY_CHARGE                 = 21,  //  MP
                  AIR_FAIL                       = 22,  // HP
                  O2_FAIL                        = 23,  // HP
                  PRESSURE_SENSOR_FAULT          = 24,  // HP
                  ARDUINO_FAIL                   = 25}; // HP

// struct for all data sent
struct dataFormat {
    uint8_t  version = HEV_FORMAT_VERSION; //
    uint8_t  fsm_state = 0;
    uint16_t pressure_air_supply = 0;
    uint16_t pressure_air_regulated = 0;
    uint16_t pressure_o2_supply = 0;
    uint16_t pressure_o2_regulated = 0;
    uint16_t pressure_buffer = 0;
    uint16_t pressure_inhale = 0;
    uint16_t pressure_patient = 0;
    uint16_t temperature_buffer = 0;
    uint16_t pressure_diff_patient = 0;
    uint8_t  readback_valve_air_in = 0;
    uint8_t  readback_valve_o2_in = 0;
    uint8_t  readback_valve_inhale = 0;
    uint8_t  readback_valve_exhale = 0;
    uint8_t  readback_valve_purge = 0;
    uint8_t  readback_mode = 0;
};

struct cmdFormat {
    uint8_t  version = HEV_FORMAT_VERSION; //
    uint8_t  cmdCode = 0;
    uint32_t  param   = 0;
};

struct alarmFormat{
    uint8_t  version = HEV_FORMAT_VERSION; //
    uint8_t  alarmCode = 0;
    uint32_t param   = 0;
                    // do we do the same as dataFormat and put all alarms in one message?
};

// enum of all transfer types
enum payloadType {
    payloadData,
    payloadCmd,
    payloadAlarm,
    payloadUnset
};

// payload consists of type and information
// type is set as address in the protocol
// information is set as information in the protocol
class payload {
public:
    payload(payloadType type = payloadType::payloadUnset)  {type_ = type; } //data_ = nullptr; cmd_ = nullptr; alarm_ = nullptr; }
    payload(const payload &other) {
        type_ = other.type_;
        memcpy(& data_, &other. data_, sizeof( dataFormat));
        memcpy(&  cmd_, &other.  cmd_, sizeof(  cmdFormat));
        memcpy(&alarm_, &other.alarm_, sizeof(alarmFormat));
    }
    payload& operator=(const payload& other) {
        type_ = other.type_;
        memcpy(& data_, &other. data_, sizeof( dataFormat));
        memcpy(&  cmd_, &other.  cmd_, sizeof(  cmdFormat));
        memcpy(&alarm_, &other.alarm_, sizeof(alarmFormat));
        return *this;
    }

    ~payload() { unsetAll(); }

    void setType(payloadType type) { type_ = type; }
    payloadType getType() {return type_; }

    // requires argument as new struct
    void setData (dataFormat   *data) { type_ = payloadType::payloadData;  memcpy(& data_,  data, sizeof( dataFormat)); }
    void setCmd  (cmdFormat     *cmd) { type_ = payloadType::payloadCmd;   memcpy(&  cmd_,   cmd, sizeof(  cmdFormat)); }
    void setAlarm(alarmFormat *alarm) { type_ = payloadType::payloadAlarm; memcpy(&alarm_, alarm, sizeof(alarmFormat)); }

    // get pointers to particular payload types
    dataFormat  *getData () {return & data_; }
    cmdFormat   *getCmd  () {return &  cmd_; }
    alarmFormat *getAlarm() {return &alarm_; }

    void unsetAll()   { unsetData(); unsetAlarm(); unsetCmd(); type_ = payloadType::payloadUnset; }
    void unsetData()  { memset(& data_, 0, sizeof( dataFormat)); }
    void unsetCmd()   { memset(&  cmd_, 0, sizeof(  cmdFormat)); }
    void unsetAlarm() { memset(&alarm_, 0, sizeof(alarmFormat)); }

    void setPayload(payloadType type, void* information) {
        setType(type);
        setInformation(information);
    }

    void setInformation(void* information) {
        switch (type_) {
            case payloadType::payloadData:
                setData (reinterpret_cast< dataFormat*>(information));
                break;
            case payloadType::payloadCmd:
                setCmd  (reinterpret_cast<  cmdFormat*>(information));
                break;
            case payloadType::payloadAlarm:
                setAlarm(reinterpret_cast<alarmFormat*>(information));
                break;
            default:
                break;
        }
    }

    // returns void pointer, in case you know what to do with data or dont care what the format is
    void *getInformation() {
        switch (type_) {
            case payloadType::payloadData:
                return reinterpret_cast<void*>(getData ());
            case payloadType::payloadCmd:
                return reinterpret_cast<void*>(getCmd  ());
            case payloadType::payloadAlarm:
                return reinterpret_cast<void*>(getAlarm());
            default:
                return nullptr;
        }
    }

    // returns payload information size
    uint8_t getSize()  {
        switch (type_) {
            case payloadType::payloadData:
                return static_cast<uint8_t>(sizeof( dataFormat));
            case payloadType::payloadCmd:
                return static_cast<uint8_t>(sizeof(  cmdFormat));
            case payloadType::payloadAlarm:
                return static_cast<uint8_t>(sizeof(alarmFormat));
            default:
                return 0;
        }
    }

private:
    payloadType type_;

    dataFormat   data_;
    cmdFormat     cmd_;
    alarmFormat alarm_;
};

#endif
