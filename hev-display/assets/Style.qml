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


pragma Singleton
import QtQml 2.12
import QtQuick.Window 2.12

QtObject {
    property string fontFamily: "Open Sans"
    property int btnPixelSize: Math.ceil(btnHeight * 0.53)
    property int mainValueSize: 60
    property int tab1Size: 35
    property int tab2Size: 30
    property int tab3Size: 20
    property int titleSize: 35
    property int h1Size: 30
    property int h2Size: 24
    property int h3Size: 20
    property int measureSize: 80
    property int settingSize: 45
    property int pSize: 16
    property int tinySize: 10
    property color fontColor: "white"
    property color fontAltColor: "#212529"
    property color mainBgColor: "#1e1e1e"
    property color altBgColor: "black"
    property color btnUpColor: "white"
    property color btnDnColor: "#525556"
    property color readOnlyColor: "#cfcfcf"
    property color disabledColor: "#333333"
    property color acceptedColor: "green"
    property color failedColor: "orange"
    property color targetColor: "#429c92"
    property color measurementColor: "#8e3276"
    property color highlightColor: "#8ee5dc"
    property int btnWidth: 100
    property int btnHeight: 100
    property int btnRadius: 10
    property int holdSecs: 1

    property color pressureAirSupplyColor: "#8b2be2"
    property color pressureAirRegulatedColor: "#e8000b"
    property color pressureO2SupplyColor: "#023eff"
    property color pressureO2RegulatedColor: "#00d7ff"
    property color pressureBufferColor: "#ffc400"
    property color pressureInhaleColor: "#d3d3d3"

    property color pressurePatientColor: "#8080FF"
    property color flowDiffPatientColor: "#8CFF80"
    property color volumeColor: "#FF8080"
}
