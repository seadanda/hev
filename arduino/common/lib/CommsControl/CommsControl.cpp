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


#include "CommsControl.h"

CommsControl::CommsControl(uint32_t baudrate) {
    _baudrate = baudrate;

    _last_trans_time = static_cast<uint32_t>(millis());

    _start_trans_index   = 0xFF;
    _last_trans_index    = 0;
    _comms_received_size = 0;
    _comms_send_size     = 0;
    _found_start = false;

    memset(_last_trans    , 0, sizeof(_last_trans    ));
    memset(_comms_received, 0, sizeof(_comms_received));
    memset(_comms_send    , 0, sizeof(_comms_send    ));

    CommsFormat::generateACK(_comms_ack);
    CommsFormat::generateNACK(_comms_nck);

    _sequence_send    = 0;
    _sequence_receive = 0;
}

CommsControl::~CommsControl() {
    ;
}

void CommsControl::beginSerial() {
    Serial.begin(_baudrate);
}

// main function to always call and try and send data
// _last_trans_time is changed when transmission occurs in sendQueue
void CommsControl::sender() {
    if (static_cast<uint32_t>(millis()) - _last_trans_time > CONST_TIMEOUT_TRANSFER) {
        if (_packet_set) {
            resendPacket();
        } else {
            if      (sendQueue(&_ring_buff_alarm)) { ; }
            else if (sendQueue(&_ring_buff_cmd  )) { ; }
            else if (sendQueue(&_ring_buff_data )) { ; }
        }
    }
}

// main function to always try to receive data
// TODO: needs switch on data type with global timeouts on data pushing
void CommsControl::receiver() {
    uint8_t current_trans_index;

    // check if any data in waiting
    if (Serial.available()) {
        // while able to read data (unable == -1)
        while (Serial.peek() >= 0) {
            // read byte by byte, just in case the transmission is somehow blocked

            // WARNING: for mkrvidor4000, readbytes takes char* not uchar*
            _last_trans_index += Serial.readBytes(_last_trans + _last_trans_index, 1);

            // if managed to read at least 1 byte
            if (_last_trans_index > 0 && _last_trans_index < COMMS_MAX_SIZE_BUFFER - 1) {
                current_trans_index = _last_trans_index - 1;

                // find the boundary of frames
                if (_last_trans[current_trans_index] == COMMS_FRAME_BOUNDARY) {
                    // if not found start or if read the same byte as last time or if read a random end first
                    if (!_found_start || current_trans_index < _start_trans_index + 6 ) {
                        _found_start = true;
                        _start_trans_index = current_trans_index;
                    } else {
                        // if managed to decode and compare CRC
                        if (decoder(_last_trans, _start_trans_index, _last_trans_index)) {

                            uint8_t sequence_received = _comms_tmp.getSequenceReceive();
                            // to decide ACK/NACK/other; for other gain sequenceReceive
                            uint8_t control = *(_comms_tmp.getControl() + 1);
                            uint8_t address = *_comms_tmp.getAddress();

                            // to decide what kind of packets received
                            PRIORITY type = getInfoType(address);

                            // switch on received data to know what to do - received ACK/NACK or other
                            switch(control & COMMS_CONTROL_TYPES) {
                                case COMMS_CONTROL_NACK:
                                    // received NACK
                                    break;
                                case COMMS_CONTROL_ACK:
                                    // received ACK
                                    finishPacket(sequence_received);
                                    break;
                                default:
                                    // received INFORMATION
                                    uint8_t sequence = _comms_tmp.getSequenceSend();
                                    CommsFormat * response = &_comms_ack;

                                    // check counters
                                    if (_sequence_receive != sequence) {
                                        trackMismatch(sequence);
                                        response = &_comms_nck;
                                    } else {
                                        resetReceiver(sequence + 1);
                                    }

                                    // check proper unpacking
                                    if(!receivePacket(type)) {
                                        response = &_comms_nck;
                                    }
                                    response->setAddress(&address);
                                    response->setSequenceReceive(_sequence_receive);
                                    sendPacket(*response);
                                    break;
                            }
                        }

                        // reset the frame
                        _found_start = false;
                        _last_trans_index = 0;
                        _start_trans_index = 0xFF;

                        // break the loop, even if more data waiting in the bus - this frame is finished
                        break;
                    }
                }
            } else if (_last_trans_index >= COMMS_MAX_SIZE_BUFFER - 1) {
                _last_trans_index = 0;
            }
        }
    } 
}

bool CommsControl::writePayload(Payload &pl) {
    PRIORITY payload_type = pl.getType();
    if (payload_type != PRIORITY::UNSET_ADDR) {
        // create comms format using payload, the type is deduced from the payload itself
        CommsFormat comms = CommsFormat(pl);

        RingBuf<CommsFormat, COMMS_MAX_SIZE_RB_SENDING> *queue = getQueue(payload_type);
        // add new entry to the queue
        if (queue->isFull()) {
            CommsFormat comms_rm;
            if (queue->pop(comms_rm)) {
                _dropped_send++;
            }
        }

        if (queue->push(comms) ) {
            return true;
        }
    }
    return false;
}

