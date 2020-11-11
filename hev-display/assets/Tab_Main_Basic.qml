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
import QtCharts 2.3

Item {
    property bool antialias: true
    property bool openGL: false
    property int axisTimeMin : -15
    property bool moreBoxes: measurementBoxes.children.length > targetBoxes.children.length
    property var boxesCount: moreBoxes ? measurementBoxes.children.length : targetBoxes.children.length
    property var boxesDiff : moreBoxes ? measurementBoxes.children.length - targetBoxes.children.length : targetBoxes.children.length - measurementBoxes.children.length

    function acknowledge(result) {
        if (result) {
            applyChanges(currentTargets)
        } else {
            rejectChanges(currentTargets)
        }
    }

    GridLayout {
        id: mainbasic
        anchors.fill: parent
        flow: GridLayout.TopToBottom
        rows: 2
        rowSpacing: 5

        GridLayout {
            flow: GridLayout.TopToBottom
            rows: 3
            rowSpacing: -15
            id: charts
            Layout.fillHeight: true
            Layout.fillWidth: true

            ChartView {
                id: pressureChart
                objectName: "pressureChart" // for C++
                title: qsTr("Pressure [cmH20]")
                Layout.fillHeight: true
                Layout.fillWidth: true
                margins.top: 0
                margins.bottom: 0

                legend.visible: false
                animationOptions: ChartView.NoAnimation
                antialiasing: antialias
                backgroundColor: Style.mainBgColor
                titleColor: "white"
                titleFont.family: Style.fontFamily
                titleFont.pixelSize: Style.h3Size

                ValueAxis {
                    id: pressureAxisTime
                    min: axisTimeMin
                    max: 0
                    tickCount: Math.abs(max-min) / 5 + 1
                    labelFormat: "%.1f"
                    color: "white"
                    labelsColor: "white"
                    gridLineColor: "white"
                    labelsFont.family: Style.fontFamily
                    labelsFont.pixelSize: Style.pSize
                }
                ValueAxis {
                    id: pressureAxismBar
                    objectName: "pressureAxismBar" // for C++
                    labelFormat: "%.1f"
                    min: 0
                    max: 30
                    color: "white"
                    labelsColor: "white"
                    gridLineColor: "white"
                    labelsFont.family: Style.fontFamily
                    labelsFont.pixelSize: Style.pSize
                }
                LineSeries {
                    objectName: "pressure_patient"
                    name: qsTr("Patient")
                    axisX: pressureAxisTime
                    axisY: pressureAxismBar
                    useOpenGL: openGL
                    color: Style.pressurePatientColor
                }
            }
            ChartView {
                id: flowChart
                objectName: "flowChart" // for C++
                title: qsTr("Flow [L/min]")
                Layout.fillHeight: true
                Layout.fillWidth: true
                margins.top: 0
                margins.bottom: 0

                legend.visible: false
                animationOptions: ChartView.NoAnimation
                antialiasing: antialias
                backgroundColor: Style.mainBgColor
                titleColor: "white"
                titleFont.family: Style.fontFamily
                titleFont.pixelSize: Style.h3Size

                ValueAxis {
                    id: flowAxisTime
                    min: axisTimeMin
                    max: 0
                    tickCount: Math.abs(max-min) / 5 + 1
                    labelFormat: "%.1f"
                    color: "white"
                    labelsColor: "white"
                    gridLineColor: "white"
                    labelsFont.family: Style.fontFamily
                    labelsFont.pixelSize: Style.pSize
                }
                ValueAxis {
                    id: flowAxisMlMin
                    objectName: "flowAxisMlMin" // for C++
                    labelFormat: "%.1f"
                    min: -100
                    max: 100
                    color: "white"
                    labelsColor: "white"
                    gridLineColor: "white"
                    labelsFont.family: Style.fontFamily
                    labelsFont.pixelSize: Style.pSize
                }
                LineSeries {
                    objectName: "flow" //"pressure_diff_patient"
                    name: qsTr("Flow") //"Patient dP"
                    axisX: flowAxisTime
                    axisY: flowAxisMlMin
                    useOpenGL: openGL
                    color: Style.flowDiffPatientColor
                }
            }
            ChartView {
                id: volumeChart
                objectName: "volumeChart" // for C++
                title: qsTr("Volume [mL]")
                Layout.fillHeight: true
                Layout.fillWidth: true
                margins.top: 0
                margins.bottom: 0

                legend.visible: false
                animationOptions: ChartView.NoAnimation
                antialiasing: antialias
                backgroundColor: Style.mainBgColor
                titleColor: "white"
                titleFont.family: Style.fontFamily
                titleFont.pixelSize: Style.h3Size

                ValueAxis {
                    id: volumeAxisTime
                    min: axisTimeMin
                    max: 0
                    tickCount: Math.abs(max-min) / 5 + 1
                    labelFormat: "%.1f"
                    color: "white"
                    labelsColor: "white"
                    gridLineColor: "white"
                    labelsFont.family: Style.fontFamily
                    labelsFont.pixelSize: Style.pSize
                }
                ValueAxis {
                    id: volumeAxisMl
                    objectName: "volumeAxisMl" // for C++
                    labelFormat: "%.1f"
                    min: 0
                    max: 300
                    color: "white"
                    labelsColor: "white"
                    gridLineColor: "white"
                    labelsFont.family: Style.fontFamily
                    labelsFont.pixelSize: Style.pSize
                }
                LineSeries {
                    objectName: "volume"
                    name: qsTr("Volume")
                    axisX: volumeAxisTime
                    axisY: volumeAxisMl
                    useOpenGL: openGL
                    color: Style.volumeColor
                }
            }
        }
        GridLayout {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignCenter
            columnSpacing: 10
            Layout.margins: 0

            id: currentTargets
            GridLayout {
                columns: 2
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignCenter
                Layout.preferredWidth: parent.width / 8
                columnSpacing: 10
                Layout.leftMargin: 10
                RoundButton {
                    text: "60s"
                    font.family: Style.fontFamily
                    font.weight: Font.Bold
                    font.pixelSize: Style.titleSize
                    Layout.fillWidth: true
                    // Layout.maximumWidth: parent.width / 3
                    // Layout.preferredHeight: Style.btnHeight / 3
                     Layout.preferredWidth: parent.width / 2
                    radius: 10
                    onClicked: axisTimeMin = -60
                }
                RoundButton {
                    text: "30s"
                    font.family: Style.fontFamily
                    font.weight: Font.Bold
                    font.pixelSize: Style.titleSize
                    radius: 10
                    Layout.fillWidth: true
                    // Layout.maximumWidth: parent.width / 3
                    // Layout.preferredHeight: Style.btnHeight / 3
                    Layout.preferredWidth: parent.width / 2
                    onClicked: axisTimeMin = -30
                }
                RoundButton {
                    text: "15s"
                    font.family: Style.fontFamily
                    font.weight: Font.Bold
                    font.pixelSize: Style.titleSize
                    radius: 10
                    Layout.fillWidth: true
                    // Layout.maximumWidth: parent.width / 3
                    // Layout.preferredHeight: Style.btnHeight / 3
                    Layout.preferredWidth: parent.width / 2
                    onClicked: axisTimeMin = -15
                }
                RoundButton {
                    text: " 5s"
                    font.family: Style.fontFamily
                    font.weight: Font.Bold
                    font.pixelSize: Style.titleSize
                    radius: 10
                    Layout.fillWidth: true
                    // Layout.maximumWidth: parent.width / 3
                    // Layout.preferredHeight: Style.btnHeight / 3
                    Layout.preferredWidth: parent.width / 2
                    onClicked: axisTimeMin = -5
                }
            }

            Settings_Ctrl {
                spacing: 0
                padding: 0
                Layout.margins: 0
                id: settingsCtrl
                titleVisible: false
                Layout.fillHeight: true
                Layout.fillWidth: true
                Layout.preferredWidth: parent.width * 6 / 8
//                Layout.preferredHeight: (mainbasic.height / boxesCount) * targetBoxes.children.length
                Layout.alignment: Qt.AlignTop
                entries: targetBoxes

                background: Rectangle {
                    anchors.fill: parent
                    border.color: "transparent"
                    color: "transparent"
                }

                RowLayout {
                    id: targetBoxes
                    anchors.fill: parent

                    Main_Ctrl {
                        type: "SET_TARGET_CURRENT"
                        code: "INSPIRATORY_PRESSURE"
                        title.text: qsTr("P_insp [cmH2O]")
                        value.readback: targets["CURRENT"]["inspiratory_pressure"].toFixed(1)
                        Layout.preferredWidth: parent.width / 5
                        value.font.pixelSize: Style.settingSize
                    }
                    Main_Ctrl {
                        type: "SET_TARGET_CURRENT"
                        code: "RESPIRATORY_RATE"
                        title.text: qsTr("RR")
                        value.readback: targets["CURRENT"]["respiratory_rate"].toFixed(1)
                        Layout.preferredWidth: parent.width / 5
                        value.font.pixelSize: Style.settingSize
                    }
                    Main_Ctrl {
                        type: "SET_TARGET_CURRENT"
                        code: "FIO2_PERCENT"
                        title.text: qsTr("FIO2 [%]")
                        value.readback: targets["CURRENT"]["fiO2_percent"].toFixed(1)
                        Layout.preferredWidth: parent.width / 5
                        value.font.pixelSize: Style.settingSize
                    }
                    Main_Ctrl {
                        type: "SET_TARGET_CURRENT"
                        code: "INHALE_TIME"
                        title.text: PayloadDictionary.commandCodes[code] + " [s]"
                        value.readback: targets["CURRENT"]["inhale_time"].toFixed(1)
                        Layout.preferredWidth: parent.width / 5
                        value.font.pixelSize: Style.settingSize
                    }
                }
            }
            Confirmation {
                id: confirmation
                callback: acknowledge
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredHeight: Style.btnHeight/2
                Layout.preferredWidth: parent.width / 10

                columns: 1
            }
        }
        GridLayout {
            columns: 1
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: parent.width / 5
            Layout.maximumWidth: parent.width / 3

            ColumnLayout {
                id: test
                spacing: 0
                Layout.margins: 0
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                Layout.preferredWidth: parent.width 
                Layout.fillHeight: true

                GroupBox {
                    id: boxaa
                    label: Label {
                        width: parent.width
                        height: Style.btnHeight
                        horizontalAlignment: Qt.AlignHCenter
                        font.pixelSize: Style.titleSize
                        font.family: Style.fontFamily
                        color: "white"
                        text: qsTr("Measurements")
                    }

                    background: Rectangle {
                        id: rectaa
                        anchors.fill: parent
                        border.color: "transparent"
                        color: "transparent"
                    }

                    font.family: Style.fontFamily
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignTop
                    Layout.preferredWidth: parent.width 
                    Layout.fillHeight: true
                    Layout.preferredHeight: (mainbasic.height / (boxesCount)) * measurementBoxes.children.length

                    ColumnLayout {
                        id: measurementBoxes
                        anchors.fill: parent
                        Main_Ctrl {
                            title.text: qsTr("P_plateau [cmH2O]")
                            value.readback: cycle["plateau_pressure"].toFixed(1)
                            value.active: false
                            value.font.pixelSize: Style.measureSize
                            value.font.weight: Font.Bold
                        }
                        Main_Ctrl {
                            title.text: qsTr("RR")
                            value.readback: cycle["respiratory_rate"].toFixed(1)
                            value.active: false
                            value.font.pixelSize: Style.measureSize
                            value.font.weight: Font.Bold
                        }
                        Main_Ctrl {
                            title.text: qsTr("FIO2 [%]")
                            value.readback: cycle["fiO2_percent"].toFixed(1)
                            value.active: false
                            value.font.pixelSize: Style.measureSize
                            value.font.weight: Font.Bold
                        }
                        GridLayout {
                            columns: 2
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            Layout.preferredWidth: parent.width 
                            Layout.maximumWidth: parent.width 
                            ColumnLayout {
                                // id: test2
                                spacing: 0
                                Layout.margins: 0
                                Layout.fillWidth: true
                                Layout.alignment: Qt.AlignTop
                                Layout.preferredWidth: parent.width / 2
                                Layout.fillHeight: true

                                Main_Ctrl {
                                    title.text: qsTr("VTE [mL]")
                                    value.readback: cycle["exhaled_tidal_volume"].toFixed(0)
                                    value.active: false
                                    value.font.pixelSize: Style.measureSize
                                    value.font.weight: Font.Bold
                                }
                            }
                            ColumnLayout {
                                // id: test3
                                spacing: 0
                                Layout.margins: 0
                                Layout.fillWidth: true
                                Layout.alignment: Qt.AlignTop
                                Layout.preferredWidth: parent.width / 2
                                Layout.fillHeight: true
                                Main_Ctrl {
                                    title.text: qsTr("MVE [L/min]")
                                    value.readback: cycle["exhaled_minute_volume"].toFixed(0)
                                    value.active: false
                                    value.font.pixelSize: Style.measureSize
                                    value.font.weight: Font.Bold
                                }

                            }
                        }
                        Main_Ctrl {
                            title.text: qsTr("PEEP [cmH20]")
                            value.readback: readback["peep"].toFixed(1)
                            value.active: false
                            value.font.pixelSize: Style.measureSize
                            value.font.weight: Font.Bold
                        }
                    }
                }
                /*
                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    visible: moreBoxes
                    Layout.preferredHeight: ((mainbasic.height / boxesCount) * boxesDiff) + Style.btnHeight/2 - ( 30 * boxesDiff) // 30 somehow corresponds to padding
                }*/
            }
        }
    }
}
