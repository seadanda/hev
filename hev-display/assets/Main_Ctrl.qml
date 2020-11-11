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

Item {
    id: mainctrl
    property string type: ""
    property string code: ""
    property alias title: titleText
    property alias value: currentValue
    Layout.fillHeight: true
    Layout.fillWidth: true
    Rectangle {
        id: bgrect
        color: value.active ? "transparent" : Style.highlightColor
        border.color: value.active ? "white" : "white"
        width: parent.width
        height: parent.height
        radius: 10
        anchors.fill: parent
    }
    Rectangle {
        anchors.top: parent.top
        id: currentValueRect
        color: "#3b3b3b"
        border.color: "white"
        width: parent.width
        height: parent.height / 3
        radius: 10
        Text {
            id: titleText
            anchors.fill: parent
            font.family: Style.fontFamily
            font.pixelSize: Style.h2Size
            color: "white"
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            width: parent.width
        }
    }
    Cell {
        id: currentValue
        anchors.top: currentValueRect.bottom
        anchors.bottom: parent.bottom
        width: currentValueRect.width
        bkgColor: "transparent"
        bkgRadius: currentValueRect.radius
        font.pixelSize: Style.mainValueSize
        activeColor: Style.highlightColor
        inactiveColor: "black"
    }
}
