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

Item {
    property var messages
    property var callback: function() {
        console.log("No confirmation callback set")
    }

    function initialize(messages, callback) {
        this.messages = messages
        confirmation.callback = callback
    }

    ColumnLayout {
        anchors.fill: parent

        Repeater {
            model: messages.length
            Text {
                text: messages[index]
                color: "white"
                Layout.fillWidth: true
                Layout.fillHeight: true
                verticalAlignment: Text.AlignVCenter
                font.family: Style.fontFamily
                font.weight: Font.Bold
                font.pixelSize: Style.titleSize
            }
        }

        Confirmation {
            Layout.fillHeight: true
            Layout.fillWidth: true
            id: confirmation
        }
    }
}
