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


Settings_Ctrl {
    Layout.fillHeight: true
    Layout.fillWidth: true
    //Layout.preferredWidth: 900
    //Layout.alignment: Qt.AlignCenter

    titleVisible: false
    entries: layout
    property string mode: ""
    property string command_type: "SET_TARGET_" + mode


    ColumnLayout {
        id: layout
        anchors.fill: parent

        ButtonGroup { id: inhaleGroup }

        Single_Ctrl {
            type: command_type
            code: "RESPIRATORY_RATE"
            title.text: PayloadDictionary.commandCodes[code]
            unit.text: "/min"
            value.readback: targets[mode]["respiratory_rate"].toFixed(1)
        }
        Single_Ctrl {
            type: command_type
            code: "INHALE_TIME"
            title.text: PayloadDictionary.commandCodes[code]
            unit.text: "s"
            value.readback: targets[mode]["inhale_time"].toFixed(1)
            radioGroup: inhaleGroup
        }
        Single_Ctrl {
            type: command_type
            code: "IE_RATIO"
            title.text: PayloadDictionary.commandCodes[code]
            value.readback: targets[mode]["ie_ratio"].toFixed(2)
            radioGroup: inhaleGroup
        }
        Single_Ctrl {
            type: command_type
            code: "INHALE_TRIGGER_THRESHOLD"
            title.text: PayloadDictionary.commandCodes[code]
            value.readback: targets[mode]["inhale_trigger_threshold"].toFixed(1)
            unit.text: "L/min"
        }
        Single_Ctrl {
            type: command_type
            code: "EXHALE_TRIGGER_THRESHOLD"
            title.text: PayloadDictionary.commandCodes[code]
            value.readback: targets[mode]["exhale_trigger_threshold"].toFixed(1)
            unit.text: "%"

            value.active  : mode === "PC_PSV" ? true : false;
            value.color : mode === "PC_PSV" ? Style.fontAltColor : Style.disabledColor;
            title.color : mode === "PC_PSV" ? Style.fontColor : Style.disabledColor;
            unit.color : mode === "PC_PSV" ? Style.fontColor : Style.disabledColor;
        }
        Single_Ctrl {
            type: command_type
            code: "INSPIRATORY_PRESSURE"
            title.text: PayloadDictionary.commandCodes[code]
            unit.text: "mBar"
            value.readback: targets[mode]["inspiratory_pressure"].toFixed(1)
        }
        Single_Ctrl {
            type: command_type
            code: "VOLUME"
            title.text: PayloadDictionary.commandCodes[code]
            unit.text: "L"
            value.readback: targets[mode]["volume"].toFixed(0)

            value.active  : mode === "PC_AC_PRVC" ? true : false;
            value.color : mode === "PC_AC_PRVC" ? Style.fontAltColor : Style.disabledColor;
            title.color : mode === "PC_AC_PRVC" ? Style.fontColor : Style.disabledColor;
            unit.color : mode === "PC_AC_PRVC" ? Style.fontColor : Style.disabledColor;
        }
        Single_Ctrl {
            type: command_type
            code: "FIO2_PERCENT"
            title.text: PayloadDictionary.commandCodes[code]
            unit.text: "%"
            value.readback: targets[mode]["fiO2_percent"].toFixed(1)
        }
    }
}

