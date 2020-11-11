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
import QtGraphicalEffects 1.0

Item {
    property alias text: label.text
    property alias color: rect.color
    property bool alarm: false
    width: parent.width
    height: 50

    RectangularGlow {
        anchors.fill: parent
        glowRadius: 10
        spread: 0.2
        color: "black"
        cornerRadius: glowRadius
    }
    Rectangle {
        id: rect
        anchors.fill: parent
        color: "white"
    }
    Image {
        id: icon
        anchors.left: parent.left
        anchors.leftMargin: 10
        anchors.verticalCenter: parent.verticalCenter
        source: alarm ? "svg/exclamation-triangle-solid.svg" : "svg/exclamation-circle-solid.svg"
        sourceSize.width: parent.height * 0.8
        sourceSize.height: parent.height * 0.8
    }
    Text {
        id: label
        anchors.left: icon.right
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        font.pixelSize: Style.pSize
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
