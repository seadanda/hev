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

Label {
    id: item
    Layout.fillHeight: true
    Layout.fillWidth: true
    Layout.maximumHeight: Style.btnHeight / 3 * 2
    font.family: Style.fontFamily
    //font.weight: Font.Bold
    font.pixelSize: Style.titleSize
    horizontalAlignment: Qt.AlignHCenter
    verticalAlignment: Qt.AlignVCenter

    property bool active: true
    property bool spin  : true
    property string inactiveColor: "white"
    property string activeColor: "black"
    property color numColor: active ? activeColor : inactiveColor
    property color bkgColor: active ? "white": Style.mainBgColor
    property var   bkgRadius:0
    property bool modified : false
    property var readback

    property var inputMethodHints: Qt.ImhFormattedNumbersOnly
    property var validator: RegExpValidator { regExp: /\-?[0-9]+\.?[0-9]*/ }

    text: "0"
    color: numColor

    background: Rectangle {
        implicitWidth: parent.width
        color: bkgColor
        radius: bkgRadius
    }

    Button {
        id: up
        text: "+"
        font.pixelSize: Style.titleSize
        visible: active && spin
        anchors.right: parent.right
        anchors.top  : parent.top
        height: parent.height/2
        width: parent.width/5
        contentItem: Text {
            text: up.text
            font: up.font
            color: numColor
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        background: Rectangle {
            anchors.fill: parent
            color: "transparent"
        }
        onClicked: {
            try { item.text = Number(item.text) + 1 } catch (error) { }
        }
    }

    Button {
        id: down
        text: "\u2212"
        font.pixelSize: Style.titleSize
        visible: active && spin
        anchors.right : parent.right
        anchors.bottom: parent.bottom
        height: parent.height/2
        width: parent.width/5

        contentItem: Text {
            text: down.text
            font: down.font
            color: numColor
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        background: Rectangle {
            anchors.fill: parent
            color: "transparent"
        }
        onClicked: {
            try { item.text = Number(item.text) - 1 } catch (error) { }
        }
    }

    MouseArea {
        anchors.left  : parent.left
        anchors.top   : parent.top
        anchors.bottom: parent.bottom
        anchors.right : (active && spin) ? up.left : parent.right
        onReleased: {
            if (active) askInputDigits(item, text)
        }
    }

    function swapColor() {
        numColor = active ? activeColor : inactiveColor
    }

    onActiveChanged: {
        if (!modified) swapColor()
    }

    onTextChanged: {
        modified = !(Number(text)===Number(readback))
    }

    onReadbackChanged: {
        try { text = readback; modified = false } catch (error) { }
    }

    onModifiedChanged: {
        if (modified) {
            numColor = "red"
        }
        else {
            text = readback
            swapColor()
        }
    }
}

