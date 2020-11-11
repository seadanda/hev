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
    // Should rather be a map than a list, but a map is not a valid ListModel
    property variant langs: [
        // Setting name, Display name
        ["en", "English"],
        ["fr", "Français"],
        ["de", "Deutsch"],
        ["es", "Español"],
        ["it", "Italiano"],
        ["sk", "Slovenský"],
        ["lv", "Latviešu"]
    ]
    property string lang_value: descr2lang("")
    property string lang_descr: lang2descr("")

    function initialize() {
        lang_value = localization.language
        lang_descr = lang2descr(localization.language)
    }
    function lang2descr(lang) {
        for (var i = 0; i < langs.length; ++i) {
            if (langs[i][0] === lang) return langs[i][1]
        }
        return "Unknown"
    }
    function descr2lang(str) {
        for (var i = 0; i < langs.length; ++i) {
            if (langs[i][1] === str) return langs[i][0]
        }
        return "UNKNOWN"
    }

    ColumnLayout {
        spacing: 20
        Repeater {
            model: langs
            RadioButton {
                Layout.fillWidth: true
                height: Style.btnHeight
                text: model.modelData[1]
                checked: lang_value === model.modelData[0]
                contentItem: Text {
                    text: parent.text
                    color: "white"
                    leftPadding: parent.indicator.width + parent.spacing
                    verticalAlignment: Text.AlignVCenter
                    font.family: Style.fontFamily
                    font.weight: Font.Bold
                    font.pixelSize: Style.tab1Size
                }
                onCheckedChanged: {
                    if (checked) {
                        lang_descr = text
                        lang_value = descr2lang(text)
                    }
                }
            }
        }
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
            Layout.topMargin: 10
            spacing: 10
            RoundButton {
                Layout.fillWidth: true
                Layout.minimumWidth: Style.btnHeight * 1.5
                Layout.minimumHeight: Style.btnHeight
                Image {
                    anchors.centerIn: parent
                    source: "svg/check-solid.svg"
                    sourceSize.height: parent.height * 0.8
                }
                onClicked: {
                    localization.language = lang_value
                    returnInputLanguage()
                }
            }
            RoundButton {
                Layout.fillWidth: true
                Layout.minimumWidth: Style.btnHeight * 1.5
                Layout.minimumHeight: Style.btnHeight
                Image {
                    anchors.centerIn: parent
                    source: "svg/times-solid.svg"
                    sourceSize.height: parent.height * 0.8
                }
                onClicked: {
                    returnInputLanguage()
                }
            }
        }
    }
}
