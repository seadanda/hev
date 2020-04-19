from struct import Struct 
from enum import Enum, auto, unique
import logging
import binascii
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# VERSIONING
# change version in BaseFormat for all data
# i.e. if and of DataFormat, CommandFormat or AlarmFormat change
# then change the RPI_VERSION

class BaseFormat():
    def __init__(self):
        self._RPI_VERSION = 0xA1
        self._byteArray = None
        self._type = PAYLOAD_TYPE.UNSET
        self._version = 0

    @property
    def byteArray(self):
        return self._byteArray
    
    @byteArray.setter
    def byteArray(self):
        print("Use fromByteArray to change this")

    # check for mismatch between pi and microcontroller version
    def checkVersion(self):
        if self._RPI_VERSION == self._version :
            self._version_error = True
        else : 
            self._version_error = False

    def getSize(self):
        return len(self._byteArray)
            
    def getType(self):
        return self._type

    
# =======================================
# data type payload
# =======================================
class DataFormat(BaseFormat):

    # define the format here, including version
    def __init__(self):
        super().__init__()
        # struct will set the num bytes per variable
        # B = unsigned char = 1 byte
        # H = unsigned short = 2 bytes
        # I = unsigned int = 4 bytes
        # < = little endian
        # > = big endian
        # ! = network format (big endian)
        self._dataStruct = Struct("<BIBHHHHHHHHHBBBBBB")
        self._byteArray = None
        self._type = PAYLOAD_TYPE.DATA


        # make all zero to start with
        self._version = 0
        self._timestamp = 0
        self._fsm_state = "IDLE"
        self._pressure_air_supply = 0
        self._pressure_air_regulated = 0
        self._pressure_o2_supply = 0
        self._pressure_o2_regulated = 0
        self._pressure_buffer = 0
        self._pressure_inhale = 0
        self._pressure_patient = 0
        self._temperature_buffer = 0
        self._pressure_diff_patient = 0
        self._readback_valve_air_in = 0
        self._readback_valve_o2_in = 0
        self._readback_valve_inhale = 0
        self._readback_valve_exhale = 0
        self._readback_valve_purge = 0
        self._readback_mode = 0

    def __repr__(self):
        return f"""{{
    "version"                : {self._version},
    "timestamp"              : {self._timestamp},
    "fsm_state"              : {self._fsm_state},
    "pressure_air_supply"    : {self._pressure_air_supply},
    "pressure_air_regulated" : {self._pressure_air_regulated},
    "pressure_o2_supply"     : {self._pressure_o2_supply},
    "pressure_o2_regulated"  : {self._pressure_o2_regulated},
    "pressure_buffer"        : {self._pressure_buffer},
    "pressure_inhale"        : {self._pressure_inhale},
    "pressure_patient"       : {self._pressure_patient},
    "temperature_buffer"     : {self._temperature_buffer},
    "pressure_diff_patient"  : {self._pressure_diff_patient},
    "readback_valve_air_in"  : {self._readback_valve_air_in},
    "readback_valve_o2_in"   : {self._readback_valve_o2_in},
    "readback_valve_inhale"  : {self._readback_valve_inhale},
    "readback_valve_exhale"  : {self._readback_valve_exhale},
    "readback_valve_purge"   : {self._readback_valve_purge},
    "readback_mode"          : {self._readback_mode}
}}"""
        
    # for receiving DataFormat from microcontroller
    # fill the struct from a byteArray, 
    def fromByteArray(self, byteArray):
        self._byteArray = byteArray
        #logging.info(f"bytearray size {len(byteArray)} ")
        #logging.info(binascii.hexlify(byteArray))
        (self._version,
        self._timestamp,
        self._fsm_state,
        self._pressure_air_supply,
        self._pressure_air_regulated,
        self._pressure_o2_supply,
        self._pressure_o2_regulated,
        self._pressure_buffer,
        self._pressure_inhale,
        self._pressure_patient,
        self._temperature_buffer,
        self._pressure_diff_patient,
        self._readback_valve_air_in,
        self._readback_valve_o2_in,
        self._readback_valve_inhale,
        self._readback_valve_exhale,
        self._readback_valve_purge,
        self._readback_mode) = self._dataStruct.unpack(self._byteArray) 
        try:
            self._fsm_state = BL_STATES(self._fsm_state)
        except ValueError:
            self._fsm_state = BL_STATES(1)


    # for sending DataFormat to microcontroller
    # this is for completeness.  Probably we never send this data
    # to the microcontroller
    def toByteArray(self):
        # since pi is sender
        self._version = self._RPI_VERSION

        self._byteArray = self._dataStruct.pack(
            self._RPI_VERSION,
            self._timestamp,
            self._fsm_state,
            self._pressure_air_supply,
            self._pressure_air_regulated,
            self._pressure_o2_supply,
            self._pressure_o2_regulated,
            self._pressure_buffer,
            self._pressure_inhale,
            self._pressure_patient,
            self._temperature_buffer,
            self._pressure_diff_patient,
            self._readback_valve_air_in,
            self._readback_valve_o2_in,
            self._readback_valve_inhale,
            self._readback_valve_exhale,
            self._readback_valve_purge,
            self._readback_mode
        ) 

    def getDict(self):
        data = {
            "version"                : self._version,
            "timestamp"              : self._timestamp,
            "fsm_state"              : self._fsm_state,
            "pressure_air_supply"    : self._pressure_air_supply,
            "pressure_air_regulated" : self._pressure_air_regulated,
            "pressure_o2_supply"     : self._pressure_o2_supply,
            "pressure_o2_regulated"  : self._pressure_o2_regulated,
            "pressure_buffer"        : self._pressure_buffer,
            "pressure_inhale"        : self._pressure_inhale,
            "pressure_patient"       : self._pressure_patient,
            "temperature_buffer"     : self._temperature_buffer,
            "pressure_diff_patient"  : self._pressure_diff_patient,
            "readback_valve_air_in"  : self._readback_valve_air_in,
            "readback_valve_o2_in"   : self._readback_valve_o2_in,
            "readback_valve_inhale"  : self._readback_valve_inhale,
            "readback_valve_exhale"  : self._readback_valve_exhale,
            "readback_valve_purge"   : self._readback_valve_purge,
            "readback_mode"          : self._readback_mode
        }
        return data

