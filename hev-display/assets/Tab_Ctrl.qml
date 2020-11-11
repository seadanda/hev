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


import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12

ColumnLayout {
    function generateMessage(changes, types, codes) {
        var messages = []
        for (var modeIdx = 0; modeIdx < changes.length; modeIdx++) {
            for (var cmdIdx = 0; cmdIdx < changes[modeIdx].length; cmdIdx++) {
                messages.push(types[changes[modeIdx][cmdIdx][0]] + ", " + codes[changes[modeIdx][cmdIdx][1]] + ": " + changes[modeIdx][cmdIdx][2])
            }
        }

        return messages
    }

    function sendChanges(changes, cmd_type) {
        for (var modeIdx = 0; modeIdx < changes.length; modeIdx++) {
            for (var cmdIdx = 0; cmdIdx < changes[modeIdx].length; cmdIdx++) {
                dataSource.sendCommand(cmd_type + changes[modeIdx][cmdIdx][0], changes[modeIdx][cmdIdx][1], changes[modeIdx][cmdIdx][2])
            }
        }
    }

    function callback() {
        for (var modeIndex in modes.children) {
            dataSource.sendCommand("GET_TARGETS", modes.itemAt(modeIndex).mode, 0)
        }
    }

    function acknowledge(result) {
        if (result) {
            var changes = []
            for (var modeIndex in modes.children) {
                changes.push(modes.itemAt(modeIndex).getModified())
            }
            var messages = generateMessage(changes, PayloadDictionary.breathingModes, PayloadDictionary.commandCodes)

            function confirmed(result) {
                if (result) sendChanges(changes, "SET_TARGET_")
                returnConfirmation()
            }
            if (messages.length > 0) askConfirmation(messages, confirmed)
        } else {
            callback()
            for (var modeIndex in modes.children) {
                modes.itemAt(modeIndex).resetModified()
            }
        }
    }

}
