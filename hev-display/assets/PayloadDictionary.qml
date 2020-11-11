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
    property variant breathingModes: {
        "UNKNOWN"    : qsTr("Unknown"),
        "PC_AC"      : qsTr("PC/AC"),
        "PC_AC_PRVC" : qsTr("PC/AC-PRVC"),
        "PC_PSV"     : qsTr("PC-PSV"),
        "CPAP"       : qsTr("CPAP"),
        //"TEST"       : qsTr("Test"),
        "PURGE"      : qsTr("Purge"),
        "FLUSH"      : qsTr("Flush"),
    }

    property variant commandTypes: {
        "PRIORITY_HIGH"         : qsTr("High Priority"),
        "PRIORITY_MEDIUM"       : qsTr("Medium Priority"),
        "PRIORITY_LOW"          : qsTr("Low Priority"),

        "GENERAL"               : qsTr("General"),
        "SET_DURATION"          : qsTr("Set Duration"),
        "SET_MODE"              : qsTr("Set Mode"),
        "SET_THRESHOLD_MIN"     : qsTr("Set Alarm Limit Minimum"),
        "SET_THRESHOLD_MAX"     : qsTr("Set Alarm Limit Maximum"),
        "SET_VALVE"             : qsTr("Set Valve"),
        "SET_PID"               : qsTr("Set PID"),
        "SET_TARGET_PC_AC"      : qsTr("Set PC/AC"),
        "SET_TARGET_PC_AC_PRVC" : qsTr("Set PC/AC-PRVC Data"),
        "SET_TARGET_PC_PSV"     : qsTr("Set PC-PSV Data"),
        "SET_TARGET_CPAP"       : qsTr("Set CPAP Data"),
        //"SET_TARGET_TEST"       : qsTr("Set Test Data"),
        "SET_TARGET_CURRENT"    : qsTr("Set Current Target Data"),
        "GET_TARGETS"           : qsTr("Get Target Data"),
        "SET_PERSONAL"          : qsTr("Set Personal Data"),
        "GET_THRESHOLD_MIN"     : qsTr("Get Alarm Limit Minimum"),
        "GET_THRESHOLD_MAX"     : qsTr("Get Alarm Limit Maximum"),
    }

    property variant commandCodes: {
        "UNKNOWN"                        : qsTr("Unknown"),
        "IDLE"                           : qsTr("Idle"),
        "STOP"                           : qsTr("Stop"),
        "STANDBY"                        : qsTr("Standby"),
        "AIR_IN_ENABLE"                  : qsTr("Air in Valve Enable"),
        "O2_IN_ENABLE"                   : qsTr("O2 in Valve Enable"),
        "PURGE_ENABLE"                   : qsTr("Purge Valve Enable"),
        "INHALE_DUTY_CYCLE"              : qsTr("Inhale Valve Duty Cycle"),
        "INHALE_OPEN_MIN"                : qsTr("Inhale Valve Open Minimum"),
        "INHALE_OPEN_MAX"                : qsTr("Inhale Valve Open Maximum"),
        "PID_KP"                             : qsTr("KP"),
        "PID_KI"                             : qsTr("KI"),
        "PID_KD"                             : qsTr("KD"),
        "PID_GAIN"                       : qsTr("PID GAIN"),
        "MAX_PATIENT_PRESSURE"           : qsTr("Max. Patient Pressure"),
        "TARGET_FINAL_PRESSURE"          : qsTr("Target Final Pressure"),
        "NSTEPS"                         : qsTr("Number of Steps"),
        "RESPIRATORY_RATE"               : qsTr("Respiratory Rate"),
        "INHALE_TIME"                    : qsTr("Inhale Time"),
        "IE_RATIO"                       : qsTr("I:E Ratio"),
        "INSPIRATORY_PRESSURE"           : qsTr("Inhale Pressure"),
        "VOLUME"                         : qsTr("Inhale Volume"),
        "FIO2_PERCENT"                   : qsTr("Percentage O2"),
        "BUFFER_UPPER_PRESSURE"          : qsTr("Buffer Upper Pressure"),
        "BUFFER_LOWER_PRESSURE"          : qsTr("Buffer Lower Pressure"),
        "INHALE_TRIGGER_THRESHOLD"       : qsTr("Inhale Trigger Sensitivity"),
        "EXHALE_TRIGGER_THRESHOLD"       : qsTr("Exhale Trigger Sensitivity"),
        "APNEA"                          : qsTr("APNEA"),
        "CHECK_VALVE_EXHALE"             : qsTr("Check Valve Exhale"),
        "CHECK_P_PATIENT"                : qsTr("Check Pressure Patient"),
        "EXPIRATION_SENSE_FAULT_OR_LEAK" : qsTr("Exp. Sense Fault or Leak"),
        "EXPIRATION_VALVE_LEAK"          : qsTr("Expiration Valve Leak"),
        "HIGH_FIO2"                      : qsTr("High FIO2"),
        "HIGH_PRESSURE"                  : qsTr("High Pressure"),
        "HIGH_RR"                        : qsTr("High Respiratory Rate"),
        "HIGH_VTE"                       : qsTr("High VTE"),
        "LOW_VTE"                        : qsTr("Low VTE"),
        "HIGH_VTI"                       : qsTr("High VTI"),
        "LOW_VTI"                        : qsTr("Low VTI"),
        "INTENTIONAL_STOP"               : qsTr("Intentional Stop"),
        "LOW_BATTERY"                    : qsTr("Low Battery"),
        "LOW_FIO2"                       : qsTr("Low FIO2"),
        "OCCLUSION"                      : qsTr("Occlusion"),
        "HIGH_PEEP"                      : qsTr("High PEEP"),
        "LOW_PEEP"                       : qsTr("Low PEEP"),
        "AC_POWER_DISCONNECTION"         : qsTr("AC Power Disconnection"),
        "BATTERY_FAULT_SRVC"             : qsTr("Battery Fault SRVC"),
        "BATTERY_CHARGE"                 : qsTr("Battery charge"),
        "AIR_FAIL"                       : qsTr("Air Fail"),
        "O2_FAIL"                        : qsTr("O2 Fail"),
        "PRESSURE_SENSOR_FAULT"          : qsTr("Pressure Sensor Fault"),
        "ARDUINO_FAIL"                   : qsTr("Arduino Fail"),
        "CALIBRATION"                    : qsTr("Calibration"),
        "BUFF_PURGE"                     : qsTr("Buffer Purge"),
        "BUFF_FLUSH"                     : qsTr("Buffer Flush"),
        "BUFF_PREFILL"                   : qsTr("Buffer Pre-fill"),
        "BUFF_FILL"                      : qsTr("Buffer Fill"),
        "BUFF_PRE_INHALE"                : qsTr("Buffer Pre-inhale"),
        "INHALE"                         : qsTr("Inhale"),
        "PAUSE"                          : qsTr("Pause"),
        "EXHALE_FILL"                    : qsTr("Exhale fill"),
        "EXHALE"                         : qsTr("Exhale"),
        "VALVE_AIR_IN"                   : qsTr("Air in Valve"),
        "VALVE_O2_IN"                    : qsTr("O2 in Valve "),
        "VALVE_INHALE"                   : qsTr("Inhale Valve"),
        "VALVE_EXHALE"                   : qsTr("Exhale Valve"),
        "VALVE_PURGE"                    : qsTr("Purge"),
        "VENTILATION_MODE"               : qsTr("Ventilation Mode"),
        "VALVE_INHALE_PERCENT"           : qsTr("Inhale Valve Opening"),
        "VALVE_EXHALE_PERCENT"           : qsTr("Exhale Valve Opening"),
        "VALVE_AIR_IN_ENABLE"            : qsTr("Air in Valve Enable"),
        "VALVE_O2_IN_ENABLE"             : qsTr("O2 in Valve Enable"),
        "VALVE_PURGE_ENABLE"             : qsTr("Purge Valve Enable"),
        "INHALE_TRIGGER_ENABLE"          : qsTr("Inhale Trigger Enable"),
        "EXHALE_TRIGGER_ENABLE"          : qsTr("Exhale Trigger Enable"),
        "PEEP"                           : qsTr("PEEP"),
        "INHALE_EXHALE_RATIO"            : qsTr("I:E Ratio"),
        "FSM_STATE"                      : qsTr("FSM State"),
        "PRESSURE_AIR_SUPPLY"            : qsTr("Air Supply Pressure"),
        "PRESSURE_AIR_REGULATED"         : qsTr("Air Regulated Pressure"),
        "PRESSURE_O2_SUPPLY"             : qsTr("O2 Supply Pressure"),
        "PRESSURE_O2_REGULATED"          : qsTr("O2 Regulated Pressure"),
        "PRESSURE_BUFFER"                : qsTr("Buffer Pressure"),
        "PRESSURE_INHALE"                : qsTr("Inhale Pressure"),
        "PRESSURE_PATIENT"               : qsTr("Patient Pressure"),
        "TEMPERATURE_BUFFER"             : qsTr("Buffer Temperature"),
        "PRESSURE_DIFF_PATIENT"          : qsTr("Patient Differential Pressure"),
        "AMBIENT_PRESSURE"               : qsTr("Ambient Pressure"),
        "AMBIENT_TEMPERATURE"            : qsTr("Ambient Temperature"),
        "AIRWAY_PRESSURE"                : qsTr("Airway Pressure"),
        "FLOW"                           : qsTr("Flow"),
        "TIDAL_VOLUME"                   : qsTr("Tidal Volume"),
        "EXHALED_TIDAL_VOLUME"           : qsTr("Tidal Volume Exhaled"),
        "INHALED_TIDAL_VOLUME"           : qsTr("Tidal Volume Inhaled"),
        "MINUTE_VOLUME"                  : qsTr("Minute Volume"),
        "EXHALED_MINUTE_VOLUME"          : qsTr("Minule Volume Exhaled"),
        "INHALED_MINUTE_VOLUME"          : qsTr("Minute Volume Inhaled"),
        "LUNG_COMPLIANCE"                : qsTr("Lung Compliance"),
        "STATIC_COMPLIANCE"              : qsTr("Static Compliance"),
        "INHALATION_PRESSURE"            : qsTr("Inhalation Pressure"),
        "PEAK_INSPIRATORY_PRESSURE"      : qsTr("Peak Inspiratory Pressure"),
        "PLATEAU_PRESSURE"               : qsTr("Plateau Pressure"),
        "MEAN_AIRWAY_PRESSURE"           : qsTr("Mean Airway Pressure"),
        "FI02_PERCENT"                   : qsTr("Fraction O2"),
        "APNEA_INDEX"                    : qsTr("Apnea Index"),
        "APNEA_TIME"                     : qsTr("Apnea Time"),
        "MANDATORY_BREATH"               : qsTr("Mandatory Breath"),
        "INHALE_CURRENT"                 : qsTr("Inhale Current"),
        "EXHALE_CURRENT"                 : qsTr("Exhale Current"),
        "PURGE_CURRENT"                  : qsTr("Purge Current"),
        "AIR_IN_CURRENT"                 : qsTr("Air in Current"),
        "O2_IN_CURRENT"                  : qsTr("O2 in Current"),
        "INHALE_VOLTAGE"                 : qsTr("Inhale Voltage"),
        "EXHALE_VOLTAGE"                 : qsTr("Exhale Voltage"),
        "PURGE_VOLTAGE"                  : qsTr("Purge Voltage"),
        "AIR_IN_VOLTAGE"                 : qsTr("Air in Voltage"),
        "O2_IN_VOLTAGE"                  : qsTr("O2 in Voltage"),
        "INHALE_I2CADDR"                 : qsTr("Inhale I2C Address"),
        "EXHALE_I2CADDR"                 : qsTr("Exhale I2C Address"),
        "PURGE_I2CADDR"                  : qsTr("Purge I2C Address"),
        "AIR_IN_I2CADDR"                 : qsTr("Air in I2C Address"),
        "O2_IN_I2CADDR"                  : qsTr("O2 in I2C Address"),
        "SYSTEM_TEMP"                    : qsTr("System Temperature"),
        "SEX"                            : qsTr("Sex"),
        "AGE"                            : qsTr("Age"),
        "HEIGHT"                         : qsTr("Height"),
        "WEIGHT"                         : qsTr("Weight"),
        "NAME"                           : qsTr("Name"),
        "PATIENT_ID"                     : qsTr("Patient ID"),

    }
}
