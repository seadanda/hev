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


#include "CommsFormat.h"

// constructor to init variables
CommsFormat::CommsFormat(uint8_t info_size, uint8_t address, uint16_t control) {
    init(info_size, address, control);
}

CommsFormat::CommsFormat(Payload &pl) {
    uint8_t address;
    switch (pl.getType()) {
        case PRIORITY::ALARM_ADDR:
            address = PACKET_ALARM;
            break;
        case PRIORITY::CMD_ADDR:
            address = PACKET_CMD;
            break;
        case PRIORITY::DATA_ADDR:
            address = PACKET_DATA;
            break;
        default:
            address = 0;
            break;
    }
    init(pl.getSize(), address);
    setInformation(&pl);
}

void CommsFormat::init(uint8_t info_size, uint8_t address, uint16_t control) {
    memset(_data, 0, sizeof(_data));

    _info_size   = info_size;
    _packet_size = info_size + COMMS_MIN_SIZE_PACKET ; // minimum size (start,address,control,fcs,stop)
    if (_packet_size > COMMS_MAX_SIZE_PACKET) {
        return;
    }

    setAddress(&address, false);
    setControl(reinterpret_cast<uint8_t*>(&control), false);

    // hardcoded defaults
    *getStart()   = COMMS_FRAME_BOUNDARY; // fixed start flag
    *getStop()    = COMMS_FRAME_BOUNDARY; // fixed stop flag

    generateCrc();
}


void CommsFormat::assignBytes(uint8_t* target, uint8_t* source, uint8_t size, bool calcCrc) {
    memcpy(reinterpret_cast<void *>(target), reinterpret_cast<void *>(source), size);
    if (calcCrc) {
        generateCrc();
    }
}

void CommsFormat::setSequenceSend(uint8_t counter) {
    // sequence send valid only for info frames (not supervisory ACK/NACK)
    if ((*(getControl() + 1) & COMMS_CONTROL_SUPERVISORY) == 0) {
        counter = (counter << 1) & 0xFE;
        assignBytes(getControl() + 1, &counter, 1);
    }
}

uint8_t CommsFormat::getSequenceSend() {
    // sequence send valid only for info frames (not supervisory ACK/NACK)
    if ((*(getControl() + 1) & COMMS_CONTROL_SUPERVISORY) == 0) {
        return (*(getControl() + 1) >> 1) & 0x7F;
    } else {
        return 0xFF;
    }
}

void CommsFormat::setSequenceReceive(uint8_t counter) {
    counter = (counter << 1) & 0xFE;
    assignBytes(getControl()    , &counter, 1);
}

uint8_t CommsFormat::getSequenceReceive() {
    return (*(getControl()) >> 1) & 0x7F;
}

// compare calculated and received CRC value
bool CommsFormat::compareCrc() {
    // generate data crc
    generateCrc(false);

    // get crc from fcs
    uint16_t tmpFcs;
    assignBytes(reinterpret_cast<uint8_t*>(&tmpFcs), getFcs(), 2, false);

    // return comparison
    return tmpFcs == _crc;
}

// calculate CRC value
void CommsFormat::generateCrc(bool assign) {
    // calculate crc
    _crc = uCRC16Lib::calculate(reinterpret_cast<char*>(getAddress()), static_cast<uint16_t>(_info_size + 3));

    // assign crc to fcs
    if (assign) {
        assignBytes(getFcs(), reinterpret_cast<uint8_t*>(&_crc), 2, false);
    }
}

// assign received information to packet
// NOTE: possible confusion when using set information, the address or control are not changed!
void CommsFormat::setInformation(Payload *pl) {
    // if the info size changed only the info size
    if (_info_size != pl->getSize()) {
        init(pl->getSize(), _address, _control);
    }
    assignBytes(getInformation(), reinterpret_cast<uint8_t*>(pl->getInformation()), _info_size);
}

void CommsFormat::copyData(uint8_t* data, uint8_t dataSize) {
    _packet_size = dataSize;
    _info_size = dataSize - COMMS_MIN_SIZE_PACKET;
    memset(getData(),    0, sizeof(_data));

    assignBytes(getData(), data, dataSize);
}
