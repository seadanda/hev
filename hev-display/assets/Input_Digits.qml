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
import QtGraphicalEffects 1.0
import QtQuick.VirtualKeyboard 2.1
import QtQuick.VirtualKeyboard.Settings 2.1

Dialog {
    property alias field: text_field
    function initialize(item, value) {
        text_field.text         = value
        dialog.sourceField = item
        text_field.selectAll()

        text_field.inputMethodHints = item.inputMethodHints
        text_field.validator        = item.validator
    }

    function returnInput(result) {
        if (result) {
            if (text_field.acceptableInput) {
                dialog.sourceField.text = text_field.text
            } else {
                text_field.focus = true
                return
            }
        }
        dialog.close()
    }

    property Item sourceField

    modal: true
    focus: true
    visible: false
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
    anchors.centerIn: Overlay.overlay
    background: Rectangle {
        color: Style.altBgColor
        radius: Style.btnRadius
    }
    ColumnLayout {
        anchors.fill: parent
        TextField {
            id: text_field
            Layout.fillHeight: true
            Layout.fillWidth: true
            Layout.preferredWidth: applicationWindow.width/2
            Layout.preferredHeight: Style.btnHeight

            focus: true

            horizontalAlignment: Text.AlignHCenter
            placeholderText: "Fill value"
            overwriteMode: true
            font.family: Style.fontFamily
            font.weight: Font.Bold
            font.pixelSize: Style.btnPixelSize
        }
        InputPanel {
            id: inputPanel
            Layout.fillHeight: true
            Layout.fillWidth: true
            Layout.preferredWidth: applicationWindow.width/2
        }
        Confirmation {
            callback: dialog.returnInput
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredHeight: Style.btnHeight/2
        }
    }
}