# =======================================
# cmd type payload
# =======================================
class CommandFormat(BaseFormat):
    def __init__(self, cmdType=0, cmdCode=0, param=0):
        super().__init__()
        self._dataStruct = Struct("<BIBBI")
        self._byteArray = None
        self._type = PAYLOAD_TYPE.CMD

        self._version = 0
        self._timestamp = 0
        self._cmdType = cmdType
        self._cmdCode = cmdCode
        self._param = param
        self.toByteArray()

    # manage direct reading and writing of member variables
    @property
    def cmdType(self):
        return self._cmdType
    
    @cmdType.setter
    def cmdType(self, cmdTypeIn):
        self._cmdType = cmdTypeIn
        self.toByteArray()

    @property
    def cmdCode(self):
        return self._cmdCode
    
    @cmdCode.setter
    def cmdCode(self, cmdCodeIn):
        self._cmdCode = cmdCodeIn
        self.toByteArray()

    @property
    def param(self):
        return self._param
    
    @param.setter
    def param(self, paramIn):
        self._param = paramIn
        self.toByteArray()

    # print nicely
    def __repr__(self):
        return f"""{{
    "version"   : {self._version},
    "timestamp" : {self._timestamp},
    "cmdType"   : {self._cmdType},
    "cmdCode"   : {self._cmdCode},
    "param"     : {self._param}
}}"""
        
    def fromByteArray(self, byteArray):
        self._byteArray = byteArray
        (self._version,
        self._timestamp,
        self._cmdType,
        self._cmdCode,
        self._param) = self._dataStruct.unpack(self._byteArray) 

    def toByteArray(self):
        # since pi is sender
        self._byteArray = self._dataStruct.pack(
            self._RPI_VERSION,
            self._timestamp,
            self._cmdType,
            self._cmdCode,
            self._param
        )

    def getDict(self):
        data = {
            "version"   : self._version,
            "timestamp" : self._timestamp,
            "cmdType"   : self._cmdType,
            "cmdCode"   : self._cmdCode,
            "param"     : self._param
        }
        return data
        
