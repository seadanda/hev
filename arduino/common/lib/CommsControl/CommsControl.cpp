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

//    _ring_buff_alarm = RingBuf<CommsFormat, COMMS_MAX_SIZE_RB_SENDING>();
//    _ring_buff_data  = RingBuf<CommsFormat, COMMS_MAX_SIZE_RB_SENDING>();
//    _ring_buff_cmd   = RingBuf<CommsFormat, COMMS_MAX_SIZE_RB_SENDING>();

//    _ring_buff_received = RingBuf<Payload, COMMS_MAX_SIZE_RB_RECEIVING>();

//    _comms_tmp   = CommsFormat(COMMS_MAX_SIZE_PACKET - COMMS_MIN_SIZE_PACKET );

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
    if (static_cast<uint32_t>(millis()) - _last_trans_time > CONST_TIMEOUT_ALARM) {
        sendQueue(&_ring_buff_alarm);
    }

    if (static_cast<uint32_t>(millis()) - _last_trans_time > CONST_TIMEOUT_CMD) {
        sendQueue(&_ring_buff_cmd);
    }

    if (static_cast<uint32_t>(millis()) - _last_trans_time > CONST_TIMEOUT_DATA) {
        sendQueue(&_ring_buff_data);
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
            if (_last_trans_index > 0 && _last_trans_index < COMMS_MAX_SIZE_BUFFER) {
                current_trans_index = _last_trans_index - 1;

                // find the boundary of frames
                if (_last_trans[current_trans_index] == COMMS_FRAME_BOUNDARY) {
                    // if not found start or if read the same byte as last time
                    if (!_found_start || _start_trans_index == current_trans_index) {
                        _found_start = true;
                        _start_trans_index = current_trans_index;
                    } else {
                        // if managed to decode and compare CRC
                        if (decoder(_last_trans, _start_trans_index, _last_trans_index)) {

                            _sequence_receive = (*(_comms_tmp.getControl()) >> 1 ) & 0x7F;
                            // to decide ACK/NACK/other; for other gain sequenceReceive
                            uint8_t control = *(_comms_tmp.getControl() + 1);

                            // to decide what kind of packets received
                            PAYLOAD_TYPE type = getInfoType(_comms_tmp.getAddress());

                            // switch on received data to know what to do - received ACK/NACK or other
                            switch(control & COMMS_CONTROL_TYPES) {
                                case COMMS_CONTROL_NACK:
                                    // received NACK
                                    // TODO: modify timeout for next sent frame?
                                    // resendPacket(&address);
                                    break;
                                case COMMS_CONTROL_ACK:
                                    // received ACK
                                    finishPacket(type);
                                    break;
                                default:
                                    Serial.print("add: ");
                                    uint8_t sequence_receive = (control >> 1 ) & 0x7F;
                                    sequence_receive += 1;
                                    uint8_t address = *_comms_tmp.getAddress();
                                    // received DATA
                                    if (receivePacket(type)) {
                                        _comms_ack.setAddress(&address);
                                        Serial.println(*_comms_ack.getAddress());
                                        _comms_ack.setSequenceReceive(sequence_receive);
                                        sendPacket(_comms_ack);
                                    } else {
                                        _comms_nck.setAddress(&address);
                                        _comms_nck.setSequenceReceive(sequence_receive);
                                        sendPacket(_comms_nck);
                                    }

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
            } else if (_last_trans_index >= COMMS_MAX_SIZE_BUFFER) {
                _last_trans_index = 0;
            }
        }
    } 
}

bool CommsControl::writePayload(Payload &pl) {
    PAYLOAD_TYPE payload_type = pl.getType();
    if (payload_type != PAYLOAD_TYPE::UNSET) {
        // create comms format using payload, the type is deduced from the payload itself
        CommsFormat comms = CommsFormat(pl);

        RingBuf<CommsFormat, COMMS_MAX_SIZE_RB_SENDING> *queue = getQueue(payload_type);
        // add new entry to the queue
        if (queue->isFull()) {
            CommsFormat comms_rm;
            if (queue->pop(comms_rm)) {
                ;
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
void CommsControl::sendQueue(RingBuf<CommsFormat, COMMS_MAX_SIZE_RB_SENDING> *queue) {
    // if have data to send
    if (!queue->isEmpty()) {
        queue->operator [](0).setSequenceSend(_sequence_send);
        sendPacket(queue->operator [](0));

        // reset sending counter
        _last_trans_time = static_cast<uint32_t>(millis());
    }
}

void CommsControl::sendPacket(CommsFormat &packet) {
    // if encoded and able to write data
    if (encoder(packet.getData(), packet.getSize()) ) {
        if (Serial.availableForWrite() >= _comms_send_size) {
            Serial.write(_comms_send, _comms_send_size);
        } 
    }
}

// resending the packet, can lower the timeout since either NACK or wrong FCS already checked
//WIP
void CommsControl::resendPacket(RingBuf<CommsFormat, COMMS_MAX_SIZE_RB_SENDING> *queue) {
    ;
}


// receiving anything of commsFormat
bool CommsControl::receivePacket(PAYLOAD_TYPE &type) {
    _payload_tmp.unset();
    _payload_tmp.setPayload(type, _comms_tmp.getInformation(), _comms_tmp.getInfoSize());

    // remove first entry if queue is full
    if (_ring_buff_received.isFull()) {
        Payload payload_rm;
        if (_ring_buff_received.pop(payload_rm)) {
            ;
        }
    }
    return _ring_buff_received.push(_payload_tmp);
}

// if FCS is ok, remove from queue
void CommsControl::finishPacket(PAYLOAD_TYPE &type) {
    RingBuf<CommsFormat, COMMS_MAX_SIZE_RB_SENDING> *queue = getQueue(type);

    if (queue != nullptr && !queue->isEmpty()) {
        // get the sequence send from first entry in the queue, add one as that should be return
        // 0x7F to deal with possible overflows (0 should follow after 127)
        if (((queue->operator [](0).getSequenceSend() + 1) & 0x7F) ==  _sequence_receive) {
            _sequence_send = (_sequence_send + 1) % 128;
            CommsFormat comms_rm;
            if (queue->pop(comms_rm)) {
                ;
            }
        }
    }
}

PAYLOAD_TYPE CommsControl::getInfoType(uint8_t *address) {
    switch (*address & PACKET_TYPE) {
        case PACKET_ALARM:
            return PAYLOAD_TYPE::ALARM;
        case PACKET_CMD:
            return PAYLOAD_TYPE::CMD;
        case PACKET_DATA:
            return PAYLOAD_TYPE::DATA;
        default:
            return PAYLOAD_TYPE::UNSET;
    }
}

// get link to queue according to packet format
RingBuf<CommsFormat, COMMS_MAX_SIZE_RB_SENDING> *CommsControl::getQueue(PAYLOAD_TYPE &type) {
    switch (type) {
        case PAYLOAD_TYPE::ALARM:
            return &_ring_buff_alarm;
        case PAYLOAD_TYPE::CMD:
            return &_ring_buff_cmd;
        case PAYLOAD_TYPE::DATA:
            return &_ring_buff_data;
        default:
            return nullptr;
    }
}
