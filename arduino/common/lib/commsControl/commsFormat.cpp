#include "commsFormat.h"

// constructor to init variables
commsFormat::commsFormat(uint8_t infoSize, uint8_t address, uint16_t control) {
    memset(data_, 0, sizeof(data_));

    infoSize_   = infoSize;
    packetSize_ = infoSize + CONST_MIN_SIZE_PACKET ; // minimum size (start,address,control,fcs,stop)
    if (packetSize_ > CONST_MAX_SIZE_PACKET) {
        return;
    }

    assignBytes(getAddress(), &address, 1, false);
    assignBytes(getControl(), reinterpret_cast<uint8_t*>(&control), 2, false);

    // hardcoded defaults
    *getStart()   = COMMS_FRAME_BOUNDARY; // fixed start flag
    *getStop()    = COMMS_FRAME_BOUNDARY; // fixed stop flag

    generateCrc();
}

void commsFormat::assignBytes(uint8_t* target, uint8_t* source, uint8_t size, bool calcCrc) {
    memcpy(target, source, size);
    if (calcCrc) {
        generateCrc();
    }
}

void commsFormat::setSequenceSend(uint8_t counter) {
    // sequence send valid only for info frames (not supervisory ACK/NACK)
    if ((*(getControl() + 1) & COMMS_CONTROL_SUPERVISORY) == 0) {
        counter = (counter << 1) & 0xFE;
        assignBytes(getControl() + 1, &counter, 1);
    }
}

uint8_t commsFormat::getSequenceSend() {
    // sequence send valid only for info frames (not supervisory ACK/NACK)
    if ((*(getControl() + 1) & COMMS_CONTROL_SUPERVISORY) == 0) {
        return (*(getControl() + 1) >> 1) & 0x7F;
    } else {
        return 0xFF;
    }
}

void commsFormat::setSequenceReceive(uint8_t counter) {
    counter = (counter << 1) & 0xFE;
    assignBytes(getControl()    , &counter, 1);
}

uint8_t commsFormat::getSequenceReceive() {
    return (*(getControl()) >> 1) & 0x7F;
}

// compare calculated and received CRC value
bool commsFormat::compareCrc() {
    // generate data crc
    generateCrc(false);

    // get crc from fcs
    uint16_t tmpFcs;
    assignBytes(reinterpret_cast<uint8_t*>(&tmpFcs), getFcs(), 2, false);

    // return comparison
    return tmpFcs == crc_;
}

// calculate CRC value
void commsFormat::generateCrc(bool assign) {
    // calculate crc
    crc_ = uCRC16Lib::calculate(reinterpret_cast<char*>(getAddress()), static_cast<uint16_t>(infoSize_ + 3));

    // assign crc to fcs
    if (assign) {
        assignBytes(getFcs(), reinterpret_cast<uint8_t*>(&crc_), 2, false);
    }
}

// assign received information to packet
void commsFormat::setInformation(payload *pl) {
    assignBytes(getInformation(), reinterpret_cast<uint8_t*>(pl->getInformation()), getInfoSize());
}

void commsFormat::copyData(uint8_t* data, uint8_t dataSize) {
    packetSize_ = dataSize;
    infoSize_ = dataSize - CONST_MIN_SIZE_PACKET;
    memset(getData(),    0, sizeof(data_));

    assignBytes(getData(), data, dataSize);
}


// STATIC METHODS
// TODO rewrite in a slightly better way using the enum
commsFormat* commsFormat::generateALARM(payload *pl) {
    commsFormat *tmpComms = new commsFormat(pl->getSize(), PACKET_ALARM);
    tmpComms->setInformation(pl);
    return tmpComms;
}
commsFormat* commsFormat::generateCMD  (payload *pl) {
    commsFormat *tmpComms = new commsFormat(pl->getSize(), PACKET_CMD  );
    tmpComms->setInformation(pl);
    return tmpComms;
}
commsFormat* commsFormat::generateDATA (payload *pl) {
    commsFormat *tmpComms = new commsFormat(pl->getSize(), PACKET_DATA );
    tmpComms->setInformation(pl);
    return tmpComms;
}

