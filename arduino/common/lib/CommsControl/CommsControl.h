#ifndef COMMS_CONTROL_H
#define COMMS_CONTROL_H

// Communication protocol between rasp and arduino based on HDLC format
// author Peter Svihra <peter.svihra@cern.ch>

#include <Arduino.h>
#include "RingBuf.h"

#include "CommsCommon.h"
#include "CommsFormat.h"

///////////////////////////////////////////////////////////////////////////
// class to provide simple communication protocol based on the data format
class CommsControl {
public:
    CommsControl(uint32_t baudrate = 115200);
    ~CommsControl();

    void beginSerial();

    bool writePayload(Payload &pl);
    bool readPayload (Payload &pl);

    void sender();
    void receiver();

private:
    RingBuf<CommsFormat *,CONST_MAX_SIZE_RB_SENDING> *getQueue(PAYLOAD_TYPE &type);
    PAYLOAD_TYPE getInfoType(uint8_t *address);

    void sendQueue    (RingBuf<CommsFormat *, CONST_MAX_SIZE_RB_SENDING> *queue);
    void resendPacket (RingBuf<CommsFormat *, CONST_MAX_SIZE_RB_SENDING> *queue);
    bool receivePacket(PAYLOAD_TYPE &type);
    void finishPacket (PAYLOAD_TYPE &type);

    bool encoder(uint8_t* payload, uint8_t dataSize);
    bool decoder(uint8_t* payload, uint8_t dataStart, uint8_t dataStop);

    void sendPacket(CommsFormat* packet);

private:
    uint8_t _sequence_send;
    uint8_t _sequence_receive;

    CommsFormat* _comms_ack;
    CommsFormat* _comms_nck;

    RingBuf<CommsFormat *, CONST_MAX_SIZE_RB_SENDING> *_ring_buff_alarm;
    RingBuf<CommsFormat *, CONST_MAX_SIZE_RB_SENDING> *_ring_buff_data;
    RingBuf<CommsFormat *, CONST_MAX_SIZE_RB_SENDING> *_ring_buff_cmd;

    RingBuf<Payload, CONST_MAX_SIZE_RB_RECEIVING> *_ring_buff_received;

    Payload     _payload_tmp;
    CommsFormat _comms_tmp;

    uint32_t _baudrate;

    uint64_t _last_trans_time;

    uint8_t _comms_received[CONST_MAX_SIZE_BUFFER];
    uint8_t _comms_received_size;
    uint8_t _comms_send    [CONST_MAX_SIZE_BUFFER];
    uint8_t _comms_send_size;

    uint8_t _last_trans[CONST_MAX_SIZE_BUFFER];
    uint8_t _start_trans_index;
    uint8_t _last_trans_index;

    bool _found_start;
};

#endif
