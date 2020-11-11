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
    id: ctrl
    property alias title      : label_name
    property alias value      : field_value_left
    property alias value_right: field_value_right
    property alias unit       : label_unit
    property bool active      : true

    property var radioGroup: ""
    onRadioGroupChanged: {
        radio.ButtonGroup.group = radioGroup
    }

    Layout.fillWidth: true
    Layout.fillHeight: true
    Layout.margins: 0

    property string type      : ""
    property string type_right: ""
    property string code: ""

    property var tmp_value

    RowLayout {
        Layout.margins: 0
        spacing: 5
        anchors.fill: parent
        RadioButton {
            id: radio
            Layout.fillHeight: true
            visible: radioGroup === "" ? false : true
            checked: active
        }
        Label {
            id: label_name
            Layout.fillHeight: true
            Layout.fillWidth: true
            color: Style.fontColor
            horizontalAlignment: Qt.AlignRight
            verticalAlignment: Qt.AlignVCenter
            Layout.minimumWidth: 150
            Layout.preferredWidth: radio.visible ? parent.width/2 - radio.width - parent.spacing : parent.width/2
            font.family: Style.fontFamily
            font.pixelSize: Style.titleSize
            text: ""

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    radio.checked = radio.visible
                }
            }
        }
        Cell {
            id : field_value_left
            active: (!radio.visible || radio.checked) && ctrl.active
            Layout.minimumWidth: 50
            Layout.preferredWidth: 200
        }
        Cell {
            id : field_value_right
            active: (!radio.visible || radio.checked) && ctrl.active
            Layout.minimumWidth: 50
            Layout.preferredWidth: 200
        }
        Label {
            id: label_unit
            Layout.fillHeight: true
            Layout.fillWidth: true
            color: Style.fontColor
            verticalAlignment: Qt.AlignVCenter
            Layout.minimumWidth: 50
            Layout.preferredWidth: parent.width/10
            font.family: Style.fontFamily
            font.pixelSize: Style.titleSize
        }
    }

}
