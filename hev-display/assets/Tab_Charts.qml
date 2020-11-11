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

    Rectangle {
        color: Style.mainBgColor
        anchors.fill: parent
    }
    RowLayout {
        anchors.fill: parent

        ColumnLayout {
            id: charts
            spacing: -20
            //https://www.qt.io/blog/2019/06/14/qt-support-aligning-chart-views-underneath
            property bool aligningPlots: true
            property var chartViews: [pressureChart, flowChart, volumeChart]
            function resetPlotAreas() {
                aligningPlot = true
                for (var i = 0; i < chartViews.length; i++) {
                    chartViews[i].plotArea = Qt.rect(0, 0, 0, 0)
                }
                aligningPlot = false
            }
            function alignPlotLeftMargin(chart) {
                if (aligningPlots)
                    return
                aligningPlots = true

                var tmpChart
                var bestRect = chart.plotArea
                var bestChart = chart
                for (var i = 0; i < chartViews.length; i++) {
                    tmpChart = chartViews[i]
                    if (!tmpChart.visible) {
                        continue
                    }
                    if (tmpChart.plotArea.left >
                        Math.ceil(bestRect.left) ||
                        (Math.ceil(tmpChart.plotArea.left) ===
                         Math.ceil(bestRect.left) &&
                         Math.floor(tmpChart.plotArea.right) <
                         Math.floor(bestRect.right))) {
                             bestChart = tmpChart
                             bestRect = tmpChart.plotArea
                     }
                }
                bestRect.left = Math.ceil(bestRect.left)
                bestRect.right = Math.floor(bestRect.right)
                for (i = 0; i < chartViews.length; i++) {
                    tmpChart = chartViews[i]
                    if (!tmpChart.visible) {
                        continue
                    }
                    if (tmpChart !== bestChart) {
                        var newLeft = 20 + bestRect.left -
                              Math.floor(tmpChart.plotArea.left);
                        var newRight = 20 +
                              Math.ceil(tmpChart.plotArea.right) -
                              bestRect.right
                        tmpChart.margins.left = newLeft
                        tmpChart.margins.right = newRight
                    }
                }
                aligningPlots = false
            }
            ChartView {
                id: pressureChart
                objectName: "labPressureChart" // for C++
                title: qsTr("Pressure")
                Layout.fillWidth: true
                Layout.fillHeight: true

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
                }
                ValueAxis {
                    id: pressureAxisCmH2O
                    objectName: "pressureAxisCmH2O" // for C++
                    titleText: "cmH<sub>2</sub>0"
                    labelFormat: "%.1f"
                    visible: false //TODO: only show an axis if there are series attached to it
                    min: 0
                    max: 30
                    color: "white"
                    labelsColor: "white"
                    gridLineColor: "white"
                    labelsFont.family: Style.fontFamily
                    labelsFont.pixelSize: Style.pSize
                }
                ValueAxis {
                    id: pressureAxismBar
                    objectName: "pressureAxismBar" // for C++
                    titleText: "mBar"
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
                    objectName: "pressure_air_supply"
                    property var realData: fastdata[objectName].toFixed(1)
                    name: qsTr("Air (supply)")
                    visible: false
                    axisX: pressureAxisTime
                    axisY: pressureAxismBar
                    useOpenGL: openGL
                    color: Style.pressureAirSupplyColor
                    //width: 3
                }
                LineSeries {
                    objectName: "pressure_air_regulated"
                    property var realData: fastdata[objectName].toFixed(1)
                    name: qsTr("Air (regulated)")
                    visible: false
                    axisX: pressureAxisTime
                    axisY: pressureAxismBar
                    useOpenGL: openGL
                    color: Style.pressureAirRegulatedColor
                    //style: Qt.DotLine
                }
                LineSeries {
                    objectName: "pressure_o2_supply"
                    property var realData: fastdata[objectName].toFixed(1)
                    name: qsTr("O2 (supply)")
                    visible: false
                    axisX: pressureAxisTime
                    axisY: pressureAxismBar
                    useOpenGL: openGL
                    color: Style.pressureO2SupplyColor
                }
                LineSeries {
                    objectName: "pressure_o2_regulated"
                    property var realData: fastdata[objectName].toFixed(1)
                    name: qsTr("O2 (regulated)")
                    visible: false
                    axisX: pressureAxisTime
                    axisY: pressureAxismBar
                    useOpenGL: openGL
                    color: Style.pressureO2RegulatedColor
                    //style: Qt.DotLine
                }
                LineSeries {
                    objectName: "pressure_inhale"
                    property var realData: fastdata[objectName].toFixed(1)
                    name: qsTr("Inhale")
                    visible: false
                    axisX: pressureAxisTime
                    axisYRight: pressureAxisCmH2O
                    useOpenGL: openGL
                    color: Style.pressureInhaleColor
                }
                LineSeries {
                    objectName: "pressure_patient"
                    property var realData: fastdata[objectName].toFixed(1)
                    name: qsTr("Patient")
                    axisX: pressureAxisTime
                    axisYRight: pressureAxisCmH2O
                    useOpenGL: openGL
                    color: Style.pressurePatientColor
                }
                onPlotAreaChanged: charts.alignPlotLeftMargin(pressureChart)
                onHeightChanged: pressureChart.plotArea = Qt.rect(0, 0, 0, 0)
            }
            ChartView {
                id: flowChart
                objectName: "labFlowChart" // for C++
                title: qsTr("Flow")
                Layout.fillWidth: true
                Layout.fillHeight: true

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
                    titleText: "mL/min"
                    objectName: "flowAxisMlMin" // for C++
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
                    objectName: "flow" //"pressure_diff_patient"
                    property var realData: fastdata[objectName].toFixed(1)
                    name: qsTr("Flow") //"Patient dP"
                    axisX: flowAxisTime
                    axisY: flowAxisMlMin
                    useOpenGL: openGL
                    color: Style.flowDiffPatientColor
                }
                onPlotAreaChanged: charts.alignPlotLeftMargin(flowChart)
                onHeightChanged: flowChart.plotArea = Qt.rect(0, 0, 0, 0)
            }
            ChartView {
                id: volumeChart
                objectName: "labVolumeChart" // for C++
                title: qsTr("Volume")
                Layout.fillWidth: true
                Layout.fillHeight: true

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
                    titleText: "mL"
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
                    property var realData: fastdata[objectName].toFixed(1)
                    name: qsTr("Volume")
                    axisX: volumeAxisTime
                    axisY: volumeAxisMl
                    useOpenGL: openGL
                    color: Style.volumeColor
                }
                onPlotAreaChanged: charts.alignPlotLeftMargin(volumeChart)
                onHeightChanged: volumeChart.plotArea = Qt.rect(0, 0, 0, 0)
            }
            Component.onCompleted: {
                // Alignment is currently extremely bugged when charts are added or removed
                // so for now it's disabled, uncomment the next line once it works better
                //aligningPlots = false
                alignPlotLeftMargin(pressureChart)
                alignPlotLeftMargin(flowChart)
                alignPlotLeftMargin(volumeChart)
            }
        }
        Grid {
            id: grid
            Layout.fillHeight: true
            columns: 2
            spacing: 10
            topPadding: 10

            Repeater {
                model: ListModel {}
                Component.onCompleted: {
                    var i;
                    for (i = 0; i < pressureChart.count; ++i) {
                        model.append({
                            chart: pressureChart,
                            seriesName: pressureChart.series(i).name,
                            seriesPos: i
                        })
                    }
                    for (i = 0; i < flowChart.count; ++i) {
                        model.append({
                            chart: flowChart,
                            seriesName: flowChart.series(i).name,
                            seriesPos: i
                        })
                    }
                    for (i = 0; i < volumeChart.count; ++i) {
                        model.append({
                            chart: volumeChart,
                            seriesName: volumeChart.series(i).name,
                            seriesPos: i
                        })
                    }
                }
                delegate: Rectangle {
                    property QtObject series: chart.series(seriesPos)
                    width: applicationWindow.width / 7
                    height: applicationWindow.height / 6
                    border.color: series.color
                    border.width: 3
                    radius: 10
                    color: Style.btnUpColor
                    Timer {
                        interval: 250 // 4 fps
                        running: true
                        repeat: true
                        onTriggered: currentValue.text = chart.series(seriesPos).realData
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: checkBox.checked = !checkBox.checked
                    }
                    CheckBox {
                        id: checkBox
                        visible: true
                        text: seriesName
                        font.family: Style.fontFamily
                        font.pixelSize: Style.h3Size
                        font.weight: Font.Bold
                        checked: series.visible
                        onCheckedChanged: {
                            if (series) {
                                //charts.resetPlotAreas()
                                series.visible = checked

                                if (checked) {
                                    chart.visible = true
                                } else {
                                    var vis = false
                                    for (var i = 0; i < chart.count; ++i) {
                                        if (chart.series(i).visible) {
                                            vis = true
                                            break
                                        }
                                    }
                                    chart.visible = vis
                                }
                            }
                        }
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottom: currentValueRect.top
                        text: series.axisYRight ? series.axisYRight.titleText : series.axisY.titleText
                        font.family: Style.fontFamily
                        font.pixelSize: 20
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
                            text: "-"
                            font.family: Style.fontFamily
                            font.pixelSize: 40
                            anchors.verticalCenter: parent.verticalCenter
                            horizontalAlignment: Text.AlignHCenter
                            anchors.left: parent.left
                            anchors.right: parent.right
                            color: series.color
                        }
                    }
                }
            }
            Rectangle {
                width: applicationWindow.width / 7
                height: applicationWindow.height / 13
                color: "transparent"
                GridLayout {
                    anchors.fill: parent
                    columnSpacing: 10
                    rowSpacing: 10
                    columns: 2
                    RoundButton {
                        text: "60s"
                        font.family: Style.fontFamily
                        font.weight: Font.Bold
                        font.pixelSize: 30
                        radius: 10
                        Layout.fillWidth: true
                        onClicked: axisTimeMin = -60
                    }
                    RoundButton {
                        text: "30s"
                        font.family: Style.fontFamily
                        font.weight: Font.Bold
                        font.pixelSize: 30
                        radius: 10
                        Layout.fillWidth: true
                        onClicked: axisTimeMin = -30
                    }
                }
            }
            Rectangle {
                width: applicationWindow.width / 7
                height: applicationWindow.height / 13
                color: "transparent"
                GridLayout {
                    anchors.fill: parent
                    columnSpacing: 10
                    rowSpacing: 10
                    columns: 2
                    RoundButton {
                        text: "15s"
                        font.family: Style.fontFamily
                        font.weight: Font.Bold
                        font.pixelSize: 30
                        radius: 10
                        Layout.fillWidth: true
                        onClicked: axisTimeMin = -15
                    }
                    RoundButton {
                        text: "5s"
                        font.family: Style.fontFamily
                        font.weight: Font.Bold
                        font.pixelSize: 30
                        radius: 10
                        Layout.fillWidth: true
                        onClicked: axisTimeMin = -5
                    }
                }
            }
        }
    }
}
