from struct import Struct 
from enum import Enum, IntEnum, auto, unique
from dataclasses import dataclass, asdict, field, fields
from typing import Any, ClassVar, Dict
import logging
import binascii
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# VERSIONING
# change version in PayloadFormat for all data
# i.e. if and of DataFormat, CommandFormat or AlarmFormat change
# then change the RPI_VERSION

# =======================================
# Enum definitions
# =======================================
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
    HEV_MODE_PS   = 1
    HEV_MODE_CPAP = 2
    HEV_MODE_PRVC = 3
    HEV_MODE_TEST = 4

@unique
class ALARM_TYPE(Enum):
    LP   = 1
    MP   = 2
    HP   = 3

@unique
class ALARM_CODES(Enum):
    UNKNOWN                        =  0
    APNEA                          =  1  # HP
    CHECK_VALVE_EXHALE             =  2  # HP
    CHECK_P_PATIENT                =  3  # HP
    EXPIRATION_SENSE_FAULT_OR_LEAK =  4  #   MP
    EXPIRATION_VALVE_LEAK          =  5  #   MP
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

@unique
class BL_STATES(Enum):
    UNKNOWN         =  0
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

@unique
class PAYLOAD_TYPE(IntEnum):
    UNSET      = 0
    DATA       = 1
    READBACK   = 2
    CYCLE      = 3
    THRESHOLDS = 4
    CMD        = 5
    ALARM      = 6

@dataclass
class PayloadFormat():
    # class variables excluded from init args and output dict
    _RPI_VERSION: ClassVar[int]       = field(default=0xA2, init=False, repr=False)
    _dataStruct:  ClassVar[Any]       = field(default=Struct("<BIB"), init=False, repr=False)
    _byteArray:   ClassVar[bytearray] = field(default=None, init=False, repr=False)

    # Meta information
    version: int               = 0
    timestamp: int             = 0
    payload_type: PAYLOAD_TYPE = PAYLOAD_TYPE.UNSET

    @classmethod
    def fromByteArray(cls, rec_bytes):
        """Automatically determine which subclass to initialise as"""
        DATA_TYPE_TO_CLASS = {
            1: DataFormat,
            2: ReadbackFormat,
            3: CycleFormat,
            #4: ThresholdFormat,
            5: CommandFormat,
            6: AlarmFormat,
        }
        ReturnType = DATA_TYPE_TO_CLASS[rec_bytes[5]]
        data = ReturnType._dataStruct.unpack(rec_bytes)
        return ReturnType(*data)

    @property
    def byteArray(self) -> bytearray:
        self.toByteArray()
        return self._byteArray

    @byteArray.setter
    def byteArray(self, byte_array) -> None:
        self._byteArray = byte_array

    def toByteArray(self) -> None:
        self.version = self._RPI_VERSION
        self._byteArray = self._dataStruct.pack(*[
            v.value if isinstance(v, IntEnum) or isinstance(v, Enum) else v
            for v in asdict(self).values()
        ])

    # check for mismatch between pi and microcontroller version
    def checkVersion(self) -> bool:
        return self._RPI_VERSION == self.version

    def getSize(self) -> int:
        return len(self.byteArray)

    def getType(self) -> Any:
        return self.payload_type
    
    def getDict(self) -> Dict:
        return {k: v.name if isinstance(v, IntEnum) or isinstance(v, Enum) else v for k, v in asdict(self).items()}


# =======================================
# fast data payload
# =======================================
@dataclass
class DataFormat(PayloadFormat):
    # subclass dataformat
    _dataStruct = Struct("<BIBBHHHHHHHHHHHfff")
    payload_type: PAYLOAD_TYPE = PAYLOAD_TYPE.DATA

    # subclass member variables
    fsm_state: BL_STATES        = BL_STATES.IDLE
    pressure_air_supply: int    = 0
    pressure_air_regulated: int = 0
    pressure_o2_supply: int     = 0
    pressure_o2_regulated: int  = 0
    pressure_buffer: int        = 0
    pressure_inhale: int        = 0
    pressure_patient: int       = 0
    temperature_buffer: int     = 0
    pressure_diff_patient: int  = 0
    ambient_pressure: int       = 0
    ambient_temperature: int    = 0
    airway_pressure: float      = 0
    flow: float                 = 0
    volume: float               = 0


    # for receiving DataFormat from microcontroller
    # fill the struct from a byteArray, 
    def fromByteArray(self, byteArray):
        #logging.info(f"bytearray size {len(byteArray)} ")
        #logging.info(binascii.hexlify(byteArray))
        tmp_state = 0
        (self.version,
        self.timestamp,
        self.payload_type,
        tmp_state,
        self.pressure_air_supply,
        self.pressure_air_regulated,
        self.pressure_o2_supply,
        self.pressure_o2_regulated,
        self.pressure_buffer,
        self.pressure_inhale,
        self.pressure_patient,
        self.temperature_buffer,
        self.pressure_diff_patient,
        self.ambient_pressure,
        self.ambient_temperature,
        self.airway_pressure,
        self.flow,
        self.volume) = self._dataStruct.unpack(byteArray) 
        self.fsm_state = BL_STATES(tmp_state)
        self._byteArray = byteArray


