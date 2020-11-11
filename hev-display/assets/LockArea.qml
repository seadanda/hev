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
import QtGraphicalEffects 1.0

MouseArea {
    onPressed: {
        lockSign.x = mouseX - lockSign.width / 2
        lockSign.y = mouseY - lockSign.height / 2
        lockSign.visible = true
    }
    onReleased: lockSign.visible = false
    RoundButton {
        id: lockSign
        width: parent.width * 0.1
        height: parent.width * 0.1
        visible: false
        radius: Style.btnRadius
        Image {
            anchors.centerIn: parent
            source: "svg/lock-solid.svg"
            sourceSize.width: parent.height * 0.8
            sourceSize.height: parent.height * 0.8
            ColorOverlay {
                anchors.fill: parent
                source: parent
                color: "white"
            }
        }
        background: Rectangle {
            color: Style.btnDnColor
            radius: Style.btnRadius
            opacity: 0.5
        }
    }
}
