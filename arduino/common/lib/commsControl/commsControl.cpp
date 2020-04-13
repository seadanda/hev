#include "commsControl.h"

commsControl::commsControl(uint32_t baudrate) {
    baudrate_ = baudrate;

    lastTransTime_ = millis();

    startTransIndex_   = 0xFF;
    lastTransIndex_    = 0;
    commsReceivedSize_ = 0;
    commsSendSize_     = 0;
    foundStart_ = false;

    memset(lastTrans_    , 0, sizeof(lastTrans_    ));
    memset(commsReceived_, 0, sizeof(commsReceived_));
    memset(commsSend_    , 0, sizeof(commsSend_    ));

    queueAlarm_ = new RingBuf<commsFormat *, CONST_MAX_SIZE_RB_SENDING>();
    queueData_  = new RingBuf<commsFormat *, CONST_MAX_SIZE_RB_SENDING>();
    queueCmd_   = new RingBuf<commsFormat *, CONST_MAX_SIZE_RB_SENDING>();

    queueReceived_ = new RingBuf<payload, CONST_MAX_SIZE_RB_RECEIVING>();

    commsTmp_   = commsFormat(CONST_MAX_SIZE_PACKET - CONST_MIN_SIZE_PACKET );

    commsAck_ = commsFormat::generateACK();
    commsNck_ = commsFormat::generateNACK();

    sequenceSend_    = 0;
    sequenceReceive_ = 0;
}

// WIP
commsControl::~commsControl() {
    ;
}

void commsControl::beginSerial() {
    Serial.begin(baudrate_);
}

// main function to always call and try and send data
// TODO: needs switch on data type with global timeouts on data pushing
void commsControl::sender() {
    if (millis() > lastTransTime_ + CONST_TIMEOUT_ALARM ) {
        sendQueue(queueAlarm_);
    }

    if (millis() > lastTransTime_ + CONST_TIMEOUT_CMD ) {
        sendQueue(queueCmd_);
    }

    if (millis() > lastTransTime_ + CONST_TIMEOUT_DATA ) {
        sendQueue(queueData_);
    }
}

// main function to always try to receive data
// TODO: needs switch on data type with global timeouts on data pushing
void commsControl::receiver(int &buga, int &bugb, int &bugc) {
    uint8_t currentTransIndex;

    // check if any data in waiting
    if (Serial.available()) {
        // while able to read data (unable == -1)
        while (Serial.peek() >= 0) {
            // read byte by byte, just in case the transmission is somehow blocked

            // WARNING: for mkrvidor4000, readbytes takes char* not uchar*
            lastTransIndex_ += Serial.readBytes(lastTrans_ + lastTransIndex_, 1);

            // if managed to read at least 1 byte
            if (lastTransIndex_ > 0 && lastTransIndex_ < CONST_MAX_SIZE_BUFFER) {
                currentTransIndex = lastTransIndex_ - 1;

                // find the boundary of frames
                if (lastTrans_[currentTransIndex] == COMMS_FRAME_BOUNDARY) {
                    // if not found start or if read the same byte as last time
                    if (!foundStart_ || startTransIndex_ == currentTransIndex) {
                        foundStart_ = true;
                        startTransIndex_ = currentTransIndex;
                    } else {
                        // if managed to decode and compare CRC
                        if (decoder(lastTrans_, startTransIndex_, lastTransIndex_)) {

                            sequenceReceive_ = (*(commsTmp_.getControl()) >> 1 ) & 0x7F;
                            // to decide ACK/NACK/other; for other gain sequenceReceive
                            uint8_t control = *(commsTmp_.getControl() + 1);

                            // to decide what kind of packets received
                            payloadType type = getInfoType(commsTmp_.getAddress());

                            // switch on received data to know what to do - received ACK/NACK or other
                            switch(control & COMMS_CONTROL_TYPES) {
                                case COMMS_CONTROL_NACK:
                                    // received NACK
                                    // TODO: modify timeout for next sent frame?
                                    // resendPacket(&address);
                                    buga++;
                                    break;
                                case COMMS_CONTROL_ACK:
                                    // received ACK
                                    finishPacket(type);
                                    bugb++;
                                    break;
                                default:
                                    uint8_t tmpSequenceReceive = (control >> 1 ) & 0x7F;
                                    tmpSequenceReceive += 1;
                                    bugc++;
                                    // received DATA
                                    if (receivePacket(type)) {
                                        commsAck_->setAddress(commsTmp_.getAddress());
                                        commsAck_->setSequenceReceive(tmpSequenceReceive);
                                        sendPacket(commsAck_);
                                    } else {
                                        commsNck_->setAddress(commsTmp_.getAddress());
                                        commsNck_->setSequenceReceive(tmpSequenceReceive);
                                        sendPacket(commsNck_);
                                    }

                                    break;
                            }
                        }

                        // reset the frame
                        foundStart_ = false;
                        lastTransIndex_ = 0;
                        startTransIndex_ = 0xFF;

                        // break the loop, even if more data waiting in the bus - this frame is finished
                        break;
                    }
                }
            } else if (lastTransIndex_ >= CONST_MAX_SIZE_BUFFER) {
                lastTransIndex_ = 0;
            }
        }
    }
}

