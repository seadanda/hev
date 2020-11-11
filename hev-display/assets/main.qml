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


import QtQuick 2.10
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.10
import QtGraphicalEffects 1.0
import QtQuick.VirtualKeyboard 2.1
import QtQuick.VirtualKeyboard.Settings 2.1

ApplicationWindow {
    id: applicationWindow
    visible: true
    visibility: "Maximized"
    flags: Qt.Window | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
    minimumWidth: 600
    minimumHeight: 400
    maximumWidth: 1920
    maximumHeight: 1080

    color: Style.mainBgColor

    property bool openGL: false
    property bool locked: false

    property bool powerMains  : ( battery["ok"] && !battery["bat"])
    property bool powerBattery: (!battery["ok"] &&  battery["bat"])
    property bool powerStatus : ( battery["bat85"])
    property bool powerError  : ((battery["ok"] === battery["bat"]) || battery["alarm"] || battery["rdy2buf"] || battery["prob_elec"])

    property string powerMode: {
        powerMains ? "svg/plug-solid.svg" : (powerBattery ? (powerMode === powerStatus ? "svg/battery-full-solid.svg" : "svg/battery-half-solid.svg") : "svg/battery-empty-solid.svg")
    }
    property string powerColor: {
        powerMains ? "white"              : (powerBattery ? (powerMode === powerStatus ? "orange"                     : "red")                        : "red")
    }

    property variant targets: {
        "PC_AC"     : target_PC_AC      ,
        "PC_AC_PRVC": target_PC_AC_PRVC ,
        "PC_PSV"    : target_PC_PSV     ,
        "CPAP"      : target_CPAP       ,
        "PURGE"     : target_PURGE      ,
        "FLUSH"     : target_FLUSH      ,
        "CURRENT"   : target_CURRENT
    }

    property bool alarmSilenced: false

    Timer {
        id: alarmTimer
        interval: 120000

        onTriggered: {
//            dataSource.ackAlarms()
            alarmSilenced = false
        }
    }

    // TODO: silence according to the specification
    function silenceAlarms() {
//        alarmSilenced = true
//        alarmNotification.visible = false

//        alarmTimer.restart()
    }

    function acknowledgeAlarms() {
//        alarmSilenced = false
//        alarmTimer.stop()
        dataSource.ackAlarms()
    }

    function notify(message, color = "white") {
        var notification = Qt.createQmlObject(
         'import QtQuick 2.0; Notification { text: "' + message + '"; color: "' + color + '" }',
         notifications,
         "Notifications");
        notification.destroy(3000);
        console.log(message)
    }
    Connections {
        target: dataSource
        onAlarm: console.log("Alarm: " + message);
        onAlarmsChanged: {
            alarmNotification.text = ""
            alarmNotification.visible = false
            var alarms_visible = 0
            for (var i = 0; i < dataSource.alarms.length; ++i) {
                if (dataSource.alarms[i].acked) continue
                if (++alarms_visible > 5) break
                alarmNotification.text += PayloadDictionary.commandCodes[dataSource.alarms[i].message] + "; "
                if (!alarmSilenced) alarmNotification.visible = true
            }
        }
        onDataChanged: fastdata[key] = value
        onReadbackChanged: {
            readback[key] = value;
            if (key === "ventilation_mode" && value !== readback["ventilation_mode"]) {
                notify(PayloadDictionary.breathingModes[value]+" mode")
            }
        }
        onCycleChanged: cycle[key] = value
        onIvtChanged: ivt[key] = value
        onTargetChanged: targets[mode][key] = value
        onBatteryChanged: { battery[key] = value; }
        onPersonalChanged: personal[key] = value

        onConnectedChanged: notify(dataSource.connected ? "Connected" : "Disconnected")
//        onCommandCreated: notify(name + " command created")
//        onCommandSent: notify(name + " command sent")
        onCommandAcked: notify(name + " command accepted", Style.acceptedColor)
        onCommandFailed: notify(name + " command failed", Style.failedColor)
        onNotification: notify(message)
    }

    header: Rectangle {
        height: 100

        color: Style.mainBgColor

        Image {
            id: logo
            anchors.left: parent.left
            anchors.top: parent.top
            source: "svg/cern-hev-logo-dark.png"
            sourceSize.height: parent.height
        }

        Text {
            id: modeText
            text: "Mode: "
            anchors.left: logo.right
            anchors.verticalCenter: parent.verticalCenter
            anchors.leftMargin: 30
            font.family: Style.fontFamily
            font.weight: Font.Bold
            color: Style.fontColor
            font.pixelSize: Style.titleSize
        }
        RoundButton {
            id: modeButton
            text: PayloadDictionary.breathingModes[readback["ventilation_mode"]]
            font.family: Style.fontFamily
            font.weight: Font.Bold
            font.pixelSize: Style.titleSize
            radius: Style.btnRadius
            width: 250
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: modeText.right
            anchors.leftMargin: 10
            onClicked: askInputMode()
        }
        Text {
            text: personal["name"] + ", " + personal["age"] + ", " + personal["weight"] + "kg"
            font.family: Style.fontFamily
            font.weight: Font.DemiBold
            font.pixelSize: Style.titleSize
            color: "white"
            anchors.left: modeButton.right
            anchors.leftMargin: 20
            anchors.verticalCenter: parent.verticalCenter
        }
        Image {
            id: plug
            source: powerMode
            sourceSize.width: parent.height * 0.8
            sourceSize.height: parent.height * 0.8
            anchors.right: parent.right
            anchors.rightMargin: 10
            anchors.verticalCenter: parent.verticalCenter
        }
        ColorOverlay {
            anchors.fill: plug
            source: plug
            color: powerColor
        }

        Row {
            anchors.left: parent.horizontalCenter

            Notification {
                id: alarmNotification
                width: applicationWindow.width / 2.1
                alarm: true
                color: "red"
                visible: false
            }
            Text {
                font.family: Style.fontFamily
                font.pixelSize: Style.tinySize
                font.weight: Font.DemiBold
                text: "Version: " + (typeof(version) !== "undefined" ? version : "preview")
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
            }
        }

        LockArea {
            visible: locked
            anchors.fill: parent
        }
    }

    StackLayout {
        id: stackLayout
        anchors.fill: parent
        anchors.leftMargin: drawer.width
        currentIndex: 0

        Page_Main {
            id: pageMain
            openGL: applicationWindow.openGL
        }
        Page_Alarms {
            id: pageAlarms
        }
        Page_Settings {
            id: pageSettings
        }
        Page_Expert {
            id: pageExpert
        }

        onCurrentIndexChanged: {
            try {
                itemAt(currentIndex).callback()
            } catch (error) {
            }
        }
    }
    Popup {
        id: holdPopup
        width: parent.width * 0.3
        height: parent.height * 0.3
        modal: false
        focus: false
        anchors.centerIn: Overlay.overlay

        background: Rectangle {
            color: Style.altBgColor
            radius: Style.btnRadius
        }
        ProgressBar {
            id: holdProgress
            anchors.fill: parent
            onValueChanged: if (value >= 1.0) holdComplete()
        }
        Timer {
            id: holdTimer
            interval: Style.holdSecs * 1000 / 20
            running: false
            repeat: true
            onTriggered: holdProgress.value += 0.05
        }
        onOpened: {
            holdProgress.value = 0
            holdTimer.start()
        }
    }
    function sendStandby(result) {
        if (result) dataSource.sendStandby()
        returnConfirmation()
    }
    function sendStop(result) {
        if (result) dataSource.sendStop()
        returnConfirmation()
    }

    Component {
        id: singleShot
        Timer {
            property var duration: 100
            property var multiplicator: 0
            property var action: function(multiplicator) {
                console.log("No action set")
            }
            interval: multiplicator * duration
            running: true
            onTriggered: {
                action(multiplicator)
                this.destroy()
            }
        }
    }

    signal holdComplete()
    onHoldComplete: {
        if (lockButton.pressed) {
            toggleLock()
//        } else if (connectButton.pressed) {
//            if (dataSource.connected) {
//                dataSource.broadcastDisconnect()
//            } else {
//                dataSource.broadcastConnect()
//            }
        } else if (startButton.pressed) {
            dataSource.sendStart()
        } else if (standbyButton.pressed) {
            holdPopup.close()
            askConfirmation([qsTr("Ventilation standby")], sendStandby)
        } else if (stopButton.pressed) {
            holdPopup.close()
            askConfirmation([qsTr("Ventilation stop")], sendStop)
        }
    }
    function toggleLock() {
        locked = !locked
        notify("Screen " + (locked ? "locked" : "unlocked"))
    }

    Input_Digits {
        id: dialog
    }

    function askInputDigits(item, value) {
        dialog.open()
        dialog.initialize(item, value)
        dialog.field.focus = true
    }

    Popup {
        id: modePopup
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        anchors.centerIn: Overlay.overlay
        background: Rectangle {
            color: Style.altBgColor
            radius: Style.btnRadius
        }
        visible: false
        contentItem: Input_Mode {
            id: modeInput
        }
    }
    function askInputMode() {
        modeInput.initialize(readback["ventilation_mode"])
        modePopup.open()
    }
    function returnInputMode(valid, value) {
        modePopup.close()
        if (valid) {
            dataSource.sendMode(PayloadDictionary.breathingModes[value], value)
        }
    }
    Popup {
        id: confirmationPopup
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        anchors.centerIn: Overlay.overlay
        background: Rectangle {
            color: Style.altBgColor
            radius: Style.btnRadius
        }
        visible: false
        contentItem: Input_Confirmation {
            id: confirmationInput
        }
    }
    function askConfirmation(message, callback) {
        confirmationInput.initialize(message, callback)
        confirmationPopup.open()
    }
    function returnConfirmation(valid) {
        confirmationPopup.close()
    }
    function applyChanges(controls) {
        var changes = []
        var messages = []
        for (var child in controls.children) {
            try {
                var change = controls.children[child].getModified()
                changes.push(change)
                controls.children[child].generateMessage(change, messages)
            } catch (error) {
                changes.push([])
                continue
            }
        }
        function confirmed(result) {
            if (result) {
                for (var child in controls.children) {
                    try {
                        controls.children[child].sendChanges(changes[child])
                    } catch (error) {
                        continue
                    }
                }
            }
            returnConfirmation()
        }
        if (messages.length > 0) askConfirmation(messages, confirmed)
    }
    function rejectChanges(controls) {
        for (var child in controls.children) {
            try {
                controls.children[child].resetModified()
            } catch (error) {
                continue
            }
        }
    }

    Popup {
        id: languagePopup
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        anchors.centerIn: Overlay.overlay
        background: Rectangle {
            color: Style.altBgColor
            radius: Style.btnRadius
        }
        visible: false
        contentItem: Input_Language {
            id: languageInput
        }
    }
    function returnInputLanguage() {
        languagePopup.close()
    }
    Column {
        id: notifications
        x: parent.width / 3 * 2 - 10
        y: 10
        width: parent.width / 3
        spacing: 10
    }
    LockArea {
        visible: locked
        anchors.fill: parent
    }

    function pageChange(index) {
        stackLayout.currentIndex = index
        for (var page = 0; page < pages.count; page++) {
            if (page === index) pages.itemAt(page).selectedColor = Style.btnUpColor
            else pages.itemAt(page).selectedColor = Style.btnDnColor
        }
    }

    Drawer {
        id: drawer
        modal: false
        interactive: false
        visible: true

        width: 0.06 * applicationWindow.width
        y: header.height
        height: applicationWindow.height - header.height
        background: Rectangle {
            color: Style.mainBgColor
            anchors.fill: parent
        }
        ColumnLayout {
            anchors.fill:parent
            Repeater {
                id: pages
                Layout.alignment: Qt.AlignTop
                model: [
                    "svg/user-md-solid.svg",
                    "svg/exclamation-triangle-solid.svg",
                    "svg/fan-solid.svg",
                    "svg/sliders-h-solid.svg"
                ]
                Button {
                    id: button
                    Layout.fillWidth: true
                    Layout.fillHeight: false
                    implicitHeight: width
                    property string selectedColor: index === 0 ? "white" : Style.btnDnColor
                    Image {
                        id: image
                        anchors.centerIn: parent
                        source: model.modelData
                        sourceSize.width: parent.width * 0.8
                        sourceSize.height: parent.height * 0.8
                    }
                    spacing: 1
                    background: Rectangle {
                        color: Style.mainBgColor
                    }
                    ColorOverlay {
                        anchors.fill: image
                        source: image
                        color: selectedColor
                    }
                    onReleased: pageChange(index)
                }
            }

            RoundButton {
                id: startButton
                height: Style.btnHeight
                Layout.fillWidth: true
                text: qsTr("START")
                font.family: Style.fontFamily
                font.pixelSize: Style.h3Size
                radius: Style.btnRadius
                onPressed: holdPopup.open()
                onReleased: holdPopup.close()
            }
            RoundButton {
                id: stopButton
                height: Style.btnHeight
                Layout.fillWidth: true
                text: qsTr("STOP")
                font.family: Style.fontFamily
                font.pixelSize: Style.h3Size
                radius: Style.btnRadius
                onPressed: holdPopup.open()
                onReleased: holdPopup.close()
            }
            RoundButton {
                id: standbyButton
                height: Style.btnHeight
                Layout.fillWidth: true
                text: qsTr("STANDBY")
                font.family: Style.fontFamily
                font.pixelSize: Style.h3Size
                radius: Style.btnRadius
                onPressed: holdPopup.open()
                onReleased: holdPopup.close()
            }
//            }
//            RoundButton {
//                id: connectButton
//                height: parent.height * 0.8
//                width: height
//                radius: Style.btnRadius
//                anchors.right: lockButton.left
//                anchors.rightMargin: 10
//                anchors.verticalCenter: parent.verticalCenter
//                Image {
//                    anchors.centerIn: parent
//                    source: "svg/sign-in-alt-solid.svg"
//                    visible: !dataSource.connected
//                    sourceSize.width: parent.height * 0.8
//                    sourceSize.height: parent.height * 0.8
//                }
//                BusyIndicator {
//                    anchors.centerIn: parent
//                    running: dataSource.connected
//                }
//                onPressed: holdPopup.open()
//                onReleased: holdPopup.close()
//            }
        }
    }

    RowLayout {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.rightMargin: 10
        anchors.bottomMargin: 10
        height: Style.btnHeight
        width: Style.btnHeight * 2 + 10
        spacing: 10

        RoundButton {
            id: languageButton
            Layout.fillHeight: true
            Layout.fillWidth: true
            radius: Style.btnRadius
            anchors.rightMargin: 10
            Image {
                anchors.centerIn: parent
                source: "svg/globe-europe-solid.svg"
                sourceSize.width: parent.width * 0.8
                sourceSize.height: parent.height * 0.8
                ColorOverlay {
                    anchors.fill: parent
                    source: parent
                    color: "white"
                }
            }
            background: Rectangle {
                color: Style.btnDnColor
                radius: Style.btnRadius
                opacity: 0.5
            }
            onClicked: {
                languageInput.initialize()
                languagePopup.open()
            }
        }
        RoundButton {
            id: lockButton
            Layout.fillHeight: true
            Layout.fillWidth: true
            radius: Style.btnRadius
            Image {
                anchors.centerIn: parent
                source: locked ? "svg/lock-solid.svg" : "svg/unlock-solid.svg"
                sourceSize.width: parent.height * 0.8
                sourceSize.height: parent.height * 0.8
                ColorOverlay {
                    anchors.fill: parent
                    source: parent
                    color: "white"
                }
            }
            background: Rectangle {
                color: Style.btnDnColor
                radius: Style.btnRadius
                opacity: 0.5
            }
            onPressed: holdPopup.open()
            onReleased: holdPopup.close()
        }
        LockArea {
            visible: locked
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }
}
