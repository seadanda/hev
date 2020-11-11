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
    id: page
    property bool antialias: true
    property bool openGL: false
    property int axisTimeMin : -15

    Rectangle {
        color: Style.mainBgColor
        anchors.fill: parent
    }

    ColumnLayout {
        anchors.fill: parent

        TabBar {
            id: bar
            Layout.fillWidth: false

            TabButton {
                text: qsTr("    Primary    ")
                font.family: Style.fontFamily
                font.pixelSize: Style.tab3Size
            }
            TabButton {
                text: qsTr("    Detailed    ")
                font.family: Style.fontFamily
                font.pixelSize: Style.tab3Size
            }
        }
        StackLayout {
            id: modes
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: bar.currentIndex

            Tab_Main_Basic {
                id: tabMainBasic
                openGL: openGL
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
            Tab_Main_Advanced {
                id: tabMainAdvanced
                openGL: openGL
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }
    }
}
