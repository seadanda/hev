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
    property string modeValue   : "CURRENT"
    property string modeCurrent : "CURRENT"

    function initialize(value) {
        modeCurrent = value
        modeValue   = value
        dataSource.sendCommand("GET_TARGETS", modeValue, 0)
        for (var radio in radios.children) {
            if (radios.children[radio].code === value) {
                radios.children[radio].checked = true
            }
        }
    }

    function acknowledge(result) {
        returnInputMode(result, modeValue)
        confirmation.modified = false
    }

    ButtonGroup {
        id: group
        buttons: radios.children

        onClicked: {
            if (button.code === modeCurrent) {
                confirmation.modified = false
                button.textColor = "white"
            } else {
                confirmation.modified = true
                button.textColor = "red"
            }
            modeValue = button.code
            dataSource.sendCommand("GET_TARGETS", modeValue, 0)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        RowLayout {
            Layout.fillHeight: true
            Layout.fillWidth: true

            ColumnLayout {
                id: radios

                Layout.fillHeight: true
                Layout.fillWidth: true

                Radio_Ctrl {
                    code: "PC_AC"
                    text: PayloadDictionary.breathingModes[code]
                    textColor: "white"
                }
                Radio_Ctrl {
                    code: "PC_AC_PRVC"
                    text: PayloadDictionary.breathingModes[code]
                    textColor: "white"
                }
                Radio_Ctrl {
                    code: "PC_PSV"
                    text: PayloadDictionary.breathingModes[code]
                    textColor: "white"
                }
                Radio_Ctrl {
                    code: "CPAP"
                    text: PayloadDictionary.breathingModes[code]
                    textColor: "white"
                }
                // Radio_Ctrl {
                //     code: "TEST"
                //     text: PayloadDictionary.breathingModes[code]
                //     textColor: "white"
                // }
            }

            GridLayout {
                Layout.fillHeight: true
                Layout.fillWidth: true
                columns: 3
                columnSpacing: 10

                Label {
                    Layout.fillHeight: true;
                    Layout.fillWidth: true;
                    Layout.column: 1;
                    Layout.row: 0;
                    horizontalAlignment: Qt.AlignRight
                    verticalAlignment: Qt.AlignVCenter

                    text: qsTr("Current")
                    color: "white"
                    font.family: Style.fontFamily
                    font.pixelSize: Style.h1Size
                }
                Label {
                    Layout.fillHeight: true;
                    Layout.fillWidth: true;
                    Layout.column: 2;
                    Layout.row: 0;
                    horizontalAlignment: Qt.AlignRight
                    verticalAlignment: Qt.AlignVCenter

                    text: qsTr("New")
                    color: "white"
                    font.family: Style.fontFamily
                    font.pixelSize: Style.h1Size
                }

                Repeater {
                    model: ["RESPIRATORY_RATE", "INHALE_TIME", "IE_RATIO", "INHALE_TRIGGER_THRESHOLD", "EXHALE_TRIGGER_THRESHOLD", "INSPIRATORY_PRESSURE", "VOLUME", "FIO2_PERCENT"]
                    Label {
                        Layout.fillHeight: true;
                        Layout.fillWidth: true;
                        Layout.column: 0;
                        Layout.row: index + 1;
                        horizontalAlignment: Qt.AlignRight
                        verticalAlignment: Qt.AlignVCenter

                        text: PayloadDictionary.commandCodes[modelData]
                        color: "white"
                        font.family: Style.fontFamily
                        font.pixelSize: Style.h1Size
                    }
                }

                Repeater {
                    id: current
                    model: ["respiratory_rate", "inhale_time", "ie_ratio", "inhale_trigger_threshold", "exhale_trigger_threshold", "inspiratory_pressure", "volume",  "fiO2_percent"]
                    Label {
                        Layout.fillHeight: true;
                        Layout.fillWidth: true;
                        Layout.column: 1;
                        Layout.row: index + 1;
                        horizontalAlignment: Qt.AlignRight
                        verticalAlignment: Qt.AlignVCenter

                        text: target_CURRENT[modelData].toFixed(2)
                        color: "white"
                        font.family: Style.fontFamily
                        font.pixelSize: Style.h1Size
                    }
                }

                Repeater {
                    id: set
                    model: ["respiratory_rate", "inhale_time", "ie_ratio", "inhale_trigger_threshold", "exhale_trigger_threshold", "inspiratory_pressure", "volume",  "fiO2_percent"]
                    Label {
                        Layout.fillHeight: true;
                        Layout.fillWidth: true;
                        Layout.column: 2;
                        Layout.row: index + 1;
                        horizontalAlignment: Qt.AlignRight
                        verticalAlignment: Qt.AlignVCenter

                        text: targets[modeValue][modelData].toFixed(2)
                        color: targets[modeValue][modelData].toFixed(2) === target_CURRENT[modelData].toFixed(2) ? "white" : "red"
                        font.family: Style.fontFamily
                        font.pixelSize: Style.h1Size
                    }
                }
            }
        }
        Confirmation {
            id: confirmation
            Layout.fillWidth: true
            callback: acknowledge
        }
    }
}