bool CommsControl::readPayload( Payload &pl) {
    if ( !_ring_buff_received.isEmpty()) {
        if (_ring_buff_received.pop(pl)) {
            return true;
        }
    }
    return false;
}

// general encoder of any transmission
bool CommsControl::encoder(uint8_t *data, uint8_t data_size) {
    if (data_size > 0) {
        _comms_send_size = 0;
        uint8_t tmpVal = 0;

        _comms_send[_comms_send_size++] = data[0];
        for (uint8_t idx = 1; idx < data_size - 1; idx++) {
            tmpVal = data[idx];
            if (tmpVal == COMMS_FRAME_ESCAPE || tmpVal == COMMS_FRAME_BOUNDARY) {
                _comms_send[_comms_send_size++] = COMMS_FRAME_ESCAPE;
                tmpVal ^= (1 << COMMS_ESCAPE_BIT_SWAP);
            }
            _comms_send[_comms_send_size++] = tmpVal;
        }
        _comms_send[_comms_send_size++] = data[data_size-1];

        return true;
    }
    return false;
}

// general decoder of any transmission
bool CommsControl::decoder(uint8_t* data, uint8_t data_start, uint8_t data_stop) {
    // need to have more than 1 byte transferred
    if (data_stop > (data_start + 1)) {
        _comms_received_size = 0;
        uint8_t tmp_val = 0;
        bool escaped = false;

        for (uint8_t idx = data_start; idx < data_stop; idx++) {
            tmp_val = data[idx];
            if (tmp_val == COMMS_FRAME_ESCAPE) {
                escaped = true;
            } else {
                if (escaped) {
                    tmp_val ^= (1 << COMMS_ESCAPE_BIT_SWAP);
                    escaped = false;
                }
                _comms_received[_comms_received_size++] = tmp_val;
            }
        }
        _comms_tmp.copyData(_comms_received, _comms_received_size);
        return _comms_tmp.compareCrc();
    }
    return false;
}

// sending anything of commsDATA format
bool CommsControl::sendQueue(RingBuf<CommsFormat, COMMS_MAX_SIZE_RB_SENDING> *queue) {
    // if have data to send
    if (!queue->isEmpty()) {
        _packet_set = queue->pop(_packet);
        if (_packet_set) {
            _packet.setSequenceSend(_sequence_send);
            sendPacket(_packet);
        }
    }
    return _packet_set;
}

void CommsControl::sendPacket(CommsFormat &packet) {
    // reset sending counter
    _last_trans_time = static_cast<uint32_t>(millis());

    // if encoded and able to write data
    if (encoder(packet.getData(), packet.getSize()) ) {
        if (Serial.availableForWrite() >= _comms_send_size) {
            Serial.write(_comms_send, _comms_send_size);
        }
    }
}

void CommsControl::resendPacket() {
    if ((++_packet_retries) < CONST_PACKET_RETRIES) {
        sendPacket(_packet);
    } else {
        resetPacket();
    }
}

void CommsControl::trackMismatch(uint8_t sequence_receive) {
    if (_mismatch_counter++ > CONST_MISMATCH_COUNTER) {
        resetReceiver(sequence_receive);
    }
}

void CommsControl::resetReceiver(uint8_t sequence_receive) {
    _mismatch_counter = 0;
    if (sequence_receive != 0xFF) {
        _sequence_receive = (sequence_receive & 0x7F);
    }
}

void CommsControl::resetPacket() {
    _packet_set = false;
    _packet_retries = 0;
}

// receiving anything of commsFormat
bool CommsControl::receivePacket(PRIORITY &type) {
    _payload_tmp.unset();
    _payload_tmp.setPayload(type, reinterpret_cast<void *>(_comms_tmp.getInformation()), _comms_tmp.getInfoSize());

    // remove first entry if queue is full
    if (_ring_buff_received.isFull()) {
        Payload payload_rm;
        if (_ring_buff_received.pop(payload_rm)) {
            _dropped_receive++;
        }
    }
    return _ring_buff_received.push(_payload_tmp);
}

// if FCS is ok, remove from queue
void CommsControl::finishPacket(uint8_t &sequence_received) {
    // get the sequence send from first entry in the queue, add one as that should be return
    // 0x7F to deal with possible overflows (0 should follow after 127)
    uint8_t sequence = ((_sequence_send + 1) & 0x7F);
    if (sequence == sequence_received) {
        _sequence_send = sequence;
        resetPacket();
    }
}

PRIORITY CommsControl::getInfoType(uint8_t &address) {
    // return enum element corresponding to the address
    return static_cast<PRIORITY>(address & PACKET_TYPE);
}

// get link to queue according to packet format
RingBuf<CommsFormat, COMMS_MAX_SIZE_RB_SENDING> *CommsControl::getQueue(PRIORITY &type) {
    switch (type) {
        case PRIORITY::ALARM_ADDR:
            return &_ring_buff_alarm;
        case PRIORITY::CMD_ADDR:
            return &_ring_buff_cmd;
        case PRIORITY::DATA_ADDR:
            return &_ring_buff_data;
        default:
            return nullptr;
    }
}
