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
import QtGraphicalEffects 1.0

GridLayout {
    property var callback: function(result) {
        console.log("No confirmation callback set")
    }

    property bool modified: false

    rowSpacing: 10
    columnSpacing: 10

    columns: 2
    RoundButton {
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.minimumWidth: Style.btnHeight * 1.5
        Layout.minimumHeight: Style.btnHeight / 2
        Layout.maximumHeight: Style.btnHeight
        radius: Style.btnRadius
//        background: Rectangle {
//            color: modified ? "green" : Style.btnUpColor
//            radius: Style.btnRadius
//        }
        Image {
            anchors.centerIn: parent
            source: "svg/check-solid.svg"
            sourceSize.height: parent.height
            ColorOverlay {
                anchors.fill: parent
                source: parent
                color: modified ? "green" : "black"
            }
        }
        onClicked: callback(true)
    }
    RoundButton {
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.minimumWidth: Style.btnHeight * 1.5
        Layout.minimumHeight: Style.btnHeight / 2
        Layout.maximumHeight: Style.btnHeight
        radius: Style.btnRadius
//        background: Rectangle {
//            color: modified ? "red" : Style.btnUpColor
//            radius: Style.btnRadius
//        }
        Image {
            anchors.centerIn: parent
            source: "svg/times-solid.svg"
            sourceSize.height: parent.height
            ColorOverlay {
                anchors.fill: parent
                source: parent
                color: modified ? "red" : "black"
            }
        }
        onClicked: callback(false)
    }
}
