from smd._internals import (_Data, Index, Commands,
                            OperationMode, Colors)
import struct
from crccheck.crc import Crc32Mpeg2 as CRC32
import serial
import time
from packaging.version import parse as parse_version


class InvalidIndexError(BaseException):
    pass


class Red():
    _HEADER = 0x55
    _PRODUCT_TYPE = 0xBA
    _PACKAGE_ESSENTIAL_SIZE = 6
    _STATUS_KEY_LIST = ['EEPROM', 'Software Version', 'Hardware Version']

    def __init__(self, ID: int) -> bool:

        self.__ack_size = 0
        self._config = None
        self._fw_file = None
        self.vars = [
            _Data(Index.Header, 'B', False, 0x55),
            _Data(Index.DeviceID, 'B'),
            _Data(Index.DeviceFamily, 'B', False, self.__class__._PRODUCT_TYPE),
            _Data(Index.PackageSize, 'B'),
            _Data(Index.Command, 'B'),
            _Data(Index.Status, 'B'),
            _Data(Index.HardwareVersion, 'I'),
            _Data(Index.SoftwareVersion, 'I'),
            _Data(Index.Baudrate, 'I'),
            _Data(Index.OperationMode, 'B'),
            _Data(Index.TorqueEnable, 'B'),
            _Data(Index.TunerEnable, 'B'),
            _Data(Index.TunerMethod, 'B'),
            _Data(Index.OutputShaftCPR, 'f'),
            _Data(Index.OutputShaftRPM, 'f'),
            _Data(Index.UserIndicator, 'B'),
            _Data(Index.MinimumPositionLimit, 'i'),
            _Data(Index.MaximumPositionLimit, 'i'),
            _Data(Index.TorqueLimit, 'H'),
            _Data(Index.VelocityLimit, 'H'),
            _Data(Index.PositionFF, 'f'),
            _Data(Index.VelocityFF, 'f'),
            _Data(Index.TorqueFF, 'f'),
            _Data(Index.PositionDeadband, 'f'),
            _Data(Index.VelocityDeadband, 'f'),
            _Data(Index.TorqueDeadband, 'f'),
            _Data(Index.PositionOutputLimit, 'f'),
            _Data(Index.VelocityOutputLimit, 'f'),
            _Data(Index.TorqueOutputLimit, 'f'),
            _Data(Index.PositionScalerGain, 'f'),
            _Data(Index.PositionPGain, 'f'),
            _Data(Index.PositionIGain, 'f'),
            _Data(Index.PositionDGain, 'f'),
            _Data(Index.VelocityScalerGain, 'f'),
            _Data(Index.VelocityPGain, 'f'),
            _Data(Index.VelocityIGain, 'f'),
            _Data(Index.VelocityDGain, 'f'),
            _Data(Index.TorqueScalerGain, 'f'),
            _Data(Index.TorquePGain, 'f'),
            _Data(Index.TorqueIGain, 'f'),
            _Data(Index.TorqueDGain, 'f'),
            _Data(Index.SetPosition, 'f'),
            _Data(Index.SetVelocity, 'f'),
            _Data(Index.SetTorque, 'f'),
            _Data(Index.SetDutyCycle, 'f'),
            _Data(Index.Buzzer_1, 'B'),
            _Data(Index.Buzzer_2, 'B'),
            _Data(Index.Buzzer_3, 'B'),
            _Data(Index.Buzzer_4, 'B'),
            _Data(Index.Buzzer_5, 'B'),
            _Data(Index.Servo_1, 'B'),
            _Data(Index.Servo_2, 'B'),
            _Data(Index.Servo_3, 'B'),
            _Data(Index.Servo_4, 'B'),
            _Data(Index.Servo_5, 'B'),
            _Data(Index.RGB_1, 'B'),
            _Data(Index.RGB_2, 'B'),
            _Data(Index.RGB_3, 'B'),
            _Data(Index.RGB_4, 'B'),
            _Data(Index.RGB_5, 'B'),
            _Data(Index.PresentPosition, 'f'),
            _Data(Index.PresentVelocity, 'f'),
            _Data(Index.MotorCurrent, 'f'),
            _Data(Index.AnalogPort, 'H'),
            _Data(Index.Button_1, 'B'),
            _Data(Index.Button_2, 'B'),
            _Data(Index.Button_3, 'B'),
            _Data(Index.Button_4, 'B'),
            _Data(Index.Button_5, 'B'),
            _Data(Index.Light_1, 'H'),
            _Data(Index.Light_2, 'H'),
            _Data(Index.Light_3, 'H'),
            _Data(Index.Light_4, 'H'),
            _Data(Index.Light_5, 'H'),
            _Data(Index.Joystick_1, 'ffB'),
            _Data(Index.Joystick_2, 'ffB'),
            _Data(Index.Joystick_3, 'ffB'),
            _Data(Index.Joystick_4, 'ffB'),
            _Data(Index.Joystick_5, 'ffB'),
            _Data(Index.Distance_1, 'H'),
            _Data(Index.Distance_2, 'H'),
            _Data(Index.Distance_3, 'H'),
            _Data(Index.Distance_4, 'H'),
            _Data(Index.Distance_5, 'H'),
            _Data(Index.QTR_1, 'B'),
            _Data(Index.QTR_2, 'B'),
            _Data(Index.QTR_3, 'B'),
            _Data(Index.QTR_4, 'B'),
            _Data(Index.QTR_5, 'B'),
            _Data(Index.Pot_1, 'H'),
            _Data(Index.Pot_2, 'H'),
            _Data(Index.Pot_3, 'H'),
            _Data(Index.Pot_4, 'H'),
            _Data(Index.Pot_5, 'H'),
            _Data(Index.IMU_1, 'ff'),
            _Data(Index.IMU_2, 'ff'),
            _Data(Index.IMU_3, 'ff'),
            _Data(Index.IMU_4, 'ff'),
            _Data(Index.IMU_5, 'ff'),
            _Data(Index.CRCValue, 'I')
        ]

        if ID > 255 or ID < 0:
            raise ValueError("Device ID can not be higher than 254 or lower than 0!")
        else:
            self.vars[Index.DeviceID].value(ID)

    def get_ack_size(self):
        return self.__ack_size

    def set_variables(self, index_list=[], value_list=[], ack=False):
        self.vars[Index.Command].value(Commands.WRITE_ACK if ack else Commands.WRITE)

        fmt_str = '<' + ''.join([var.type() for var in self.vars[:6]])
        for index, value in zip(index_list, value_list):
            self.vars[int(index)].value(value)
            fmt_str += 'B' + self.vars[int(index)].type()

        self.__ack_size = struct.calcsize(fmt_str)

        struct_out = list(struct.pack(fmt_str, *[*[var.value() for var in self.vars[:6]], *[val for pair in zip(index_list, [self.vars[int(index)].value() for index in index_list]) for val in pair]]))

        struct_out[int(Index.PackageSize)] = len(struct_out) + self.vars[int(Index.CRCValue)].size()

        self.vars[Index.CRCValue].value(CRC32.calc(struct_out))

        return bytes(struct_out) + struct.pack('<' + self.vars[Index.CRCValue].type(), self.vars[Index.CRCValue].value())

    def get_variables(self, index_list=[]):
        self.vars[Index.Command].value(Commands.READ)

        fmt_str = '<' + ''.join([var.type() for var in self.vars[:6]])
        fmt_str += 'B' * len(index_list)

        self.__ack_size = struct.calcsize(fmt_str + self.vars[Index.CRCValue].type()) \
            + struct.calcsize('<' + ''.join(self.vars[idx].type() for idx in index_list))

        struct_out = list(struct.pack(fmt_str, *[*[var.value() for var in self.vars[:6]], *[int(idx) for idx in index_list]]))

        struct_out[int(Index.PackageSize)] = len(struct_out) + self.vars[Index.CRCValue].size()

        self.vars[Index.CRCValue].value(CRC32.calc(struct_out))

        return bytes(struct_out) + struct.pack('<' + self.vars[Index.CRCValue].type(), self.vars[Index.CRCValue].value())

    def reboot(self):
        self.vars[Index.Command].value(Commands.REBOOT)
        fmt_str = '<' + ''.join([var.type() for var in self.vars[:6]])
        struct_out = list(struct.pack(fmt_str, *[var.value() for var in self.vars[:6]]))
        struct_out[int(Index.PackageSize)] = len(struct_out) + self.vars[Index.CRCValue].size()
        self.vars[Index.CRCValue].value(CRC32.calc(struct_out))
        self.__ack_size = 0

        return bytes(struct_out) + struct.pack('<' + self.vars[Index.CRCValue].type(), self.vars[Index.CRCValue].value())

    def factory_reset(self):
        self.vars[Index.Command].value(Commands.HARD_RESET)
        fmt_str = '<' + ''.join([var.type() for var in self.vars[:6]])
        struct_out = list(struct.pack(fmt_str, *[var.value() for var in self.vars[:6]]))
        struct_out[int(Index.PackageSize)] = len(struct_out) + self.vars[Index.CRCValue].size()
        self.vars[Index.CRCValue].value(CRC32.calc(struct_out))
        self.__ack_size = 0

        return bytes(struct_out) + struct.pack('<' + self.vars[Index.CRCValue].type(), self.vars[Index.CRCValue].value())

    def EEPROM_write(self, ack=False):
        self.vars[Index.Command].value(Commands.__EEPROM_WRITE_ACK if ack else Commands.EEPROM_WRITE)
        fmt_str = '<' + ''.join([var.type() for var in self.vars[:6]])
        struct_out = list(struct.pack(fmt_str, *[var.value() for var in self.vars[:6]]))
        struct_out[int(Index.PackageSize)] = len(struct_out) + self.vars[Index.CRCValue].size()
        self.vars[Index.CRCValue].value(CRC32.calc(struct_out))
        self.__ack_size = struct.calcsize(fmt_str + self.vars[Index.CRCValue].type())
        return bytes(struct_out) + struct.pack('<' + self.vars[Index.CRCValue].type(), self.vars[Index.CRCValue].value())

    def ping(self):
        self.vars[Index.Command].value(Commands.PING)
        fmt_str = '<' + ''.join([var.type() for var in self.vars[:6]])
        struct_out = list(struct.pack(fmt_str, *[var.value() for var in self.vars[:6]]))
        struct_out[int(Index.PackageSize)] = len(struct_out) + self.vars[Index.CRCValue].size()
        self.vars[Index.CRCValue].value(CRC32.calc(struct_out))
        self.__ack_size = struct.calcsize(fmt_str + self.vars[Index.CRCValue].type())
        return bytes(struct_out) + struct.pack('<' + self.vars[Index.CRCValue].type(), self.vars[Index.CRCValue].value())

    def reset_encoder(self):
        self.vars[Index.Command].value(Commands.RESET_ENC)
        fmt_str = '<' + ''.join([var.type() for var in self.vars[:6]])
        struct_out = list(struct.pack(fmt_str, *[var.value() for var in self.vars[:6]]))
        struct_out[int(Index.PackageSize)] = len(struct_out) + self.vars[Index.CRCValue].size()
        self.vars[Index.CRCValue].value(CRC32.calc(struct_out))
        self.__ack_size = struct.calcsize(fmt_str + self.vars[Index.CRCValue].type())
        return bytes(struct_out) + struct.pack('<' + self.vars[Index.CRCValue].type(), self.vars[Index.CRCValue].value())

    def scan_sensors(self):
        self.vars[Index.Command].value(Commands.SCAN_SENSORS)
        fmt_str = '<' + ''.join([var.type() for var in self.vars[:6]])
        struct_out = list(struct.pack(fmt_str, *[var.value() for var in self.vars[:6]]))
        struct_out[int(Index.PackageSize)] = len(struct_out) + self.vars[Index.CRCValue].size()
        self.vars[Index.CRCValue].value(CRC32.calc(struct_out))
        self.__ack_size = struct.calcsize(fmt_str + self.vars[Index.CRCValue].type())
        return bytes(struct_out) + struct.pack('<' + self.vars[Index.CRCValue].type(), self.vars[Index.CRCValue].value())

    def enter_bootloader(self):
        self.vars[Index.Command].value(Commands.BL_JUMP)
        fmt_str = '<' + ''.join([var.type() for var in self.vars[:6]])
        struct_out = list(struct.pack(fmt_str, *[var.value() for var in self.vars[:6]]))
        struct_out[int(Index.PackageSize)] = len(struct_out) + self.vars[Index.CRCValue].size()
        self.vars[Index.CRCValue].value(CRC32.calc(struct_out))
        self.__ack_size = 0
        return bytes(struct_out) + struct.pack('<' + self.vars[Index.CRCValue].type(), self.vars[Index.CRCValue].value())

    def update_driver_id(self, id):
        self.vars[Index.Command].value(Commands.WRITE)
        fmt_str = '<' + ''.join([var.type() for var in self.vars[:6]])
        fmt_str += 'B' + self.vars[int(Index.DeviceID)].type()
        struct_out = list(struct.pack(fmt_str, *[*[var.value() for var in self.vars[:6]], int(Index.DeviceID), id]))
        struct_out[int(Index.PackageSize)] = len(struct_out) + self.vars[int(Index.CRCValue)].size()
        self.vars[Index.CRCValue].value(CRC32.calc(struct_out))
        return bytes(struct_out) + struct.pack('<' + self.vars[Index.CRCValue].type(), self.vars[Index.CRCValue].value())


