from struct import Struct 
from enum import Enum, auto, unique
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class payloadType(Enum):
    payloadAlarm = auto()
    payloadCmd   = auto()
    payloadData  = auto()
    payloadUnset = auto()

# VERSIONING
# change version in baseFormat for all data
# i.e. if and of dataFormat, commandFormat or AlarmFormat change
# then change the RPI_VERSION

class BaseFormat():
    def __init__(self):
        self._RPI_VERSION = 0xA0
        self._byteArray = None
        self._type = payloadType.payloadUnset
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
class dataFormat(BaseFormat):

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
        self._dataStruct = Struct("<BBHHHHHHHHHBBBBBB")
        self._byteArray = None
        self._type = payloadType.payloadData


        # make all zero to start with
        self._version = 0
        self._fsm_state = 0
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
        
    # for receiving dataFormat from microcontroller
    # fill the struct from a byteArray, 
    def fromByteArray(self, byteArray):
        self._byteArray = byteArray
        (self._version,
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


    # for sending dataFormat to microcontroller
    # this is for completeness.  Probably we never send this data
    # to the microcontroller
    def toByteArray(self):
        # since pi is sender
        self._version = self._RPI_VERSION

        self._byteArray = self._dataStruct.pack(
            self._RPI_VERSION,
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
class commandFormat(BaseFormat):
    def __init__(self, cmdCode=0, param=0):
        super().__init__()
        self._dataStruct = Struct("<BBI")
        self._byteArray = None
        self._type = payloadType.payloadCmd

        self._version = 0
        self._cmdCode = cmdCode
        self._param = param
        self.toByteArray()

    # manage direct reading and writing of member variables
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
    "version" : {self._version},
    "cmdCode" : {self._cmdCode},
    "param"   : {self._param}
}}"""
        
    def fromByteArray(self, byteArray):
        self._byteArray = byteArray
        (self._version,
        self._cmdCode,
        self._param) = self._dataStruct.unpack(self._byteArray) 

    def toByteArray(self):
        # since pi is sender
        self._byteArray = self._dataStruct.pack(
            self._RPI_VERSION,
            self._cmdCode,
            self._param
        )

    def getDict(self):
        data = {
            "version" : self._version,
            "cmdCode" : self._cmdCode,
            "param"   : self._param
        }
        return data
        
@unique
class command_codes(Enum):
    CMD_START = 0x1
    CMD_STOP  = 0x2
    
# =======================================
# alarm type payload
# =======================================
class alarmFormat(BaseFormat):
    def __init__(self):
        super().__init__()
        self._dataStruct = Struct("<BBI")
        self._byteArray = None
        self._type = payloadType.payloadAlarm

        self._version = 0
        self._alarmCode   = 0
        self._param = 0

    def __repr__(self):
        return f"""{{
    "version"   : {self._version},
    "alarmCode" : {self._alarmCode},
    "param"     : {self._param}
}}"""
        
    def fromByteArray(self, byteArray):
        self._byteArray = byteArray
        (self._version,
        self._alarmCode,
        self._param) = self._dataStruct.unpack(self._byteArray)

    def toByteArray(self):
        self._byteArray = self._dataStruct.pack(
            self._RPI_VERSION,
            self._alarmCode,
            self._param
        ) 
    
    def getDict(self):
        data = {
            "version"   : self._version,
            "alarmCode" : self._alarmCode,
            "param"     : self._param
        }
        return data

@unique
class alarm_codes(Enum):
    # Taken from safety doc. Correct as of 1400 on 20200416
    APNEA                          = 1  # HP
    CHECK_VALVE_EXHALE             = 2  # HP
    CHECK_P_PATIENT                = 3  # HP
    EXPIRATION_SENSE_FAULT_OR_LEAK = 4  #  MP
    EXPIRATION_VALVE_LEAK          = 5  #  MP
    HIGH_FIO2                      = 6  #  MP
    HIGH_PRESSURE                  = 7  # HP
    HIGH_RR                        = 8  #  MP
    HIGH_VTE                       = 9  #  MP
    LOW_VTE                        = 10 #  MP
    HIGH_VTI                       = 11 #  MP
    LOW_VTI                        = 12 #  MP
    INTENTIONAL_STOP               = 13 # HP
    LOW_BATTERY                    = 14 # HP (LP) if AC power isn't (is) connected
    LOW_FIO2                       = 15 # HP
    OCCLUSION                      = 16 # HP
    HIGH_PEEP                      = 17 # HP
    LOW_PEEP                       = 18 # HP
    AC_POWER_DISCONNECTION         = 19 #  MP
    BATTERY_FAULT_SRVC             = 20 #  MP
    BATTERY_CHARGE                 = 21 #  MP
    AIR_FAIL                       = 22 # HP
    O2_FAIL                        = 23 # HP
    PRESSURE_SENSOR_FAULT          = 24 # HP
    ARDUINO_FAIL                   = 25 # HP
