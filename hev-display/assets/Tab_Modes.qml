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
    function callback() {
        for (var modeIndex in modes.children) {
            dataSource.sendCommand("GET_TARGETS", modes.itemAt(modeIndex).mode, 0)
        }
    }

    function acknowledge(result) {
        if (result) {
            applyChanges(modes)
        } else {
            callback()
            rejectChanges(modes)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true

            TabBar {
                id: bar
                Layout.fillWidth: true
                TabButton {
                    text: PayloadDictionary.breathingModes["PC_AC"]
                    font.family: Style.fontFamily
                    font.pixelSize: Style.tab2Size
                }
                TabButton {
                    text: PayloadDictionary.breathingModes["PC_AC_PRVC"]
                    font.family: Style.fontFamily
                    font.pixelSize: Style.tab2Size
                }
                TabButton {
                    text: PayloadDictionary.breathingModes["PC_PSV"]
                    font.family: Style.fontFamily
                    font.pixelSize: Style.tab2Size
                }
                TabButton {
                    text: PayloadDictionary.breathingModes["CPAP"]
                    font.family: Style.fontFamily
                    font.pixelSize: Style.tab2Size
                }
                // TabButton {
                //     text: PayloadDictionary.breathingModes["TEST"]
                //     font.family: Style.fontFamily
                //     font.pixelSize: Style.tab2Size
                // }
            }
            StackLayout {
                id: modes
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: bar.currentIndex
                Mode_Ctrl {
                    mode: "PC_AC"
                }
                Mode_Ctrl {
                    mode: "PC_AC_PRVC"
                }
                Mode_Ctrl {
                    mode: "PC_PSV"
                }
                Mode_Ctrl {
                    mode: "CPAP"
                }
                // Mode_Ctrl {
                //     mode: "TEST"
                // }
            }
        }

        Confirmation {
            Layout.fillHeight: true
            Layout.fillWidth: true
            callback: acknowledge
        }
    }
}