class Master():
    _BROADCAST_ID = 0xFF

    def __init__(self, portname, baudrate=115200) -> None:
        self.__attached_drivers = []
        self.__driver_list = [Red(255)] * 256
        if baudrate > 12500000 or baudrate < 3053:
            raise ValueError('Baudrate must be between 3.053 KBits/s and 12.5 MBits/s.')
        else:
            self.__baudrate = baudrate
            self.__post_sleep = (10 / self.__baudrate) * 3
            self.__ph = serial.Serial(port=portname, baudrate=self.__baudrate, timeout=0.1)

    def __del__(self):
        try:
            self.__ph.reset_input_buffer()
            self.__ph.reset_output_buffer()
            self.__ph.close()
        except Exception as e:
            raise e

    def __write_bus(self, data):
        self.__ph.write(data)

    def __read_bus(self, size) -> bytes:
        self.__ph.reset_input_buffer()
        return self.__ph.read(size=size)

    def attached(self):
        return self.__attached_drivers

    def update_driver_baudrate(self, id: int, br: int):
        """Update the baudrate of the driver with
        given device ID. Following the method, the master
        baudrate must be updated accordingly to initiate a
        communication line with the board.

        Args:
            id (int): The device ID of the driver
            br (int): New baudrate value

        Raises:
            ValueError: Baudrate is not valid
        """

        if (br < 3053) or (br > 12500000):
            raise ValueError("{br} is not in acceptable range!")

        self.set_variables(id, [[Index.Baudrate, br]])
        time.sleep(self.__post_sleep)
        self.eeprom_write(id)
        time.sleep(self.__post_sleep)
        self.reboot(id)

    def update_master_baudrate(self, br: int):
        """ Update the master serial port baudrate.

        Args:
            br (int): Baudrate in range [3053, 12500000]

        Raises:
            ValueError: Invalid baudrate
            e: Unspecific exception
        """

        if (br < 3053) or (br > 12500000):
            raise ValueError("{br} is not in acceptable range!")

        try:
            self.__ph.reset_input_buffer()
            self.__ph.reset_output_buffer()
            settings = self.__ph.get_settings()
            self.__ph.close()
            settings['baudrate'] = br
            self.__ph.apply_settings(settings)
            self.__ph.open()

            self.__post_sleep = (10 / br) * 3

        except Exception as e:
            raise e

    def attach(self, driver: Red):
        """ Attach a SMD driver to the master to define access to it.

        Args:
            driver (Red): Driver to be attached
        """
        self.__driver_list[driver.vars[Index.DeviceID].value()] = driver

    def detach(self, id: int):
        """ Detach the SMD driver with given ID from master driver list.

        Args:
            id (int): The device ID of the driver to be detached.

        Raises:
            ValueError: Device ID is not valid
        """
        if (id < 0) or (id > 255):
            raise ValueError("{} is not a valid ID!".format(id))

        self.__driver_list[id] = Red(255)

    def set_variables(self, id: int, idx_val_pairs=[], ack=False):
        """ Set variables on the driver with given ID
        with a list containing [Index, value] sublists. Index
        is the parameter index and the value is the value attached to it.

        Args:
            id (int):  The device ID of the driver
            idx_val_pairs (list, optional): List containing Index, value pairs. Defaults to [].
            ack (bool, optional): Get acknowledge from the driver. Defaults to False.

        Raises:
            ValueError: Device ID is not valid
            IndexError: The given list is empty
            Exception: Error raised from operation on the list except empty list

        Returns:
            list | None: Return the list of written values if ack is True, otherwise None.
        """

        if (id < 0) or (id > 254):
            raise ValueError("{} is not a valid ID!".format(id))

        if len(idx_val_pairs) == 0:
            raise IndexError("Given id, value pair list is empty!")

        try:
            index_list = [pair[0] for pair in idx_val_pairs]
            value_list = [pair[1] for pair in idx_val_pairs]
        except Exception as e:
            raise Exception(" Raised {} with args {}".format(e, e.args))

        self.__write_bus(self.__driver_list[id].set_variables(index_list, value_list, ack))
        if ack:
            if self.__read_ack(id):
                return [self.__driver_list[id].vars[index].value() for index in index_list]
        time.sleep(self.__post_sleep)
        return None

    def get_variables(self, id: int, index_list: list):
        """ Get variables from the driver with respect to given list

        Args:
            id (int): The device ID of the driver
            index_list (list): A list containing the Indexes to read

        Raises:
            ValueError: Device ID is not valid
            IndexError: The given list is empty

        Returns:
            list | None: Return the list of read values if any, otherwise None.
        """

        if (id < 0) or (id > 254):
            raise ValueError("{} is not a valid ID!".format(id))

        if len(index_list) == 0:
            raise IndexError("Given index list is empty!")

        self.__write_bus(self.__driver_list[id].get_variables(index_list))
        time.sleep(self.__post_sleep)
        if self.__read_ack(id):
            return [self.__driver_list[id].vars[index].value() for index in index_list]
        else:
            return None

    def __parse(self, data: bytes):
        """ Parse the data which has passed the CRC check

        Args:
            data (bytes): Input data package in bytes
        """

        id = data[Index.DeviceID]
        data = data[6:-4]

        i = 0
        while i < len(data):
            fmt_str = '<B' + self.__driver_list[id].vars[data[i]].type()

            sdata = data[i: i + self.__driver_list[id].vars[data[i]].size() + 1]
            unpacked = list(struct.unpack(fmt_str, sdata))

            self.__driver_list[id].vars[unpacked[0]].value(unpacked[1] if len(unpacked) <= 2 else unpacked[1::])
            i += self.__driver_list[id].vars[data[i]].size() + 1

    def __read_ack(self, id: int) -> bool:
        """ Read acknowledge data from the driver with given ID.

        Args:
            id (int): The device ID of the driver

        Returns:
            bool: Return True if acknowledge is read and correct.
        """

        ret = self.__read_bus(self.__driver_list[id].get_ack_size())
        if len(ret) == self.__driver_list[id].get_ack_size():
            if CRC32.calc(ret[:-4]) == struct.unpack('<I', ret[-4:])[0]:
                if ret[int(Index.PackageSize)] > 10:
                    self.__parse(ret)
                    return True
                else:
                    return True  # Ping package
            else:
                return False
        else:
            return False

    def set_variables_sync(self, index: Index, id_val_pairs=[]):
        dev = Red(self.__class__._BROADCAST_ID)
        dev.vars[Index.Command].value(Commands.SYNC_WRITE)

        fmt_str = '<' + ''.join([var.type() for var in dev.vars[:6]])
        struct_out = list(struct.pack(fmt_str, *[var.value() for var in dev.vars[:6]]))

        fmt_str += 'B'
        struct_out += list(struct.pack('<B', int(index)))

        for pair in id_val_pairs:
            fmt_str += 'B'
            struct_out += list(struct.pack('<B', pair[0]))
            struct_out += list(struct.pack('<' + dev.vars[index].type(), pair[1]))

        struct_out[int(Index.PackageSize)] = len(struct_out) + dev.vars[Index.CRCValue].size()
        dev.vars[Index.CRCValue].value(CRC32.calc(struct_out))

        self.__write_bus(bytes(struct_out) + struct.pack('<' + dev.vars[Index.CRCValue].type(), dev.vars[Index.CRCValue].value()))
        time.sleep(self.__post_sleep)

    def __set_variables_bulk(self, id: int):
        raise NotImplementedError()

    def __get_variables_bulk(self, id: int):
        raise NotImplementedError()

    def scan(self) -> list:
        """ Scan the serial port and find drivers.

        Returns:
            list: Connected drivers.
        """
        self.__ph.reset_input_buffer()
        self.__ph.reset_output_buffer()
        self.__ph.timeout = 0.025
        connected = []
        for id in range(255):
            self.attach(Red(id))
            if self.ping(id):
                connected.append(id)
            else:
                self.detach(id)
        self.__ph.timeout = 0.1
        self.__attached_drivers = connected
        return connected

    def reboot(self, id: int):
        """ Reboot the driver.

        Args:
            id (int): The device ID of the driver.
        """
        self.__write_bus(self.__driver_list[id].reboot())
        time.sleep(self.__post_sleep)

    def factory_reset(self, id: int):
        """ Clear the EEPROM config of the driver.

        Args:
            id (int): The device ID of the driver.
        """
        self.__write_bus(self.__driver_list[id].factory_reset())
        time.sleep(self.__post_sleep)

    def eeprom_write(self, id: int, ack=False):
        """ Save the config to the EEPROM.

        Args:
            id (int): The device ID of the driver.
            ack (bool, optional): Wait for acknowledge. Defaults to False.

        Returns:
            bool | None: Return True if ack returns
                         Return False if ack does not return or incorrect
                         Return None if ack is not requested.
        """
        self.__write_bus(self.__driver_list[id].EEPROM_write(ack=ack))
        time.sleep(self.__post_sleep)

        if ack:
            if self.__read_ack(id):
                return True
            else:
                return False
        return None

    def ping(self, id: int) -> bool:
        """ Ping the driver with given ID.

        Args:
            id (int): The device ID of the driver.

        Returns:
            bool: Return True if device replies otherwise False.
        """
        self.__write_bus(self.__driver_list[id].ping())
        time.sleep(self.__post_sleep)

        if self.__read_ack(id):
            return True
        else:
            return False

    def reset_encoder(self, id: int):
        """ Reset the encoder.

        Args:
            id (int): The device ID of the driver.
        """
        self.__write_bus(self.__driver_list[id].reset_encoder())
        time.sleep(self.__post_sleep)

    def scan_sensors(self, id: int) -> list:
        """ Get the list of sensor IDs which are connected to the driver.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list: List of the protocol IDs of the connected sensors otherwise None.
        """

        _ID_OFFSETS = [[1, 64], [6, 69], [11, 45], [16, 74], [21, 79], [26, 85], [31, 50], [36, 89], [41, 55], [46, 94]]
        self.__write_bus(self.__driver_list[id].scan_sensors())
        time.sleep(2)
        self.__write_bus(self.__driver_list[id].scan_sensors())
        ret = self.__read_bus(18)
        if len(ret) == 18:
            if CRC32.calc(ret[:-4]) == struct.unpack('<I', ret[-4:])[0]:
                data = struct.unpack('<Q', ret[6:-4])[0]
                addrs = [i for i in range(64) if (data & (1 << i)) == (1 << i)]
                result = []
                for addr in addrs:
                    result.append(Index(addr - _ID_OFFSETS[int(addr / 5)][0] + _ID_OFFSETS[int(addr / 5)][1]))
                return result
        else:
            return None

    def enter_bootloader(self, id: int):
        """ Put the driver into bootloader mode.

        Args:
            id (int): The device ID of the driver.
        """

        self.__write_bus(self.__driver_list[id].enter_bootloader())
        time.sleep(self.__post_sleep)

    def get_driver_info(self, id: int):
        """ Get hardware and software versions from the driver

        Args:
            id (int): The device ID of the driver.

        Returns:
            dict | None: Dictionary containing versions or None.
        """
        st = dict()
        data = self.get_variables(id, [Index.HardwareVersion, Index.SoftwareVersion])
        if data is not None:
            ver = list(struct.pack('<I', data[0]))
            st['HardwareVersion'] = "{1}.{2}.{3}".format(*ver[::-1])
            ver = list(struct.pack('<I', data[1]))
            st['SoftwareVersion'] = "{1}.{2}.{3}".format(*ver[::-1])

            self.__driver_list[id]._config = st
            return st
        else:
            return None

    def update_driver_id(self, id: int, id_new: int):
        """ Update the device ID of the driver

        Args:
            id (int): The device ID of the driver
            id_new (int): New device ID

        Raises:
            ValueError: Current or updating device IDs are not valid
        """
        if (id < 0) or (id > 254):
            raise ValueError("{} is not a valid ID!".format(id))

        if (id_new < 0) or (id_new > 254):
            raise ValueError("{} is not a valid ID argument!".format(id_new))

        self.__write_bus(self.__driver_list[id].update_driver_id(id_new))
        time.sleep(self.__post_sleep)
        self.eeprom_write(id_new)
        time.sleep(self.__post_sleep)
        self.reboot(id)

    def enable_torque(self, id: int, en: bool):
        """ Enable power to the motor of the driver.

        Args:
            id (int): The device ID of the driver
            en (bool): Enable. True enables the torque.
        """

        self.set_variables(id, [[Index.TorqueEnable, en]])
        time.sleep(self.__post_sleep)

    def pid_tuner(self, id: int):
        """ Start PID auto-tuning routine. This routine will estimate
        PID coefficients for position and velocity control operation modes.

        Args:
            id (int): The device ID of the driver.
        """
        self.set_variables(id, [[Index. TunerEnable, 1]])

    def set_operation_mode(self, id: int, mode: OperationMode):
        """ Set the operation mode of the driver.

        Args:
            id (int): The device ID of the driver.
            mode (OperationMode): One of the PWM, Position, Velocity, Torque modes.
        """

        self.set_variables(id, [[Index.OperationMode, mode]])
        time.sleep(self.__post_sleep)

    def get_operation_mode(self, id: int):
        """ Get the current operation mode from the driver.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the operation mode, otherwise None.
        """
        return self.get_variables(id, [Index.OperationMode])

    def set_shaft_cpr(self, id: int, cpr: float):
        """ Set the count per revolution (CPR) of the motor output shaft.

        Args:
            id (int): The device ID of the driver.
            cpr (float): The CPR value of the output shaft/
        """
        self.set_variables(id, [[Index.OutputShaftCPR, cpr]])
        time.sleep(self.__post_sleep)

    def set_shaft_rpm(self, id: int, rpm: float):
        """ Set the revolution per minute (RPM) value of the output shaft at 12V rating.

        Args:
            id (int): The device ID of the driver.
            rpm (float): The RPM value of the output shaft at 12V
        """
        self.set_variables(id, [[Index.OutputShaftRPM, rpm]])
        time.sleep(self.__post_sleep)

    def set_user_indicator(self, id: int):
        """ Set the user indicator color for 5 seconds. The user indicator color is cyan.

        Args:
            id (int): The device ID of the driver.
        """
        self.set_variables(id, [[Index.UserIndicator, 1]])
        time.sleep(self.__post_sleep)

    def set_position_limits(self, id: int, plmin: int, plmax: int):
        """ Set the position limits of the motor in terms of encoder ticks.
        Default for min is -2,147,483,648 and for max is 2,147,483,647.
        The torque ise disabled if the value is exceeded so a tolerence
        factor should be taken into consideration when setting this values. 

        Args:
            id (int): The device ID of the driver.
            plmin (int): The minimum position limit.
            plmax (int): The maximum position limit.
        """
        self.set_variables(id, [[Index.MinimumPositionLimit, plmin], [Index.MaximumPositionLimit, plmax]])
        time.sleep(self.__post_sleep)

    def get_position_limits(self, id: int):
        """ Get the position limits of the motor in terms of encoder ticks.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the position limits, otherwise None.
        """
        return self.get_variables(id, [Index.MinimumPositionLimit, Index.MaximumPositionLimit])

    def set_torque_limit(self, id: int, tl: int):
        """ Set the torque limit of the driver in terms of milliamps (mA).
        Torque is disabled after a timeout if the current drawn is over the
        given torque limit. Default torque limit is 65535.

        Args:
            id (int): The device ID of the driver.
            tl (int): New torque limit (mA)
        """
        self.set_variables(id, [[Index.TorqueLimit, tl]])
        time.sleep(self.__post_sleep)

    def get_torque_limit(self, id: int):
        """ Get the torque limit from the driver in terms of milliamps (mA).

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the torque limit, otherwise None.
        """
        return self.get_variables(id, [Index.TorqueLimit])

    def set_velocity_limit(self, id: int, vl: int):
        """ Set the velocity limit for the motor output shaft in terms of RPM. The velocity limit
        applies only in velocity mode. Default velocity limit is 65535.

        Args:
            id (int): The device ID of the driver.
            vl (int): New velocity limit (RPM)
        """
        self.set_variables(id, [[Index.VelocityLimit, vl]])
        time.sleep(self.__post_sleep)

    def get_velocity_limit(self, id: int):
        """ Get the velocity limit from the driver in terms of RPM.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the velocity limit, otherwise None.
        """
        return self.get_variables(id, [Index.VelocityLimit])

    def set_position(self, id: int, sp: int):
        """ Set the desired setpoint for the position control in terms of encoder ticks.

        Args:
            id (int): The device ID of the driver.
            sp (int | float): Position control setpoint.
        """
        self.set_variables(id, [[Index.SetPosition, sp]])
        time.sleep(self.__post_sleep)

    def get_position(self, id: int):
        """ Get the current position of the motor from the driver in terms of encoder ticks.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the current position, otherwise None.
        """
        return self.get_variables(id, [Index.PresentPosition])

    def set_velocity(self, id: int, sp: float):
        """ Set the desired setpoint for the velocity control in terms of RPM.

        Args:
            id (int): The device ID of the driver.
            sp (int | float): Velocity control setpoint.
        """
        self.set_variables(id, [[Index.SetVelocity, sp]])
        time.sleep(self.__post_sleep)

    def get_velocity(self, id: int):
        """ Get the current velocity of the motor output shaft from the driver in terms of RPM.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the current velocity, otherwise None.
        """
        return self.get_variables(id, [Index.PresentVelocity])

    def set_torque(self, id: int, sp: float):
        """ Set the desired setpoint for the torque control in terms of milliamps (mA).

        Args:
            id (int): The device ID of the driver.
            sp (int | float): Torque control setpoint.
        """
        self.set_variables(id, [[Index.SetTorque, sp]])
        time.sleep(self.__post_sleep)

    def get_torque(self, id: int):
        """ Get the current drawn from the motor from the driver in terms of milliamps (mA).

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the current, otherwise None.
        """
        return self.get_variables(id, [Index.MotorCurrent])

    def set_duty_cycle(self, id: int, pct: float):
        """ Set the duty cycle to the motor for PWM control mode in terms of percentage.
        Negative values will change the motor direction.

        Args:
            id (int): The device ID of the driver.
            pct (int | float): Duty cycle percentage.
        """
        self.set_variables(id, [[Index.SetDutyCycle, pct]])
        time.sleep(self.__post_sleep)

    def get_analog_port(self, id: int):
        """ Get the ADC values from the analog port of the device with
        10 bit resolution. The value is in range [0, 4095].

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list containing the ADC conversion of the port, otherwise None.
        """
        return self.get_variables(id, [Index.AnalogPort])

    def set_control_parameters_position(self, id: int, p=None, i=None, d=None, db=None, ff=None, ol=None):
        """ Set the control block parameters for position control mode.
        Only assigned parameters are written, None's are ignored. The default
        max output limit is 950.

        Args:
            id (int): The device ID of the driver.
            p (float): Proportional gain. Defaults to None.
            i (float): Integral gain. Defaults to None.
            d (float): Derivative gain. Defaults to None.
            db (float): Deadband (of the setpoint type). Defaults to None.
            ff (float): Feedforward. Defaults to None.
            ol (float): Maximum output limit. Defaults to None.
        """
        index_list = [Index.PositionPGain, Index.PositionIGain, Index.PositionDGain, Index.PositionDeadband, Index.PositionFF, Index.PositionOutputLimit]
        val_list = [p, i, d, db, ff, ol]

        self.set_variables(id, [list(pair) for pair in zip(index_list, val_list) if pair[1] is not None])
        time.sleep(self.__post_sleep)

    def get_control_parameters_position(self, id: int):
        """ Get the position control block parameters.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list [P, I, D, FF, DB, OUTPUT_LIMIT], otherwise None.
        """

        return self.get_variables(id, [Index.PositionPGain, Index.PositionIGain, Index.PositionDGain, Index.PositionDeadband, Index.PositionFF, Index.PositionOutputLimit])

    def set_control_parameters_velocity(self, id: int, p=None, i=None, d=None, db=None, ff=None, ol=None):
        """ Set the control block parameters for velocity control mode.
        Only assigned parameters are written, None's are ignored. The default
        max output limit is 950.

        Args:
            id (int): The device ID of the driver.
            p (float): Proportional gain. Defaults to None.
            i (float): Integral gain. Defaults to None.
            d (float): Derivative gain. Defaults to None.
            db (float): Deadband (of the setpoint type). Defaults to None.
            ff (float): Feedforward. Defaults to None.
            ol (float): Maximum output limit. Defaults to None.
        """
        index_list = [Index.VelocityPGain, Index.VelocityIGain, Index.VelocityDGain, Index.VelocityDeadband, Index.VelocityFF, Index.VelocityOutputLimit]
        val_list = [p, i, d, db, ff, ol]

        self.set_variables(id, [list(pair) for pair in zip(index_list, val_list) if pair[1] is not None])
        time.sleep(self.__post_sleep)

    def get_control_parameters_velocity(self, id: int):
        """ Get the velocity control block parameters.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list [P, I, D, FF, DB, OUTPUT_LIMIT], otherwise None.
        """
        return self.get_variables(id, [Index.VelocityPGain, Index.VelocityIGain, Index.VelocityDGain, Index.VelocityDeadband, Index.VelocityFF, Index.VelocityOutputLimit])

    def set_control_parameters_torque(self, id: int, p=None, i=None, d=None, db=None, ff=None, ol=None):
        """ Set the control block parameters for torque control mode.
        Only assigned parameters are written, None's are ignored. The default
        max output limit is 950.

        Args:
            id (int): The device ID of the driver.
            p (float): Proportional gain. Defaults to None.
            i (float): Integral gain. Defaults to None.
            d (float): Derivative gain. Defaults to None.
            db (float): Deadband (of the setpoint type). Defaults to None.
            ff (float): Feedforward. Defaults to None.
            ol (float): Maximum output limit. Defaults to None.
        """
        index_list = [Index.TorquePGain, Index.TorqueIGain, Index.TorqueDGain, Index.TorqueDeadband, Index.TorqueFF, Index.TorqueOutputLimit]
        val_list = [p, i, d, db, ff, ol]

        self.set_variables(id, [list(pair) for pair in zip(index_list, val_list) if pair[1] is not None])
        time.sleep(self.__post_sleep)

    def get_control_parameters_torque(self, id: int):
        """ Get the torque control block parameters.

        Args:
            id (int): The device ID of the driver.

        Returns:
            list | None: Returns the list [P, I, D, FF, DB, OUTPUT_LIMIT], otherwise None.
        """
        return self.get_variables(id, [Index.TorquePGain, Index.TorqueIGain, Index.TorqueDGain, Index.TorqueDeadband, Index.TorqueFF, Index.TorqueOutputLimit])

    def get_button(self, id: int, index: Index):
        """ Get the button module data with given index.

        Args:
            id (int): The device ID of the driver.
            index (Index): The index of the button module.

        Raises:
            InvalidIndexError: Index is not a button module index

        Returns:
            int: Returns the button state
        """
        if (index < Index.Button_1) or (index > Index.Button_5):
            raise InvalidIndexError()

        ret = self.get_variables(id, [index])
        if ret is None:
            return ret
        return ret[0]

    def get_light(self, id: int, index: Index):
        """ Get the ambient light module data with given index.

        Args:
            id (int): The device ID of the driver.
            index (Index): The index of the ambient light module.

        Raises:
            InvalidIndexError: Index is not a light module index

        Returns:
            float: Returns the ambient light measurement (in lux)
        """
        if (index < Index.Light_1) or (index > Index.Light_5):
            raise InvalidIndexError()

        ret = self.get_variables(id, [index])
        if ret is None:
            return ret
        return ret[0]

    def set_buzzer(self, id: int, index: Index, en: bool):
        """ Enable/disable the buzzer module with given index.

        Args:
            id (int): The device ID of the driver.
            index (Index): The index of the buzzer module.
            en (bool): Enable = 1, Disable = 0

        Raises:
            InvalidIndexError: Index is not a buzzer module index
        """
        if (index < Index.Buzzer_1) or (index > Index.Buzzer_5):
            raise InvalidIndexError()
        return self.set_variables(id, [[Index, en]])

    def get_joystick(self, id: int, index: Index):
        """ Get the joystick module data with given index.

        Args:
            id (int): The device ID of the driver.
            index (Index): The index of the joystick module.

        Raises:
            InvalidIndexError: Index is not a joystick module index

        Returns:
            list: Returns the joystick module analogs and button data
        """
        if (index < Index.Joystick_1) or (index > Index.Joystick_5):
            raise InvalidIndexError()

        ret = self.get_variables(id, [index])
        if ret is None:
            return ret
        return ret[0]

    def get_distance(self, id: int, index: Index):
        """ Get the ultrasonic distance module data with given index.

        Args:
            id (int): The device ID of the driver.
            index (Index): The index of the ultrasonic distance module.

        Raises:
            InvalidIndexError: Index is not a ultrasonic distance module index

        Returns:
            int: Returns the distance from the ultrasonic distance module (in cm)
        """
        if (index < Index.Distance_1) or (index > Index.Distance_5):
            raise InvalidIndexError()

        ret = self.get_variables(id, [index])
        if ret is None:
            return ret
        return ret[0]

    def get_qtr(self, id: int, index: Index):
        """ Get the qtr module data with given index.

        Args:
            id (int): The device ID of the driver.
            index (Index): The index of the qtr module.

        Raises:
            InvalidIndexError: Index is not a qtr module index

        Returns:
            list: Returns qtr module data: [Left(bool), Middle(bool), Right(bool)]
        """
        if (index < Index.QTR_1) or (index > Index.QTR_5):
            raise InvalidIndexError()

        data = self.get_variables(id, [index])
        if data is not None:
            return [data[0] & (1 << i) for i in range(3)]
        else:
            return None

    def set_servo(self, id: int, index: Index, val: int):
        """ Move servo module to a position.

        Args:
            id (int): The device ID of the driver.
            index (Index): The index of the servo module.
            val (int): The value to write to the servo

        Raises:
            ValueError: Value should be in range [0, 255]
            InvalidIndexError: Index is not a servo module index
        """
        if val < 0 or val > 255:
            raise ValueError()
        if (index < Index.Servo_1) or (index > Index.Servo_5):
            raise InvalidIndexError()
        return self.set_variables(id, [[Index, val]])

    def get_potantiometer(self, id: int, index: Index):
        """ Get the potantiometer module data with given index.

        Args:
            id (int): The device ID of the driver.
            index (Index): The index of the potantiometer module.

        Raises:
            InvalidIndexError: Index is not a potantiometer module index

        Returns:
            int: Returns the ADC conversion from the potantiometer module
        """
        if (index < Index.Pot_1) or (index > Index.Pot_5):
            raise InvalidIndexError()

        ret = self.get_variables(id, [index])
        if ret is None:
            return ret
        return ret[0]

    def set_rgb(self, id: int, index: Index, color: Colors):
        """ Set the colour emitted from the RGB module.

        Args:
            id (int): The device ID of the driver.
            index (Index): The index of the RGB module.
            color (Colors): Color for RGB from Colors class

        Raises:
            ValueError: Color is invalid
            InvalidIndexError: Index is not a RGB module index
        """
        if color < Colors.NO_COLOR or color > Colors.INDIGO:
            raise ValueError()
        if (index < Index.RGB_1) or (index > Index.RGB_5):
            raise InvalidIndexError()
        return self.set_variables(id, [[Index, color]])

    def get_imu(self, id: int, index: Index):
        """ Get IMU module data (roll, pitch)

        Args:
            id (int): The device ID of the driver.
            index (Index): The index of the IMU module.

        Raises:
            InvalidIndexError: Index is not a IMU module index

        Returns:
            list: Returns roll, pitch angles
        """
        if (index < Index.IMU_1) or (index > Index.IMU_5):
            raise InvalidIndexError()

        ret = self.get_variables(id, [index])
        if ret is None:
            return ret
        return ret[0]