bool commsControl::writePayload(payload &pl) {
    commsFormat* tmpComms;
    payloadType type = pl.getType();

    // switch on different received payload types
    // TODO simplify the static functions
    switch(type) {
        case payloadAlarm:
            tmpComms = commsFormat::generateALARM(&pl);
            break;
        case payloadData:
            tmpComms = commsFormat::generateDATA(&pl);
            break;
        case payloadCmd:
            tmpComms = commsFormat::generateCMD(&pl);
            break;
        default:
            return false;
    }

    RingBuf<commsFormat *, CONST_MAX_SIZE_RB_SENDING> *queue = getQueue(type);
    // add new entry to the queue
    if (queue->isFull()) {
        commsFormat *tmpCommsRm;
        if (queue->pop(tmpCommsRm)) {
            delete tmpCommsRm;
        }
    }

    if (queue->push(tmpComms) ) {
        return true;
    }
    return false;
}

bool commsControl::readPayload( payload &pl) {
    if ( !queueReceived_->isEmpty()) {
        if (queueReceived_->pop(pl)) {
            return true;
        }
    }
    return false;
}

// general encoder of any transmission
bool commsControl::encoder(uint8_t *data, uint8_t dataSize) {
    if (dataSize > 0) {
        commsSendSize_ = 0;
        uint8_t tmpVal = 0;

        commsSend_[commsSendSize_++] = data[0];
        for (uint8_t idx = 1; idx < dataSize - 1; idx++) {
            tmpVal = data[idx];
            if (tmpVal == COMMS_FRAME_ESCAPE || tmpVal == COMMS_FRAME_BOUNDARY) {
                commsSend_[commsSendSize_++] = COMMS_FRAME_ESCAPE;
                tmpVal ^= (1 << COMMS_ESCAPE_BIT_SWAP);
            }
            commsSend_[commsSendSize_++] = tmpVal;
        }
        commsSend_[commsSendSize_++] = data[dataSize-1];

        return true;
    }
    return false;
}


// general decoder of any transmission
bool commsControl::decoder(uint8_t* data, uint8_t dataStart, uint8_t dataStop) {
    // need to have more than 1 byte transferred
    if (dataStop > (dataStart + 1)) {
        commsReceivedSize_ = 0;
        uint8_t tmpVal = 0;
        bool escaped = false;

        for (uint8_t idx = dataStart; idx < dataStop; idx++) {
            tmpVal = data[idx];
            if (tmpVal == COMMS_FRAME_ESCAPE) {
                escaped = true;
            } else {
                if (escaped) {
                    tmpVal ^= (1 << COMMS_ESCAPE_BIT_SWAP);
                    escaped = false;
                }
                commsReceived_[commsReceivedSize_++] = tmpVal;
            }
        }
        commsTmp_.copyData(commsReceived_, commsReceivedSize_);
        return commsTmp_.compareCrc();
    }
    return false;
}

// sending anything of commsDATA format
void commsControl::sendQueue(RingBuf<commsFormat *, CONST_MAX_SIZE_RB_SENDING> *queue) {
    // if have data to send
    if (!queue->isEmpty()) {
        // reset sending counter
        lastTransTime_ = millis();

        queue->operator [](0)->setSequenceSend(sequenceSend_);

        sendPacket(queue->operator [](0));
    }
}

void commsControl::sendPacket(commsFormat *packet) {
    // if encoded and able to write data
    if (encoder(packet->getData(), packet->getSize()) ) {
        if (Serial.availableForWrite() >= commsSendSize_) {
            Serial.write(commsSend_, commsSendSize_);
        }
    }
}

// resending the packet, can lower the timeout since either NACK or wrong FCS already checked
//WIP
void commsControl::resendPacket(RingBuf<commsFormat *, CONST_MAX_SIZE_RB_SENDING> *queue) {
    ;
}


// receiving anything of commsFormat
bool commsControl::receivePacket(payloadType &type) {
    payloadTmp_.unsetAll();
    payloadTmp_.setType(type);
    void *tmpInformation = payloadTmp_.getInformation();
    // if type is definet, copy information from comms to payload
    if (tmpInformation != nullptr) {
        memcpy(tmpInformation, commsTmp_.getInformation(), commsTmp_.getInfoSize());

        // remove first entry if queue is full
        if (queueReceived_->isFull()) {
            payload tmpPlRm;
            if (queueReceived_->pop(tmpPlRm)) {
                ;
            }
        }
        return queueReceived_->push(payloadTmp_);
    }
    return false;
}

// if FCS is ok, remove from queue
void commsControl::finishPacket(payloadType &type) {
    RingBuf<commsFormat *, CONST_MAX_SIZE_RB_SENDING> *tmpQueue = getQueue(type);

    if (tmpQueue != nullptr && !tmpQueue->isEmpty()) {
        // get the sequence send from first entry in the queue, add one as that should be return
        // 0x7F to deal with possible overflows (0 should follow after 127)
        if (((tmpQueue->operator [](0)->getSequenceSend() + 1) & 0x7F) ==  sequenceReceive_) {
            sequenceSend_ = (sequenceSend_ + 1) % 128;
            commsFormat * tmpComms;
            if (tmpQueue->pop(tmpComms)) {
                delete tmpComms;
            }
        }
    }
}

payloadType commsControl::getInfoType(uint8_t *address) {
    switch (*address & PACKET_TYPE) {
        case PACKET_ALARM:
            return payloadType::payloadAlarm;
        case PACKET_CMD:
            return payloadType::payloadCmd;
        case PACKET_DATA:
            return payloadType::payloadData;
        default:
            return payloadType::payloadUnset;
    }
}

// get link to queue according to packet format
RingBuf<commsFormat *, CONST_MAX_SIZE_RB_SENDING> *commsControl::getQueue(payloadType &type) {
    switch (type) {
        case payloadType::payloadAlarm:
            return queueAlarm_;
        case payloadType::payloadCmd:
            return queueCmd_;
        case payloadType::payloadData:
            return queueData_;
        default:
            return nullptr;
    }
}
