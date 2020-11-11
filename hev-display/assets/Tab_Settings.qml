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
    function acknowledge(result) {
        if (result) {
            applyChanges(settings)
        } else {
            rejectChanges(settings)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        id: settings
        Settings_Ctrl {
            id: buffers
            title: qsTr("Buffers")
            entries: buffersLayout
            Layout.fillHeight: true
            Layout.fillWidth: true

            GridLayout {
                id: buffersLayout
                anchors.fill: parent
                columns: 3
                Single_Ctrl {
                    type: "SET_DURATION"
                    code: "CALIBRATION"
                    title.text: PayloadDictionary.commandCodes[code].replace(qsTr("Buffer"), "")
                    unit.text: "ms"
                    value.readback: readback["duration_calibration"]
                }
                Single_Ctrl {
                    type: "SET_DURATION"
                    code: "BUFF_PURGE"
                    title.text: PayloadDictionary.commandCodes[code].replace(qsTr("Buffer"), "")
                    unit.text: "ms"
                    value.readback: readback["duration_buff_purge"]
                }
                Single_Ctrl {
                    type: "SET_DURATION"
                    code: "BUFF_FLUSH"
                    title.text: PayloadDictionary.commandCodes[code].replace(qsTr("Buffer"), "")
                    unit.text: "ms"
                    value.readback: readback["duration_buff_flush"]
                }
                Single_Ctrl {
                    type: "SET_DURATION"
                    code: "BUFF_PREFILL"
                    title.text: PayloadDictionary.commandCodes[code].replace(qsTr("Buffer"), "")
                    unit.text: "ms"
                    value.readback: readback["duration_buff_prefill"]
                }
                Single_Ctrl {
                    type: "SET_DURATION"
                    code: "BUFF_FILL"
                    title.text: PayloadDictionary.commandCodes[code].replace(qsTr("Buffer"), "")
                    unit.text: "ms"
                    value.readback: readback["duration_buff_fill"]
                }
                Single_Ctrl {
                    type: "SET_DURATION"
                    code: "BUFF_PRE_INHALE"
                    title.text: PayloadDictionary.commandCodes[code].replace(qsTr("Buffer"), "")
                    unit.text: "ms"
                    value.readback: readback["duration_buff_pre_inhale"]
                }
            }
        }
        /*
        GridLayout {
            id: valves_pid_layout
            //anchors.fill: parent
            columns: 2

        Settings_Ctrl {
            id: pidsettings
            title: qsTr("PID")
            entries: pidLayout
            Layout.fillHeight: true
            Layout.fillWidth: true

            GridLayout {
            id: pidLayout
            anchors.fill: parent
            columns: 2

                Single_Ctrl {
                    type: "SET_PID"
                    code: "KP"
                    title.text: "KP"
                    value.readback: readback["kp"].toFixed(4)
                }
                Single_Ctrl {
                    type: "SET_PID"
                    code: "KI"
                    title.text: "KI"
                    value.readback: readback["ki"].toFixed(4)
                }
                Single_Ctrl {
                    type: "SET_PID"
                    code: "KD"
                    title.text: "KD"
                    value.readback: readback["kd"].toFixed(4)
                }
                Single_Ctrl {
                    type: "SET_TARGET_CURRENT"
                    code: "PID_GAIN"
                    title.text: PayloadDictionary.commandCodes[code].replace(qsTr("PID_GAIN"), "")
                    value.readback:  targets["CURRENT"]["pid_gain"].toFixed(1)
                }
            }
        }
        */

        Settings_Ctrl {
            id: pidsettings
            title: qsTr("PID")
            entries: pidLayout
            Layout.fillHeight: true
            Layout.fillWidth: true

            GridLayout {
            id: pidLayout
            anchors.fill: parent
            columns: 3
                Single_Ctrl {
                    type: "SET_PID"
                    code: "KP"
                    title.text: "KP"
                    value.readback: readback["kp"].toFixed(4)
                }
                Single_Ctrl {
                    type: "SET_PID"
                    code: "KI"
                    title.text: "KI"
                    value.readback: readback["ki"].toFixed(4)
                }
                Single_Ctrl {
                    type: "SET_PID"
                    code: "KD"
                    title.text: "KD"
                    value.readback: readback["kd"].toFixed(4)
                }
                Single_Ctrl {
                    type: "SET_PID"
                    code: "PID_GAIN"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback:  readback["pid_gain"].toFixed(1)
                }
                Single_Ctrl {
                    type: "SET_PID"
                    code: "MAX_PATIENT_PRESSURE"
                    title.text: PayloadDictionary.commandCodes[code].replace(qsTr("Patient Pressure"), "PP")
                    value.readback:  readback["max_patient_pressure"].toFixed(1)
                }
            }
        }
        Settings_Ctrl {
            id: valves
            title: qsTr("Valves")
            entries: valvesLayout
            Layout.fillHeight: true
            Layout.fillWidth: true

            GridLayout {
            id: valvesLayout
            anchors.fill: parent
            columns: 3
            Single_Ctrl {
                code: "VALVE_AIR_IN"
                title.text: PayloadDictionary.commandCodes[code].replace(qsTr("Valve"), "")
                value.readback: readback["valve_air_in"]
                active: false
            }
            Single_Ctrl {
                code: "VALVE_O2_IN"
                title.text: PayloadDictionary.commandCodes[code].replace(qsTr("Valve"), "")
                value.readback: readback["valve_o2_in"]
                active: false
            }
            Single_Ctrl {
                code: "VALVE_INHALE"
                title.text: PayloadDictionary.commandCodes[code].replace(qsTr("Valve"), "")
                value.readback: readback["valve_inhale"]
                active: false
            }
            Single_Ctrl {
                code: "VALVE_EXHALE"
                title.text: PayloadDictionary.commandCodes[code].replace(qsTr("Valve"), "")
                value.readback: readback["valve_exhale"]
                active: false
            }
            Single_Ctrl {
                code: "VALVE_PURGE"
                title.text: PayloadDictionary.commandCodes[code].replace(qsTr("Valve"), "")
                value.readback: readback["valve_purge"]
                active: false
            }
            Single_Ctrl {
                code: "VALVE_INHALE_PERCENT"
                title.text: PayloadDictionary.commandCodes[code].replace(qsTr("Valve"), "")
                unit.text: "%"
                value.readback: readback["valve_inhale_percent"]
                active: false
            }
            Single_Ctrl {
                code: "VALVE_EXHALE_PERCENT"
                title.text: PayloadDictionary.commandCodes[code].replace(qsTr("Valve"), "")
                unit.text: "%"
                value.readback: readback["valve_exhale_percent"]
                active: false
            }
            }
        }

        Settings_Ctrl {
            id: breathing
            title: qsTr("Breathing")
            entries: breathingLayout
            Layout.fillHeight: true
            Layout.fillWidth: true

            GridLayout {
                id: breathingLayout
                anchors.fill: parent
                columns: 3

                Single_Ctrl {
                    type: "SET_DURATION"
                    code: "INHALE"
                    title.text: PayloadDictionary.commandCodes[code]
                    unit.text: "ms"
                    value.readback: readback["duration_inhale"]
                }
                Single_Ctrl {
                    type: "SET_DURATION"
                    code: "PAUSE"
                    title.text: PayloadDictionary.commandCodes[code]
                    unit.text: "ms"
                    value.readback: readback["duration_pause"]
                }
                Single_Ctrl {
                    type: "SET_DURATION"
                    code: "EXHALE_FILL"
                    title.text: PayloadDictionary.commandCodes[code]
                    unit.text: "ms"
                    value.readback: readback["duration_exhale_fill"]
                }
                Single_Ctrl {
                    type: "SET_DURATION"
                    code: "EXHALE"
                    title.text: PayloadDictionary.commandCodes[code]
                    unit.text: "ms"
                    value.readback: readback["duration_exhale"]
                }

                Single_Ctrl {
                    code: "FSM_STATE"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: fastdata["fsm_state"]
                    active: false
                }
                Single_Ctrl {
                    code: "RESPIRATORY_RATE"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: cycle["respiratory_rate"].toFixed(1)
                    active: false
                }
                Single_Ctrl {
                    code: "INHALE_EXHALE_RATIO"
                    title.text: PayloadDictionary.commandCodes[code]
                    value.readback: readback["inhale_exhale_ratio"].toFixed(2)
                    active: false
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
