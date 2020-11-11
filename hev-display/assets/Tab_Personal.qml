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
    function callback() {
        dataSource.sendCommand("GENERAL", "GET_PERSONAL", 0)
    }

    function acknowledge(result) {
        if (result) {
            applyChanges(settings)
        } else {
            callback()
            rejectChanges(settings)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        id: settings
        Settings_Ctrl {
            titleVisible: false
            entries: personalLayout
            Layout.fillHeight: true
            Layout.fillWidth: true

            function sendChanges(changes) {
                dataSource.sendPersonal(name.value.text, patient_id.value.text, age.value.text, sex.value.text, height.value.text, weight.value.text)
            }

            GridLayout {
                id: personalLayout
                anchors.fill: parent
                columns: 1
                Single_Ctrl {
                    id: name
                    type: "SET_PERSONAL"
                    code: "NAME"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: personal["name"]
                    value.spin: false
                    value.inputMethodHints: Qt.ImhAutoUppercase | Qt.ImhSensitiveData
                    value.validator: RegExpValidator { regExp: /.+/ }
                }
                Single_Ctrl {
                    id: patient_id
                    type: "SET_PERSONAL"
                    code: "PATIENT_ID"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: personal["patient_id"]
                    value.spin: false
                    value.inputMethodHints: Qt.ImhAutoUppercase | Qt.ImhSensitiveData
                    value.validator: RegExpValidator { regExp: /.+/ }
                }
                Single_Ctrl {
                    id: age
                    type: "SET_PERSONAL"
                    code: "AGE"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: personal["age"]
                    unit.text: qsTr("years")
                }
//                ComboBox {
//                    Layout.fillHeight: true
//                    Layout.fillWidth: true
//                    Layout.maximumHeight: Style.btnHeight / 3 * 2

//                }

                Single_Ctrl {
                    id: sex
                    type: "SET_PERSONAL"
                    code: "SEX"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: personal["sex"]
                    value.spin: false
                    value.inputMethodHints: Qt.ImhLowercaseOnly
                    value.validator: RegExpValidator { regExp: /.{1}/ }
                }
                Single_Ctrl {
                    id: weight
                    type: "SET_PERSONAL"
                    code: "WEIGHT"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: personal["weight"]
                    unit.text: "kg"
                }
                Single_Ctrl {
                    id: height
                    type: "SET_PERSONAL"
                    code: "HEIGHT"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: personal["height"]
                    unit.text: "cm"
                }
            }
        }

        Confirmation {
            Layout.fillHeight: true
            Layout.fillWidth: true
            callback: acknowledge
        }
    }
}

