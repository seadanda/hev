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
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12

// this class only works with contents of type Single_Ctrl
GroupBox {
    property bool titleVisible: true
    property var entries

    function getModified() {
        var listOfCommands = []
        for (var child in entries.children) {
            try {
                if (entries.children[child].value.modified) {
                    if (entries.children[child].type !== "" ) {
                        listOfCommands.push([entries.children[child].type, entries.children[child].code, entries.children[child].value.text])
                    }
                }
                if (entries.children[child].value_right.modified) {
                    if (entries.children[child].type_right !== "" ) {
                        listOfCommands.push([entries.children[child].type_right, entries.children[child].code, entries.children[child].value_right.text])
                    }
                }
            } catch (error) {
                continue
            }
        }
        return listOfCommands
    }

    function resetModified() {
        for (var child in entries.children) {
            if (entries.children[child].value.modified) {
                entries.children[child].value.modified = false
            }
        }
    }

    function generateMessage(changes, messages) {
        for (var changeIndex = 0; changeIndex < changes.length; changeIndex++) {
            messages.push(PayloadDictionary.commandTypes[changes[changeIndex][0]] + ", " + PayloadDictionary.commandCodes[changes[changeIndex][1]] + ": " + changes[changeIndex][2])
        }
    }

    function sendChanges(changes) {
        for (var changeIndex = 0; changeIndex < changes.length; changeIndex++) {
            dataSource.sendCommand(changes[changeIndex][0], changes[changeIndex][1], changes[changeIndex][2])
        }
    }

    label: Label {
        visible: titleVisible
        width: parent.width
        Layout.fillHeight: true
        horizontalAlignment: Qt.AlignHCenter
        verticalAlignment  : Qt.AlignVCenter
        font.pixelSize: Style.titleSize
        font.family: Style.fontFamily
        color: Style.fontAltColor
        text: title
        background: Rectangle {
            anchors.fill: parent
            color: "white"
        }
    }
}
