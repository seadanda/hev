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

    RowLayout {
        anchors.fill: parent

        ColumnLayout {
            id: mainTimeCharts
            Layout.fillHeight: true
            Layout.fillWidth: true
            spacing: -15

            ChartView {
                id: mainPressureChart
                objectName: "mainPressureChart"
                Layout.fillWidth: true
                Layout.fillHeight: true
                title: qsTr("Pressure [cmH2O]")
                titleColor: "white"
                titleFont.family: Style.fontFamily
                titleFont.pixelSize: Style.h3Size

                legend.visible: false
                animationOptions: ChartView.NoAnimation
                antialiasing: antialias
                backgroundColor: Style.mainBgColor

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
                    id: pressureAxisCmH2O
                    objectName: "pressureAxisCmH2O"
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
                    axisX: pressureAxisTime
                    axisY: pressureAxisCmH2O
                    useOpenGL: openGL
                }
            }

            ChartView {
                id: flowChart
                objectName: "mainFlowChart"
                Layout.fillWidth: true
                Layout.fillHeight: true
                title: qsTr("Flow [mL/min]")
                titleFont.family: Style.fontFamily
                titleFont.pixelSize: Style.h3Size
                titleColor: "white"

                legend.visible: false
                animationOptions: ChartView.NoAnimation
                antialiasing: antialias
                backgroundColor: Style.mainBgColor

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
                    objectName: "flowAxisMlMin"
                    labelFormat: "%.1f"
                    min: -150
                    max:  150
                    color: "white"
                    labelsColor: "white"
                    gridLineColor: "white"
                    labelsFont.family: Style.fontFamily
                    labelsFont.pixelSize: Style.pSize
                }
                LineSeries {
                    objectName: "flow"
                    axisX: flowAxisTime
                    axisY: flowAxisMlMin
                    useOpenGL: openGL
                }
            }

            ChartView {
                id: mainVolumeChart
                objectName: "mainVolumeChart"
                Layout.fillWidth: true
                Layout.fillHeight: true
                title: qsTr("Volume [mL]")
                titleFont.family: Style.fontFamily
                titleFont.pixelSize: Style.h3Size
                titleColor: "white"

                legend.visible: false
                animationOptions: ChartView.NoAnimation
                antialiasing: antialias
                backgroundColor: Style.mainBgColor

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
                    objectName: "volumeAxisMl"
                    labelFormat: "%.1f"
                    min: 0
                    max: 800
                    color: "white"
                    labelsColor: "white"
                    gridLineColor: "white"
                    labelsFont.family: Style.fontFamily
                    labelsFont.pixelSize: Style.pSize
                }
                LineSeries {
                    objectName: "volume"
                    axisX: volumeAxisTime
                    axisY: volumeAxisMl
                    useOpenGL: openGL
                }
            }
        }
        Grid {
            id: grid
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignVCenter
            columns: 2
            spacing: 10
            topPadding: 10

            Repeater {
                model: ListModel {}
                Component.onCompleted: {
                    model.append({
                        name: "FIO<sub>2</sub>",
                        unit: "%",
                        map: cycle,
                        key: "fiO2_percent",
                        color: "black"
                    })
                    model.append({
                        name: "I:E",
                        unit: "",
                        map: readback,
                        key: "inhale_exhale_ratio",
                        color: "black"
                    })
                    model.append({
                        name: "P<sub>PEAK</sub>",
                        unit: "cmH20",
                        map: cycle,
                        key: "peak_inspiratory_pressure",
                        color: "black"
                    })
                    model.append({
                        name: "P<sub>PLATEAU</sub>",
                        unit: "cmH20",
                        map: cycle,
                        key: "plateau_pressure",
                        color: "black"
                    })
                    model.append({
                        name: "P<sub>MEAN</sub>",
                        unit: "cmH20",
                        map: cycle,
                        key: "mean_airway_pressure",
                        color: "black"
                    })
                    model.append({
                        name: "PEEP",
                        unit: "cmH20",
                        map: readback,
                        key: "peep",
                        color: "black"
                    })
                    model.append({
                        name: "VTI",
                        unit: "mL",
                        map: cycle,
                        key: "inhaled_tidal_volume",
                        color: "black"
                    })
                    model.append({
                        name: "VTE",
                        unit: "mL",
                        map: cycle,
                        key: "exhaled_tidal_volume",
                        color: "black"
                    })
                    model.append({
                        name: "MVI",
                        unit: "L/min",
                        map: cycle,
                        key: "inhaled_minute_volume",
                        color: "black"
                    })
                    model.append({
                        name: "MVE",
                        unit: "L/min",
                        map: cycle,
                        key: "exhaled_minute_volume",
                        color: "black"
                    })
                }
                delegate: Rectangle {
                    width: applicationWindow.width / 7
                    height: applicationWindow.height / 7.5
                    border.color: color
                    border.width: 3
                    radius: 10
                    color: Style.btnUpColor
                    Label {
                        id: label
                        text: name
                        font.family: Style.fontFamily
                        font.pixelSize: Style.h3Size
                        font.weight: Font.Bold
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottom: currentValueRect.top
                        text: unit
                        font.family: Style.fontFamily
                        font.pixelSize: Style.h3Size
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignTop
                        width: parent.width
                    }
                    Rectangle {
                        id: currentValueRect
                        color: "black"
                        width: parent.width
                        height: applicationWindow.height / 15
                        radius: 10
                        anchors.bottom: parent.bottom
                        Text {
                            id: currentValue
                            text: map[key].toFixed(2)
                            font.family: Style.fontFamily
                            font.pixelSize: Style.tab2Size
                            anchors.verticalCenter: parent.verticalCenter
                            horizontalAlignment: Text.AlignHCenter
                            anchors.left: parent.left
                            anchors.right: parent.right
                            color: "white"
                        }
                    }
                }
            }
            RowLayout {
                width: applicationWindow.width / 7

                RoundButton {
                    text: qsTr("60s")
                    font.family: Style.fontFamily
                    font.weight: Font.Bold
                    font.pixelSize: Style.titleSize
                    radius: 10
                    Layout.fillWidth: true
                    onClicked: axisTimeMin = -60
                }
                RoundButton {
                    text: qsTr("30s")
                    font.family: Style.fontFamily
                    font.weight: Font.Bold
                    font.pixelSize: Style.titleSize
                    radius: 10
                    Layout.fillWidth: true
                    onClicked: axisTimeMin = -30
                }
            }
            RowLayout {
                width: applicationWindow.width / 7

                RoundButton {
                    text: qsTr("15s")
                    font.family: Style.fontFamily
                    font.weight: Font.Bold
                    font.pixelSize: Style.titleSize
                    radius: 10
                    Layout.fillWidth: true
                    onClicked: axisTimeMin = -15
                }
                RoundButton {
                    text: qsTr(" 5s")
                    font.family: Style.fontFamily
                    font.weight: Font.Bold
                    font.pixelSize: Style.titleSize
                    radius: 10
                    Layout.fillWidth: true
                    onClicked: axisTimeMin = -5
                }
            }
        }
        ColumnLayout {
            id: mainLoopCharts
            spacing: -15

            ChartView {
                id: loopPressureVolumeChart
                objectName: "loopPressureVolumeChart"
                Layout.fillWidth: true
                Layout.fillHeight: true
                titleColor: "white"

                legend.visible: false
                animationOptions: ChartView.NoAnimation
                antialiasing: antialias
                backgroundColor: Style.mainBgColor

                ValueAxis {
                    id: loopPressureVolumeAxisPressure
                    objectName: "loopPressureVolumeAxisPressure"
                    titleText: qsTr("Pressure [mBar]")
                    labelFormat: "%.1f"
                    min: 0
                    max: 30
                    color: "white"
                    labelsColor: "white"
                    gridLineColor: "white"
                    labelsFont.family: Style.fontFamily
                    labelsFont.pixelSize: Style.pSize
                }
                ValueAxis {
                    id: loopPressureVolumeAxisVolume
                    objectName: "loopPressureVolumeAxisVolume"
                    titleText: qsTr("Volume [mL]")
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
                    objectName: "loopPressureVolume"
                    axisX: loopPressureVolumeAxisPressure
                    axisY: loopPressureVolumeAxisVolume
                    useOpenGL: openGL
                }
            }
            ChartView {
                id: loopFlowVolumeChart
                objectName: "loopFlowVolumeChart"
                Layout.fillWidth: true
                Layout.fillHeight: true
                titleColor: "white"

                legend.visible: false
                animationOptions: ChartView.NoAnimation
                antialiasing: antialias
                backgroundColor: Style.mainBgColor

                ValueAxis {
                    id: loopFlowVolumeAxisVolume
                    objectName: "loopFlowVolumeAxisVolume"
                    titleText: qsTr("Volume [mL]")
                    labelFormat: "%.1f"
                    min: 0
                    max: 300
                    color: "white"
                    labelsColor: "white"
                    gridLineColor: "white"
                    labelsFont.family: Style.fontFamily
                    labelsFont.pixelSize: Style.pSize
                }
                ValueAxis {
                    id: loopFlowVolumeAxisFlow
                    objectName: "loopFlowVolumeAxisFlow"
                    titleText: qsTr("Flow [mL/min]")
                    labelFormat: "%.1f"
                    min: -1000
                    max: 1500
                    color: "white"
                    labelsColor: "white"
                    gridLineColor: "white"
                    labelsFont.family: Style.fontFamily
                    labelsFont.pixelSize: Style.pSize
                }

                LineSeries {
                    objectName: "loopFlowVolume"
                    axisX: loopFlowVolumeAxisVolume
                    axisY: loopFlowVolumeAxisFlow
                    useOpenGL: openGL
                }
            }
            ChartView {
                id: loopPressureFlowChart
                objectName: "loopPressureFlowChart"
                Layout.fillWidth: true
                Layout.fillHeight: true
                titleColor: "white"

                legend.visible: false
                animationOptions: ChartView.NoAnimation
                antialiasing: antialias
                backgroundColor: Style.mainBgColor

                ValueAxis {
                    id: loopPressureFlowAxisPressure
                    objectName: "loopPressureFlowAxisPressure"
                    titleText: qsTr("Pressure [mBar]")
                    labelFormat: "%.1f"
                    min: 0
                    max: 30
                    color: "white"
                    labelsColor: "white"
                    gridLineColor: "white"
                    labelsFont.family: Style.fontFamily
                    labelsFont.pixelSize: Style.pSize
                }
                ValueAxis {
                    id: loopPressureFlowAxisFlow
                    objectName: "loopPressureFlowAxisFlow"
                    titleText: qsTr("Flow [mL/min]")
                    labelFormat: "%.1f"
                    min: -1000
                    max: 1500
                    color: "white"
                    labelsColor: "white"
                    gridLineColor: "white"
                    labelsFont.family: Style.fontFamily
                    labelsFont.pixelSize: Style.pSize
                }

                LineSeries {
                    objectName: "loopPressureFlow"
                    axisX: loopPressureFlowAxisPressure
                    axisY: loopPressureFlowAxisFlow
                    useOpenGL: openGL
                }
            }
        }
    }
}
