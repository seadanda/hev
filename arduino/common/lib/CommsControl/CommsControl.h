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
    RingBuf<CommsFormat, COMMS_MAX_SIZE_RB_SENDING> *getQueue(PRIORITY &type);
    PRIORITY getInfoType(uint8_t &address);

    bool sendQueue(RingBuf<CommsFormat, COMMS_MAX_SIZE_RB_SENDING> *queue);
    void resendPacket ();
    void resetPacket  ();
    void trackMismatch(uint8_t sequence_receive);
    void resetReceiver(uint8_t sequence_receive = 0xFF);
    bool receivePacket(PRIORITY &type);
    void finishPacket (uint8_t &sequence_received);

    bool encoder(uint8_t* payload, uint8_t data_size);
    bool decoder(uint8_t* payload, uint8_t dataStart, uint8_t data_stop);

    void sendPacket(CommsFormat &packet);

private:
    uint8_t _sequence_send;
    uint8_t _sequence_receive;

    CommsFormat _comms_ack;
    CommsFormat _comms_nck;

    uint8_t     _mismatch_counter = 0;
    CommsFormat _packet;
    uint8_t     _packet_retries = 0;
    bool        _packet_set = false;
    RingBuf<CommsFormat, COMMS_MAX_SIZE_RB_SENDING> _ring_buff_alarm;
    RingBuf<CommsFormat, COMMS_MAX_SIZE_RB_SENDING> _ring_buff_data;
    RingBuf<CommsFormat, COMMS_MAX_SIZE_RB_SENDING> _ring_buff_cmd;

    RingBuf<Payload, COMMS_MAX_SIZE_RB_RECEIVING> _ring_buff_received;

    Payload     _payload_tmp;
    CommsFormat _comms_tmp;

    uint32_t _baudrate;

    uint32_t _last_trans_time;

    uint8_t _comms_received[COMMS_MAX_SIZE_BUFFER];
    uint8_t _comms_received_size;
    uint8_t _comms_send    [COMMS_MAX_SIZE_BUFFER];
    uint8_t _comms_send_size;

    uint8_t _last_trans[COMMS_MAX_SIZE_BUFFER];
    uint8_t _start_trans_index;
    uint8_t _last_trans_index;

    bool _found_start;
};

#endif