# =======================================
# alarm type payload
# =======================================
class AlarmFormat(BaseFormat):
    def __init__(self):
        super().__init__()
        self._dataStruct = Struct("<BIBBI")
        self._byteArray = None
        self._type = PAYLOAD_TYPE.ALARM

        self._version = 0
        self._timestamp = 0
        self._alarmType = 0
        self._alarmCode = 0
        self._param = 0

    def __repr__(self):
        return f"""{{
    "version"   : {self._version},
    "timestamp" : {self._timestamp},
    "alarmType" : {self._alarmType},
    "alarmCode" : {self._alarmCode},
    "param"     : {self._param}
}}"""
        
    def fromByteArray(self, byteArray):
        self._byteArray = byteArray
        (self._version,
        self._timestamp,
        self._alarmType,
        self._alarmCode,
        self._param) = self._dataStruct.unpack(self._byteArray)

    def toByteArray(self):
        self._byteArray = self._dataStruct.pack(
            self._RPI_VERSION,
            self._timestamp,
            self._alarmType,
            self._alarmCode,
            self._param
        ) 
    
    def getDict(self):
        data = {
            "version"   : self._version,
            "timestamp" : self._timestamp,
            "alarmType" : self._alarmType,
            "alarmCode" : self._alarmCode,
            "param"     : self._param
        }
        return data


# =======================================
# Enum definitions
# =======================================
class PAYLOAD_TYPE(Enum):
    DATA  = auto()
    CMD   = auto()
    ALARM = auto()
    UNSET = auto()

@unique
class CMD_TYPE(Enum):
    GENERAL           =  1
    SET_TIMEOUT       =  2
    SET_MODE          =  3
    SET_THRESHOLD_MIN =  4
    SET_THRESHOLD_MAX =  5

@unique
class CMD_GENERAL(Enum):
    START =  1
    STOP  =  2
    PURGE =  3
    FLUSH =  4

# Taken from the FSM doc. Correct as of 1400 on 20200417
@unique
class CMD_SET_TIMEOUT(Enum):
    CALIBRATION     =  1
    BUFF_PURGE      =  2
    BUFF_FLUSH      =  3
    BUFF_PREFILL    =  4
    BUFF_FILL       =  5
    BUFF_LOADED     =  6
    BUFF_PRE_INHALE =  7
    INHALE          =  8
    PAUSE           =  9
    EXHALE_FILL     = 10
    EXHALE          = 11

class CMD_SET_MODE(Enum):
    HEV_MODE_PS   = auto()
    HEV_MODE_CPAP = auto()
    HEV_MODE_PRVC = auto()
    HEV_MODE_TEST = auto()

@unique
class ALARM_TYPE(Enum):
    LP   = 1
    MP   = 2
    HP   = 3

@unique
class ALARM_CODES(Enum):
    APNEA                          =  1  # HP
    CHECK_VALVE_EXHALE             =  2  # HP
    CHECK_P_PATIENT                =  3  # HP
    EXPIRATION_SENSE_FAULT_OR_LEAK =  4  #   MP
    EXPIRATION_VALVE_Leak          =  5  #   MP
    HIGH_FIO2                      =  6  #   MP
    HIGH_PRESSURE                  =  7  # HP
    HIGH_RR                        =  8  #   MP
    HIGH_VTE                       =  9  #   MP
    LOW_VTE                        = 10  #   MP
    HIGH_VTI                       = 11  #   MP
    LOW_VTI                        = 12  #   MP
    INTENTIONAL_STOP               = 13  # HP
    LOW_BATTERY                    = 14  # HP (LP) if AC power isn't (is) connected
    LOW_FIO2                       = 15  # HP
    OCCLUSION                      = 16  # HP
    HIGH_PEEP                      = 17  # HP
    LOW_PEEP                       = 18  # HP
    AC_POWER_DISCONNECTION         = 19  #   MP
    BATTERY_FAULT_SRVC             = 20  #   MP
    BATTERY_CHARGE                 = 21  #   MP
    AIR_FAIL                       = 22  # HP
    O2_FAIL                        = 23  # HP
    PRESSURE_SENSOR_FAULT          = 24  # HP
    ARDUINO_FAIL                   = 25  # HP

class CMD_MAP(Enum):
    GENERAL           =  CMD_GENERAL
    SET_TIMEOUT       =  CMD_SET_TIMEOUT
    SET_MODE          =  CMD_SET_MODE
    SET_THRESHOLD_MIN =  ALARM_CODES
    SET_THRESHOLD_MAX =  ALARM_CODES

class BL_STATES(Enum):
    IDLE            =  1
    CALIBRATION     =  2
    BUFF_PREFILL    =  3
    BUFF_FILL       =  4
    BUFF_LOADED     =  5
    BUFF_PRE_INHALE =  6
    INHALE          =  7
    PAUSE           =  8
    EXHALE_FILL     =  9
    EXHALE          = 10
    STOP            = 11
    BUFF_PURGE      = 12
    BUFF_FLUSH      = 13
