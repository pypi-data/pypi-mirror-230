import struct
import enum


class Commands(enum.IntEnum):
    PING = 0x00
    WRITE = 0x01
    WRITE_ACK = 0x80 | 0x01
    READ = 0x02,
    EEPROM_WRITE = 0x03
    SCAN_SENSORS = 0x04
    REBOOT = 0x05
    RESET_ENC = 0x06
    HARD_RESET = 0x17
    ERROR_CLEAR = 0x18
    BL_JUMP = 0x30
    SYNC_WRITE = 0x40 | 0x01
    BULK_WRITE = 0x20 | 0x01
    BULK_READ = 0x20 | 0x02
    ACK = 0x80
    __EEPROM_WRITE_ACK = -1


class OperationMode():
    PWM = 0
    Position = 1
    Velocity = 2
    Torque = 3


class Colors():
    NO_COLOR = 0
    RED = 1
    GREEN = 2
    BLUE = 3
    WHITE = 4
    YELLOW = 5
    CYAN = 6
    MAGENTA = 7
    ORANGE = 8
    PURPLE = 9
    PINK = 10
    AMBER = 11
    TEAL = 12
    INDIGO = 13


Index = enum.IntEnum('Index', [
    'Header',
    'DeviceID',
    'DeviceFamily',
    'PackageSize',
    'Command',
    'Status',
    'HardwareVersion',
    'SoftwareVersion',
    'Baudrate',
    'OperationMode',
    'TorqueEnable',
    'TunerEnable',
    'TunerMethod',
    'OutputShaftCPR',
    'OutputShaftRPM',
    'UserIndicator',
    'MinimumPositionLimit',
    'MaximumPositionLimit',
    'TorqueLimit',
    'VelocityLimit',
    'PositionFF',
    'VelocityFF',
    'TorqueFF',
    'PositionDeadband',
    'VelocityDeadband',
    'TorqueDeadband',
    'PositionOutputLimit',
    'VelocityOutputLimit',
    'TorqueOutputLimit',
    'PositionScalerGain',
    'PositionPGain',
    'PositionIGain',
    'PositionDGain',
    'VelocityScalerGain',
    'VelocityPGain',
    'VelocityIGain',
    'VelocityDGain',
    'TorqueScalerGain',
    'TorquePGain',
    'TorqueIGain',
    'TorqueDGain',
    'SetPosition',
    'SetVelocity',
    'SetTorque',
    'SetDutyCycle',
    'Buzzer_1',
    'Buzzer_2',
    'Buzzer_3',
    'Buzzer_4',
    'Buzzer_5',
    'Servo_1',
    'Servo_2',
    'Servo_3',
    'Servo_4',
    'Servo_5',
    'RGB_1',
    'RGB_2',
    'RGB_3',
    'RGB_4',
    'RGB_5',
    'PresentPosition',
    'PresentVelocity',
    'MotorCurrent',
    'AnalogPort',
    'Button_1',
    'Button_2',
    'Button_3',
    'Button_4',
    'Button_5',
    'Light_1',
    'Light_2',
    'Light_3',
    'Light_4',
    'Light_5',
    'Joystick_1',
    'Joystick_2',
    'Joystick_3',
    'Joystick_4',
    'Joystick_5',
    'Distance_1',
    'Distance_2',
    'Distance_3',
    'Distance_4',
    'Distance_5',
    'QTR_1',
    'QTR_2',
    'QTR_3',
    'QTR_4',
    'QTR_5',
    'Pot_1',
    'Pot_2',
    'Pot_3',
    'Pot_4',
    'Pot_5',
    'IMU_1',
    'IMU_2',
    'IMU_3',
    'IMU_4',
    'IMU_5',
    'CRCValue',
    ], start=0)


class _Data():
    def __init__(self, index, var_type, rw=True, value=0):
        self.__index = index
        self.__type = var_type
        self.__size = struct.calcsize(self.__type)
        self.__value = value
        self.__rw = rw

    def value(self, value=None):
        if value is None:
            return self.__value
        elif self.__rw:
            if len(self.__type) > 1:
                self.__value = list(struct.unpack('<' + self.__type, struct.pack('<' + self.__type, *value)))
            else:
                self.__value = struct.unpack('<' + self.__type, struct.pack('<' + self.__type, value))[0]

    def index(self) -> enum.IntEnum:
        return self.__index

    def size(self) -> int:
        return self.__size

    def type(self) -> str:
        return self.__type
