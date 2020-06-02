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
    GENERAL                =  1
    SET_DURATION           =  2
    SET_MODE               =  3
    SET_THRESHOLD_MIN      =  4
    SET_THRESHOLD_MAX      =  5
    SET_VALVE              =  6
    SET_PID                =  7
    SET_TARGET_PC_AC       =  8
    SET_TARGET_PC_AC_PRVC  =  9
    SET_TARGET_PC_PSV      =  10
    SET_TARGET_CPAP        =  11
    SET_TARGET_TEST        =  12
    SET_TARGET_CURRENT     =  13
    GET_TARGETS            =  14


@unique
class CMD_GENERAL(Enum):
    START =  1
    STOP  =  2
    RESET =  3
    STANDBY = 4

# Taken from the FSM doc. Correct as of 1400 on 20200417
@unique
class CMD_SET_DURATION(Enum):
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

@unique
class VENTILATION_MODE(Enum):
    UNKNOWN    = 0
    PC_AC      = 1
    PC_AC_PRVC = 2
    PC_PSV     = 3
    CPAP       = 4
    TEST       = 5
    PURGE      = 6
    FLUSH      = 7
    CURRENT    = 100   # not settable

@unique
class CMD_SET_VALVE(Enum):
    AIR_IN_ENABLE = 1
    O2_IN_ENABLE  = 2
    PURGE_ENABLE  = 3
    INHALE_DUTY_CYCLE = 4
    INHALE_OPEN_MIN = 5
    INHALE_OPEN_MAX = 6
    INHALE_TRIGGER_ENABLE = 7
    EXHALE_TRIGGER_ENABLE = 8
    INHALE_TRIGGER_THRESHOLD = 9
    EXHALE_TRIGGER_THRESHOLD = 10

@unique
class CMD_SET_PID(Enum):
    KP = 1
    KI = 2
    KD = 3
    TARGET_FINAL_PRESSURE = 4
    NSTEPS = 5

@unique
class CMD_SET_TARGET(Enum):
    INSPIRATORY_PRESSURE = 1
    RESPIRATORY_RATE     = 2 
    IE_RATIO             = 3
    VOLUME               = 4
    PEEP                 = 5
    FIO2                 = 6
    INHALE_TIME          = 7

@unique
class ALARM_TYPE(Enum):
    PRIORITY_LOW    = 1
    PRIORITY_MEDIUM = 2
    PRIORITY_HIGH   = 3

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
    GENERAL                =  CMD_GENERAL
    SET_DURATION           =  CMD_SET_DURATION
    SET_MODE               =  VENTILATION_MODE
    SET_VALVE              =  CMD_SET_VALVE
    SET_PID                =  CMD_SET_PID
    SET_TARGET_PC_AC       =  CMD_SET_TARGET
    SET_TARGET_PC_AC_PRVC  =  CMD_SET_TARGET
    SET_TARGET_PC_PSV      =  CMD_SET_TARGET
    SET_TARGET_CPAP        =  CMD_SET_TARGET
    SET_TARGET_TEST        =  CMD_SET_TARGET
    SET_TARGET_CURRENT     =  CMD_SET_TARGET
    SET_THRESHOLD_MIN      =  ALARM_CODES
    SET_THRESHOLD_MAX      =  ALARM_CODES
    GET_TARGETS            =  VENTILATION_MODE

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
    STANDBY         = 14

@unique
class PAYLOAD_TYPE(IntEnum):
    UNSET      = 0
    DATA       = 1
    READBACK   = 2
    CYCLE      = 3
    THRESHOLDS = 4
    CMD        = 5
    ALARM      = 6
    DEBUG      = 7
    IVT        = 8
    LOGMSG     = 9
    TARGET     = 10
    BATTERY    = 11

class HEVVersionError(Exception):
    pass

@dataclass
class PayloadFormat():
    # class variables excluded from init args and output dict
    _RPI_VERSION: ClassVar[int]       = field(default=0xAC, init=False, repr=False)
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
            7: DebugFormat,
            8: IVTFormat,
            9: LogMsgFormat,
            10: TargetFormat,
            11: BatteryFormat
        }
        ReturnType = DATA_TYPE_TO_CLASS[rec_bytes[5]]
        payload_obj = ReturnType()
        payload_obj.fromByteArray(rec_bytes)
        return payload_obj

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
    def checkVersion(self):
        if self._RPI_VERSION != self.version : 
            raise HEVVersionError('Version Mismatch', "PI:", self._RPI_VERSION, "uC:", self.version)

    def getSize(self) -> int:
        return len(self.byteArray)

    def getType(self) -> Any:
        return self.payload_type if isinstance(self.payload_type, IntEnum) else PAYLOAD_TYPE(self.payload_type)
    
    def getDict(self) -> Dict:
        return {k: v.name if isinstance(v, IntEnum) or isinstance(v, Enum) else v for k, v in asdict(self).items()}


