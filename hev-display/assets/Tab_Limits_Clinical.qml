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
    function getThresholds(child) {
        dataSource.sendCommand("GET_THRESHOLD_MIN", buffersLayout.children[child].code, 0)
        dataSource.sendCommand("GET_THRESHOLD_MAX", buffersLayout.children[child].code, 0)
    }

    function callback() {
        for (var child in buffersLayout.children) {
            singleShot.createObject(this, { action: getThresholds, multiplicator: child, duration: 200})
        }
    }

    function acknowledge(result) {
        if (result) {
            applyChanges(settings)
        } else {
            callback()
            rejectChanges(settings)
        }
    }

    property string cmd_type: "SET_THRESHOLD_"

    ColumnLayout {
        anchors.fill: parent
        id: settings
        Settings_Ctrl {
            titleVisible: false
            entries: buffersLayout
            Layout.fillHeight: true
            Layout.fillWidth: true

            GridLayout {
                id: buffersLayout
                anchors.fill: parent
                columns: 2

                Single_Ctrl {
                    code: "APNEA"
                    type : cmd_type + "MIN"
                    //type_right: cmd_type + "MAX"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: dataSource.cmdReadback["GET_THRESHOLD_MIN"][code]
                    //value_right.readback: dataSource.cmdReadback["GET_THRESHOLD_MAX"][code]
                }
                Double_Ctrl {
                    type : cmd_type + "MIN"
                    type_right: cmd_type + "MAX"
                    code: "CHECK_P_PATIENT"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: dataSource.cmdReadback["GET_THRESHOLD_MIN"][code]
                    value_right.readback: dataSource.cmdReadback["GET_THRESHOLD_MAX"][code]
                }
                Single_Ctrl {
                    type: cmd_type + "MAX"
                    code: "HIGH_FIO2"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: dataSource.cmdReadback["GET_THRESHOLD_MAX"][code]
                }
                Single_Ctrl {
                    type: cmd_type + "MAX"
                    code: "HIGH_PRESSURE"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: dataSource.cmdReadback["GET_THRESHOLD_MAX"][code]
                }
                Single_Ctrl {
                    type: cmd_type + "MAX"
                    code: "HIGH_RR"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: dataSource.cmdReadback["GET_THRESHOLD_MAX"][code]
                }
                Single_Ctrl {
                    type: cmd_type + "MAX"
                    code: "HIGH_VTE"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: dataSource.cmdReadback["GET_THRESHOLD_MAX"][code]
                }
                Single_Ctrl {
                    type : cmd_type + "MIN"
                    code: "LOW_VTE"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: dataSource.cmdReadback["GET_THRESHOLD_MIN"][code]
                }
                Single_Ctrl {
                    type: cmd_type + "MAX"
                    code: "HIGH_VTI"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: dataSource.cmdReadback["GET_THRESHOLD_MAX"][code]
                }
                Single_Ctrl {
                    type : cmd_type + "MIN"
                    code: "LOW_VTI"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: dataSource.cmdReadback["GET_THRESHOLD_MIN"][code]
                }
                Single_Ctrl {
                    type : cmd_type + "MIN"
                    code: "LOW_FIO2"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: dataSource.cmdReadback["GET_THRESHOLD_MIN"][code]
                }
                Double_Ctrl {
                    type : cmd_type + "MIN"
                    type_right: cmd_type + "MAX"
                    code: "OCCLUSION"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: dataSource.cmdReadback["GET_THRESHOLD_MIN"][code]
                    value_right.readback: dataSource.cmdReadback["GET_THRESHOLD_MAX"][code]
                }
                Single_Ctrl {
                    type: cmd_type + "MAX"
                    code: "HIGH_PEEP"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: dataSource.cmdReadback["GET_THRESHOLD_MAX"][code]
                }
                Single_Ctrl {
                    type : cmd_type + "MIN"
                    code: "LOW_PEEP"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: dataSource.cmdReadback["GET_THRESHOLD_MIN"][code]
                }
            }
        }
        Confirmation {
            callback: acknowledge
            Layout.fillHeight: true
            Layout.fillWidth: true
        }
    }
}
