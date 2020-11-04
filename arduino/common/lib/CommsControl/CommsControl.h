// © Copyright CERN, Riga Technical University and University of Liverpool 2020.
// All rights not expressly granted are reserved. 
// 
// This file is part of hev-sw.
// 
// hev-sw is free software: you can redistribute it and/or modify it under
// the terms of the GNU General Public Licence as published by the Free
// Software Foundation, either version 3 of the Licence, or (at your option)
// any later version.
// 
// hev-sw is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public Licence
// for more details.
// 
// You should have received a copy of the GNU General Public License along
// with hev-sw. If not, see <http://www.gnu.org/licenses/>.
// 
// The authors would like to acknowledge the much appreciated support
// of all those involved with the High Energy Ventilator project
// (https://hev.web.cern.ch/).


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

    uint32_t countDroppedSend()    { return _dropped_send   ; }
    uint32_t countDroppedReceive() { return _dropped_receive; }
    uint8_t  countBufferSize(PRIORITY type) { return getQueue(type)->size(); }

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
    uint32_t    _dropped_send = 0;
    uint32_t    _dropped_receive = 0;
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