# =======================================
# fast data payload
# =======================================
@dataclass
class DataFormat(PayloadFormat):
    # subclass dataformat
    _dataStruct = Struct("<BIBBHfHffffHfHHfff")
    payload_type: PAYLOAD_TYPE = PAYLOAD_TYPE.DATA
    # subclass member variables
    fsm_state: BL_STATES          = BL_STATES.IDLE
    pressure_air_supply: int      = 0
    pressure_air_regulated: float = 0.0
    pressure_o2_supply: int       = 0
    pressure_o2_regulated: float  = 0.0
    pressure_buffer: float        = 0.0
    pressure_inhale: float        = 0.0
    pressure_patient: float       = 0.0
    temperature_buffer: int       = 0
    pressure_diff_patient: float  = 0.0
    ambient_pressure: int         = 0
    ambient_temperature: int      = 0
    airway_pressure: float        = 0.0
    flow: float                   = 0.0
    volume: float                 = 0.0

    # for receiving DataFormat from microcontroller
    # fill the struct from a byteArray, 
    def fromByteArray(self, byteArray):
        #logging.info(f"bytearray size {len(byteArray)} ")
        #logging.info(binascii.hexlify(byteArray))
        tmp_state = 0
        tmp_payload_type = 0
        (self.version,
        self.timestamp,
        tmp_payload_type,
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

        self.checkVersion()
        self.payload_type = PAYLOAD_TYPE(tmp_payload_type)
        self._byteArray = byteArray


# =======================================
# readback data payload
# =======================================
@dataclass
class ReadbackFormat(PayloadFormat):
    _dataStruct = Struct("<BIBHHHHHHHHHHHffBBBBBBBBBBBff")
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

    valve_air_in: float           = 0.0
    valve_o2_in: float            = 0.0
    valve_inhale: int             = 0
    valve_exhale: int             = 0
    valve_purge: int              = 0
    ventilation_mode: int         = VENTILATION_MODE.PC_AC

    valve_inhale_percent: int     = 0
    valve_exhale_percent: int     = 0
    valve_air_in_enable: int      = 0
    valve_o2_in_enable: int       = 0
    valve_purge_enable: int       = 0
    inhale_trigger_enable: int    = 0
    exhale_trigger_enable: int    = 0
    peep: float                   = 0.0
    inhale_exhale_ratio: float    = 0.0

    # for receiving DataFormat from microcontroller
    # fill the struct from a byteArray, 
    def fromByteArray(self, byteArray):
        #logging.info(f"bytearray size {len(byteArray)} ")
        #logging.info(binascii.hexlify(byteArray))
        tmp_mode = 0
        tmp_payload_type = 0
        (self.version,
        self.timestamp,
        tmp_payload_type,
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
        tmp_mode,
        self.valve_inhale_percent,
        self.valve_exhale_percent,
        self.valve_air_in_enable,
        self.valve_o2_in_enable,
        self.valve_purge_enable,
        self.inhale_trigger_enable,
        self.exhale_trigger_enable,
        self.peep,
        self.inhale_exhale_ratio) = self._dataStruct.unpack(byteArray) 

        self.checkVersion()
        self.ventilation_mode = VENTILATION_MODE(tmp_mode)
        self.payload_type = PAYLOAD_TYPE(tmp_payload_type)
        self._byteArray = byteArray


# =======================================
# cycle data payload
# =======================================
@dataclass
class CycleFormat(PayloadFormat):
    # subclass dataformat
    _dataStruct = Struct("<BIBffffffffffffffHHB")
    payload_type: PAYLOAD_TYPE = PAYLOAD_TYPE.CYCLE

    respiratory_rate: float          = 0.0
    tidal_volume: float              = 0.0
    exhaled_tidal_volume: float      = 0.0
    inhaled_tidal_volume: float      = 0.0
    minute_volume: float             = 0.0
    exhaled_minute_volume: float     = 0.0
    inhaled_minute_volume: float     = 0.0
    lung_compliance: float           = 0.0
    static_compliance: float         = 0.0
    inhalation_pressure: float       = 0.0
    peak_inspiratory_pressure: float = 0.0
    plateau_pressure: float          = 0.0
    mean_airway_pressure: float      = 0.0
    fi02_percent: float              = 0.0
    apnea_index: int                 = 0
    apnea_time: int                  = 0
    mandatory_breath: int            = 0

    # for receiving DataFormat from microcontroller
    # fill the struct from a byteArray, 
    def fromByteArray(self, byteArray):
        #logging.info(f"bytearray size {len(byteArray)} ")
        #logging.info(binascii.hexlify(byteArray))
        tmp_payload_type = 0
        (self.version,
        self.timestamp,
        tmp_payload_type,
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

        self.checkVersion()
        self.payload_type = PAYLOAD_TYPE(tmp_payload_type)
        self._byteArray = byteArray

# =======================================
# debug data payload; this can change
# =======================================
@dataclass
class DebugFormat(PayloadFormat):
    # subclass dataformat
    _dataStruct = Struct("<BIBfffffffff")
    payload_type: PAYLOAD_TYPE = PAYLOAD_TYPE.DEBUG

    kp              : float = 0.0
    ki              : float = 0.0
    kd              : float = 0.0
    target_pressure : float = 0.0 ##
    process_pressure: float = 0.0 
    valve_duty_cycle: float = 0.0 
    proportional    : float = 0.0 
    integral        : float = 0.0 ##
    derivative      : float = 0.0

    # for receiving DataFormat from microcontroller
    # fill the struct from a byteArray, 
    def fromByteArray(self, byteArray):
        tmp_payload_type = 0
        (self.version,
        self.timestamp,
        tmp_payload_type,
        self.kp              , 
        self.ki              ,
        self.kd              ,
        self.target_pressure ,
        self.process_pressure,
        self.valve_duty_cycle,
        self.proportional    ,
        self.integral        ,
        self.derivative      
        ) = self._dataStruct.unpack(byteArray) 

        self.checkVersion()
        self.payload_type = PAYLOAD_TYPE(tmp_payload_type)
        self._byteArray = byteArray

# =======================================
# thresholds eata payload
# =======================================
# TODO

# =======================================
# IVT data payload
# =======================================
@dataclass
class IVTFormat(PayloadFormat):
    _dataStruct = Struct("<BIBffffffffffbbbbbf")
    payload_type: PAYLOAD_TYPE = PAYLOAD_TYPE.IVT

    inhale_current : float = 0.0
    exhale_current : float = 0.0
    purge_current  : float = 0.0
    air_in_current : float = 0.0
    o2_in_current  : float = 0.0
    inhale_voltage : float = 0.0
    exhale_voltage : float = 0.0
    purge_voltage  : float = 0.0
    air_in_voltage : float = 0.0
    o2_in_voltage  : float = 0.0
    inhale_i2caddr : int = 0.0
    exhale_i2caddr : int = 0.0
    purge_i2caddr  : int = 0.0
    air_in_i2caddr : int = 0.0
    o2_in_i2caddr  : int = 0.0
    system_temp    : float = 0.0
    # for receiving DataFormat from microcontroller
    # fill the struct from a byteArray, 
    def fromByteArray(self, byteArray):
        #logging.info(f"bytearray size {len(byteArray)} ")
        #logging.info(binascii.hexlify(byteArray))
        tmp_payload_type = 0
        (self.version,
        self.timestamp,
        tmp_payload_type,
        self.inhale_current ,
        self.exhale_current ,
        self.purge_current  ,
        self.air_in_current ,
        self.o2_in_current  ,
        self.inhale_voltage ,
        self.exhale_voltage ,
        self.purge_voltage  ,
        self.air_in_voltage ,
        self.o2_in_voltage  ,
        self.inhale_i2caddr ,
        self.exhale_i2caddr ,
        self.purge_i2caddr  ,
        self.air_in_i2caddr ,
        self.o2_in_i2caddr  ,
        self.system_temp    
        ) = self._dataStruct.unpack(byteArray) 

        self.checkVersion()
        self.payload_type = PAYLOAD_TYPE(tmp_payload_type)
        self._byteArray = byteArray

# =======================================
# Target data payload
# =======================================
@dataclass
class TargetFormat(PayloadFormat):
    _dataStruct = Struct("<BIBBffffffH")
    payload_type: PAYLOAD_TYPE = PAYLOAD_TYPE.TARGET

    mode                  : int   = 0
    inspiratory_pressure  : float = 0.0
    ie_ratio              : float = 0.0
    volume                : float = 0.0
    respiratory_rate      : float = 0.0
    peep                  : float = 0.0
    fiO2                  : float = 0.0
    inhale_time           : int   = 0 

    # for receiving DataFormat from microcontroller
    # fill the struct from a byteArray, 
    def fromByteArray(self, byteArray):
        #logging.info(f"bytearray size {len(byteArray)} ")
        #logging.info(binascii.hexlify(byteArray))
        tmp_payload_type = 0
        tmp_mode = 0
        (self.version,
        self.timestamp,
        tmp_payload_type,
        tmp_mode                 , 
        self.inspiratory_pressure, 
        self.ie_ratio            , 
        self.volume              , 
        self.respiratory_rate    , 
        self.peep                , 
        self.fiO2                , 
        self.inhale_time         ) = self._dataStruct.unpack(byteArray) 

        self.checkVersion()
        self.payload_type = PAYLOAD_TYPE(tmp_payload_type)
        self.mode         = VENTILATION_MODE(tmp_mode)
        self._byteArray = byteArray
# =======================================
# Log msg payload
# =======================================
@dataclass
class LogMsgFormat(PayloadFormat):
    _dataStruct = Struct("<BIB50s")
    payload_type: PAYLOAD_TYPE = PAYLOAD_TYPE.LOGMSG

    message   : str = ""
    # for receiving DataFormat from microcontroller
    # fill the struct from a byteArray, 
    def fromByteArray(self, byteArray):
        #logging.info(f"bytearray size {len(byteArray)} ")
        #logging.info(binascii.hexlify(byteArray))
        tmp_payload_type = 0
        tmp_chararray  = ""
        (self.version,
        self.timestamp,
        tmp_payload_type,
        tmp_chararray) = self._dataStruct.unpack(byteArray) 

        self.checkVersion()
        self.message = tmp_chararray.decode('ascii')
        self.payload_type = PAYLOAD_TYPE(tmp_payload_type)
        self._byteArray = byteArray

# =======================================
# BATTERY data payload
# =======================================
@dataclass
class BatteryFormat(PayloadFormat):
    _dataStruct = Struct("<BIBbbbbbbb")
    payload_type: PAYLOAD_TYPE = PAYLOAD_TYPE.BATTERY

    bat       : int = 0
    ok        : int = 0
    alarm     : int = 0
    rdy2buf   : int = 0
    bat85     : int = 0
    prob_elec : int = 0
    dummy     : int = 0

    # fill the struct from a byteArray, 
    def fromByteArray(self, byteArray):
        tmp_payload_type = 0
        (self.version,
        self.timestamp,
        tmp_payload_type,
        self.bat       ,
        self.ok        ,
        self.alarm     ,
        self.rdy2buf   ,
        self.bat85     ,
        self.prob_elec ,
        self.dummy     ,
        ) = self._dataStruct.unpack(byteArray) 

        self.checkVersion()
        self.payload_type = PAYLOAD_TYPE(tmp_payload_type)
        self._byteArray = byteArray
        
# =======================================
# cmd type payload
# =======================================
@dataclass
class CommandFormat(PayloadFormat):
    _dataStruct = Struct("<BIBBBf")
    payload_type: PAYLOAD_TYPE = PAYLOAD_TYPE.CMD

    cmd_type: int = 0
    cmd_code: int = 0
    param: float  = 0.0

    def fromByteArray(self, byteArray):
        tmp_payload_type = 0
        (self.version,
        self.timestamp,
        tmp_payload_type,
        self.cmd_type,
        self.cmd_code,
        self.param) = self._dataStruct.unpack(byteArray) 

        self.checkVersion()
        self.payload_type = PAYLOAD_TYPE(tmp_payload_type)
        self._byteArray = byteArray


# =======================================
# alarm type payload
# =======================================
@dataclass
class AlarmFormat(PayloadFormat):
    _dataStruct = Struct("<BIBBBf")
    payload_type: PAYLOAD_TYPE = PAYLOAD_TYPE.ALARM

    alarm_type: int = 0
    alarm_code: ALARM_CODES = ALARM_CODES.UNKNOWN
    param: float = 0.0
        
    def __eq__(self, other):
        return  (self.alarm_type == other.alarm_type) and (self.alarm_code == other.alarm_code)

    def fromByteArray(self, byteArray):
        alarm = 0
        priority = 0
        tmp_payload_type = 0
        (self.version,
        self.timestamp,
        tmp_payload_type,
        priority,
        alarm,
        self.param) = self._dataStruct.unpack(byteArray)

        self.checkVersion()
        self.alarm_type = ALARM_TYPE(priority)
        self.alarm_code = ALARM_CODES(alarm)
        self.payload_type = PAYLOAD_TYPE(tmp_payload_type)
        self._byteArray = byteArray
