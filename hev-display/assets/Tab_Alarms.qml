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
import QtGraphicalEffects 1.0

Item {
    ScrollView {
        anchors.fill: parent
        ScrollBar.vertical.policy: ScrollBar.AlwaysOn

        ListView {
            id: listView
            interactive: true
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 10
            model: dataSource.alarms

            delegate: Item {
                property QtObject alarm: dataSource.alarms[model.index]
                x: 5
                width: 80
                height: 30
                Row {
                    spacing: 10
                    Image {
                        source: alarm.acked ? 'svg/bell-regular.svg' : 'svg/bell-solid.svg'
                        sourceSize.width: parent.height * 0.8
                        sourceSize.height: parent.height * 0.8
                        ColorOverlay {
                            anchors.fill: parent
                            source: parent
                            color: Style.fontColor
                        }
                    }
                    Text {
                        text: alarm.since.toLocaleString("")
                        font.family: Style.fontFamily
                        font.pixelSize: Style.tab2Size
                        font.italic: true
                        color: Style.fontColor
                    }
                    Text {
                        text: alarm.until.toLocaleString("")
                        font.family: Style.fontFamily
                        font.pixelSize: Style.tab2Size
                        font.italic: true
                        color: Style.fontColor

                    }
                    Text {
                        text: PayloadDictionary.commandTypes[alarm.priority] + ": " + PayloadDictionary.commandCodes[alarm.message]
                        anchors.verticalCenter: parent.verticalCenter
                        font.family: Style.fontFamily
                        font.pixelSize: Style.tab2Size
                        font.bold: !alarm.acked
                        color: Style.fontColor
                    }
                }
            }
        }
    }
    Row {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 10
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 80
        spacing: 10
        RoundButton {
            id: btn
            width: Style.btnHeight * 1.5
            height: Style.btnHeight
            Image {
                anchors.centerIn: parent
                source: "svg/bell-regular.svg"
                sourceSize.height: parent.height * 0.8
            }
            onClicked: acknowledgeAlarms()
        }
        Text {
            anchors.verticalCenter: btn.verticalCenter
            text: qsTr("Acknowledge")
            font.family: Style.fontFamily
            font.pixelSize: Style.tab2Size
            color: Style.fontColor
        }
        RoundButton {
            id: silence
            width: Style.btnHeight * 1.5
            height: Style.btnHeight
            Image {
                anchors.centerIn: parent
                source: "svg/bell-solid.svg"
                sourceSize.height: parent.height * 0.8
            }
            onClicked: silenceAlarms()
        }
        Text {
            anchors.verticalCenter: btn.verticalCenter
            text: qsTr("Silence (120 s)")
            font.family: Style.fontFamily
            font.pixelSize: Style.tab2Size
            color: Style.fontColor
        }
    }
}