# =======================================
# readback data payload
# =======================================
@dataclass
class ReadbackFormat(PayloadFormat):
    _dataStruct = Struct("<BIBHHHHHHHHHHHBBBBBBBBBBBBBBf")
    payload_type: PAYLOAD_TYPE = PAYLOAD_TYPE.READBACK

    duration_calibration: int     = 0
    duration_buff_purge: int      = 0
    duration_buff_flush: int      = 0
    duration_buff_prefill: int    = 0
    duration_buff_fill: int       = 0
    duration_buff_loaded: int     = 0
    duration_buff_pre_inhale: int = 0
    duration_inhale: int          = 0
    duration_pause: int           = 0
    duration_exhale_fill: int     = 0
    duration_exhale: int          = 0

    valve_air_in: int             = 0
    valve_o2_in: int              = 0
    valve_inhale: int             = 0
    valve_exhale: int             = 0
    valve_purge: int              = 0
    ventilation_mode: int         = 0 #CMD_SET_MODE.HEV_MODE_PS

    valve_inhale_percent: int     = 0
    valve_exhale_percent: int     = 0
    valve_air_in_enable: int      = 0
    valve_o2_in_enable: int       = 0
    valve_purge_enable: int       = 0
    inhale_trigger_enable: int    = 0
    exhale_trigger_enable: int    = 0
    peep: int                     = 0
    inhale_exhate_ratio: float    = 0.0

    # for receiving DataFormat from microcontroller
    # fill the struct from a byteArray, 
    def fromByteArray(self, byteArray):
        #logging.info(f"bytearray size {len(byteArray)} ")
        #logging.info(binascii.hexlify(byteArray))
        (self.version,
        self.timestamp,
        self.payload_type,
        self.duration_calibration,
        self.duration_buff_purge,
        self.duration_buff_flush,
        self.duration_buff_prefill,
        self.duration_buff_fill,
        self.duration_buff_loaded,
        self.duration_buff_pre_inhale,
        self.duration_inhale,
        self.duration_pause,
        self.duration_exhale_fill,
        self.duration_exhale,
        self.valve_air_in,
        self.valve_o2_in,
        self.valve_inhale,
        self.valve_exhale,
        self.valve_purge,
        self.ventilation_mode,
        self.valve_inhale_percent,
        self.valve_exhale_percent,
        self.valve_air_in_enable,
        self.valve_o2_in_enable,
        self.valve_purge_enable,
        self.inhale_trigger_enable,
        self.exhale_trigger_enable,
        self.peep,
        self.inhale_exhate_ratio) = self._dataStruct.unpack(byteArray) 
        self._byteArray = byteArray


# =======================================
# cycle data payload
# =======================================
@dataclass
class CycleFormat(PayloadFormat):
    # subclass dataformat
    _dataStruct = Struct("<BIBfffffffffHHHHBHHB")
    payload_type: PAYLOAD_TYPE = PAYLOAD_TYPE.CYCLE

    respiratory_rate: float        = 0.0
    tidal_volume: float            = 0.0
    exhaled_tidal_volume: float    = 0.0
    inhaled_tidal_volume: float    = 0.0
    minute_volume: float           = 0.0
    exhaled_minute_volume: float   = 0.0
    inhaled_minute_volume: float   = 0.0
    lung_compliance: float         = 0.0
    static_compliance: float       = 0.0
    inhalation_pressure: int       = 0
    peak_inspiratory_pressure: int = 0
    plateau_pressure: int          = 0
    mean_airway_pressure: int      = 0
    fi02_percent: int              = 0
    apnea_index: int               = 0
    apnea_time: int                = 0
    mandatory_breath: int          = 0

    # for receiving DataFormat from microcontroller
    # fill the struct from a byteArray, 
    def fromByteArray(self, byteArray):
        #logging.info(f"bytearray size {len(byteArray)} ")
        #logging.info(binascii.hexlify(byteArray))
        (self.version,
        self.timestamp,
        self.payload_type,
        self.respiratory_rate,
        self.tidal_volume,
        self.exhaled_tidal_volume,
        self.inhaled_tidal_volume,
        self.minute_volume,
        self.exhaled_minute_volume,
        self.inhaled_minute_volume,
        self.lung_compliance,
        self.static_compliance,
        self.inhalation_pressure,
        self.peak_inspiratory_pressure,
        self.plateau_pressure,
        self.mean_airway_pressure,
        self.fi02_percent,
        self.apnea_index,
        self.apnea_time,
        self.mandatory_breath) = self._dataStruct.unpack(byteArray) 
        self._byteArray = byteArray


# =======================================
# thresholds eata payload
# =======================================
# TODO

# =======================================
# cmd type payload
# =======================================
@dataclass
class CommandFormat(PayloadFormat):
    _dataStruct = Struct("<BIBBBI")
    payload_type: PAYLOAD_TYPE = PAYLOAD_TYPE.CMD

    cmd_type: int = 0
    cmd_code: int = 0
    param: int    = 0

    def fromByteArray(self, byteArray):
        (self.version,
        self.timestamp,
        self.payload_type,
        self.cmd_type,
        self.cmd_code,
        self.param) = self._dataStruct.unpack(byteArray) 
        self._byteArray = byteArray


# =======================================
# alarm type payload
# =======================================
@dataclass
class AlarmFormat(PayloadFormat):
    _dataStruct = Struct("<BIBBBI")
    payload_type: PAYLOAD_TYPE = PAYLOAD_TYPE.ALARM

    alarm_type: int = 0
    alarm_code: ALARM_CODES = ALARM_CODES.UNKNOWN
    param: int = 0

    def fromByteArray(self, byteArray):
        alarm = 0
        (self.version,
        self.timestamp,
        self.payload_type,
        self.alarm_type,
        alarm,
        self.param) = self._dataStruct.unpack(byteArray)
        self.alarm_code = ALARM_CODES(alarm)
        self._byteArray = byteArray
