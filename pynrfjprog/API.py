"""
This module serves as a Python wrapper around the nrfjprog DLL.

Note: Please look at the nrfjprogdll.h file provided with the tools for a more elaborate description of the API functions and their side effects.
"""

from __future__ import print_function

from builtins import int

import codecs
import ctypes
import enum
import os
import sys

try:
    from . import JLink
except Exception:
    import JLink

"""
Deprecated: Do not use, use log parameter in API constructor instead.
"""
DEBUG_OUTPUT = False


@enum.unique
class DeviceFamily(enum.IntEnum):
    """
    Wraps device_family_t values from DllCommonDefinitions.h

    """
    NRF51              = 0
    NRF52              = 1
    UNKNOWN            = 99

class DeviceVersion(enum.IntEnum):
    """
    Wraps device_version_t values from DllCommonDefinitions.h

    """
    # Desired order for enumerators. Only useful to indicate the enumerators that have preference if the number is the same. Only necessary in py2.7, harmless in 3.x
    __order__ = 'NRF51xxx_xxAA_REV1' + ' ' + \
                'NRF51xxx_xxAA_REV2' + ' ' + \
                'NRF51xxx_xxAA_REV3' + ' ' + \
                'NRF51xxx_xxAB_REV3' + ' ' + \
                'NRF51xxx_xxAC_REV3' + ' ' + \
                'NRF51802_xxAA_REV3' + ' ' + \
                'NRF51801_xxAB_REV3' + ' ' + \
                'NRF52832_xxAA_ENGA' + ' ' + \
                'NRF52832_xxAA_ENGB' + ' ' + \
                'NRF52832_xxAA_REV1' + ' ' + \
                'NRF52832_xxAA_FUTURE' + ' ' \
                'NRF52840_xxAA_ENGA' + ' ' + \
                'NRF52840_xxAA_FUTURE' + ' '

    UNKNOWN                 = 0
    
    NRF51xxx_xxAA_REV1      = 1
    NRF51xxx_xxAA_REV2      = 2
    NRF51xxx_xxAA_REV3      = 3
    NRF51xxx_xxAB_REV3      = 4
    NRF51xxx_xxAC_REV3      = 5
    NRF51802_xxAA_REV3      = 6
    NRF51801_xxAB_REV3      = 17
    
    NRF52832_xxAA_ENGA      = 7
    NRF52832_xxAA_ENGB      = 8
    NRF52832_xxAA_REV1      = 9
    NRF52832_xxAB_REV1      = 15
    NRF52832_xxAA_FUTURE    = 11
    NRF52832_xxAB_FUTURE    = 16
    
    NRF52840_xxAA_ENGA      = 10
    NRF52840_xxAA_FUTURE    = 12
    
    # Deprecated enumerators. Do not use for new code.
    NRF51_XLR1              = 1  # Deprecated enumerator. Please do not use in new code.
    NRF51_XLR2              = 2  # Deprecated enumerator. Please do not use in new code.
    NRF51_XLR3              = 3  # Deprecated enumerator. Please do not use in new code.
    NRF51_L3                = 4  # Deprecated enumerator. Please do not use in new code.
    NRF51_XLR3P             = 5  # Deprecated enumerator. Please do not use in new code.
    NRF51_XLR3LC            = 6  # Deprecated enumerator. Please do not use in new code.

    NRF52_FP1_ENGA          = 7 # Deprecated enumerator. Please do not use in new code.
    NRF52_FP1_ENGB          = 8 # Deprecated enumerator. Please do not use in new code.
    NRF52_FP1               = 9  # Deprecated enumerator. Please do not use in new code.
    NRF52_FP1_FUTURE        = 11 # Deprecated enumerator. Please do not use in new code.
    NRF52_FP2_ENGA          = 10 # Deprecated enumerator. Please do not use in new code.

@enum.unique
class NrfjprogdllErr(enum.IntEnum):
    """
    Wraps nrfjprogdll_err_t values from DllCommonDefinitions.h

    """
    SUCCESS                                     =  0
    OUT_OF_MEMORY                               = -1
    INVALID_OPERATION                           = -2
    INVALID_PARAMETER                           = -3
    INVALID_DEVICE_FOR_OPERATION                = -4
    WRONG_FAMILY_FOR_DEVICE                     = -5
    EMULATOR_NOT_CONNECTED                      = -10
    CANNOT_CONNECT                              = -11
    LOW_VOLTAGE                                 = -12
    NO_EMULATOR_CONNECTED                       = -13
    NVMC_ERROR                                  = -20
    RECOVER_FAILED                              = -21
    NOT_AVAILABLE_BECAUSE_PROTECTION            = -90
    NOT_AVAILABLE_BECAUSE_MPU_CONFIG            = -91
    JLINKARM_DLL_NOT_FOUND                      = -100
    JLINKARM_DLL_COULD_NOT_BE_OPENED            = -101
    JLINKARM_DLL_ERROR                          = -102
    JLINKARM_DLL_TOO_OLD                        = -103
    NRFJPROG_SUB_DLL_NOT_FOUND                  = -150
    NRFJPROG_SUB_DLL_COULD_NOT_BE_OPENED        = -151
    NOT_IMPLEMENTED_ERROR                       = -255

@enum.unique
class ReadbackProtection(enum.IntEnum):
    """
    Wraps readback_protection_status_t values from DllCommonDefinitions.h

    """
    NONE                       = 0
    REGION_0                   = 1
    ALL                        = 2
    BOTH                       = 3

@enum.unique
class Region0Source(enum.IntEnum):
    """
    Wraps region_0_source_t values from DllCommonDefinitions.h

    """
    NO_REGION_0                = 0
    FACTORY                    = 1
    USER                       = 2

@enum.unique
class RamPower(enum.IntEnum):
    """
    Wraps ram_power_status_t values from DllCommonDefinitions.h

    """
    OFF                    = 0
    ON                     = 1

@enum.unique
class RTTChannelDirection(enum.IntEnum):
    """
    Wraps rtt_direction_t values from DllCommonDefinitions.h

    """
    UP_DIRECTION           = 0
    DOWN_DIRECTION         = 1

@enum.unique
class QSPIEraseLen(enum.IntEnum):
    """
    Wraps qspi_erase_len_t values from DllCommonDefinitions.h

    """
    ERASE4KB        = 0
    ERASE32KB       = 3
    ERASE64KB       = 1
    ERASEALL        = 2
    
@enum.unique
class QSPIReadMode(enum.IntEnum):
    """
    Wraps qspi_read_mode_t values from DllCommonDefinitions.h

    """
    FASTREAD = 0
    READ2O   = 1
    READ2IO  = 2
    READ4O   = 3
    READ4IO  = 4
    
@enum.unique
class QSPIWriteMode(enum.IntEnum):
    """
    Wraps qspi_write_mode_t values from DllCommonDefinitions.h

    """
    PP    = 0
    PP2O  = 1
    PP4O  = 2
    PP4IO = 3
    
@enum.unique
class QSPIAddressMode(enum.IntEnum):
    """
    Wraps qspi_address_mode_t values from DllCommonDefinitions.h

    """
    BIT24 = 0
    BIT32 = 1
      
@enum.unique
class QSPIFrequency(enum.IntEnum):
    """
    Wraps qspi_frequency_t values from DllCommonDefinitions.h

    """
    M2  = 15
    M4  = 7
    M8  = 3
    M16 = 1
    M32 = 0
    
@enum.unique
class QSPISpiMode(enum.IntEnum):
    """
    Wraps qspi_spi_mode_t values from DllCommonDefinitions.h
    """
    MODE0 = 0
    MODE3 = 1
    
@enum.unique
class QSPILevelIO(enum.IntEnum):
    """
    Wraps qspi_custom_level_t values from DllCommonDefinitions.h
    """
    LEVEL_HIGH = 1
    LEVEL_LOW = 0
    
class QSPIInitParams(object):
    """
    Configuration class for qspi_init() function.

    """
    def __init__(self, read_mode=QSPIReadMode.READ4IO, write_mode=QSPIWriteMode.PP4IO, address_mode=QSPIAddressMode.BIT24, frequency=QSPIFrequency.M16, spi_mode=QSPISpiMode.MODE0, sck_delay=0x80, custom_instruction_io2_level=QSPILevelIO.LEVEL_LOW, custom_instruction_io3_level=QSPILevelIO.LEVEL_HIGH, CSN_pin=17, CSN_port=0, SCK_pin=19, SCK_port=0, DIO0_pin=20, DIO0_port=0, DIO1_pin=21, DIO1_port=0, DIO2_pin=22, DIO2_port=0, DIO3_pin=23, DIO3_port=0, WIP_index=0):
        self.read_mode = read_mode
        self.write_mode = write_mode
        self.address_mode = address_mode
        self.frequency = frequency
        self.spi_mode = spi_mode
        self.sck_delay = sck_delay
        self.custom_instruction_io2_level = custom_instruction_io2_level
        self.custom_instruction_io3_level = custom_instruction_io3_level
        self.CSN_pin = CSN_pin
        self.CSN_port = CSN_port
        self.SCK_pin = SCK_pin
        self.SCK_port = SCK_port
        self.DIO0_pin = DIO0_pin
        self.DIO0_port = DIO0_port
        self.DIO1_pin = DIO1_pin
        self.DIO1_port = DIO1_port
        self.DIO2_pin = DIO2_pin
        self.DIO2_port = DIO2_port
        self.DIO3_pin = DIO3_pin
        self.DIO3_port = DIO3_port
        self.WIP_index = WIP_index
    
@enum.unique
class CpuRegister(enum.IntEnum):
    """
    Wraps cpu_registers_t values from DllCommonDefinitions.h

    """
    R0                        = 0
    R1                        = 1
    R2                        = 2
    R3                        = 3
    R4                        = 4
    R5                        = 5
    R6                        = 6
    R7                        = 7
    R8                        = 8
    R9                        = 9
    R10                       = 10
    R11                       = 11
    R12                       = 12
    R13                       = 13
    R14                       = 14
    R15                       = 15
    XPSR                      = 16
    MSP                       = 17
    PSP                       = 18


class APIError(Exception):
    """
    nrfjprog DLL exception class, inherits from the built-in Exception class.

    """

    def __init__(self, err_code=None):
        """
        Constructs a new object and sets the err_code.

        @param int err_code: The error code returned by the nrfjprog DLL.
        """
        self.err_code = err_code
        if self.err_code in [member.value for name, member in NrfjprogdllErr.__members__.items()]:
            err_str = 'An error was reported by NRFJPROG DLL: {} {}.'.format(self.err_code, NrfjprogdllErr(self.err_code).name)
        else:
            err_str = 'An error was reported by NRFJPROG DLL: {}.'.format(self.err_code)

        Exception.__init__(self, err_str)


class API(object):
    """
    Main class of the module. Instance the class to get access to nrfjprog.dll functions in Python.

    Note: A copy of nrfjprog.dll must be found in the working directory.
    """

    _DEFAULT_JLINK_SPEED_KHZ = 2000

    def __init__(self, device_family, jlink_arm_dll_path=None, log_str_cb=None, log=False, log_str=None, log_file_path=None):
        """
        Constructor.

        @param enum, str or int device_family: The series of device pynrfjprog will interact with.
        @param (optional) str jlink_arm_dll_path: Absolute path to the JLinkARM DLL that you want nrfjprog to use.
        @param (optional) callable object log_str_cb: If present, the log_str_cb will be called to receive log and error information. The log_str_cb object should be callable, expect to receive a string as the only parameter and do not need to return anything.
        @param (optional) bool log: If present and true, will enable logging to sys.stderr with the default log string appended to the beginning of each debug output line.
        @param (optional) str log_str: If present, will enable logging to sys.stderr with overwriten default log string appended to the beginning of each debug output line.
        @param (optional) str log_file_path: If present, will enable logging to log_file specified. This file will be opened in write mode in API.__init__() and closed when api.close() is called.
        """
        self._device_family = None
        self._jlink_arm_dll_path = None
        self._lib = None
        self._log_str_cb = None
        self._log_file = None

        self._device_family = self._decode_enum(device_family, DeviceFamily)
        if self._device_family is None:
            raise ValueError('Parameter device_family must be of type int, str or DeviceFamily enumeration.')

        if jlink_arm_dll_path is None:
            jlink_arm_dll_path = JLink.find_latest_dll()
            if jlink_arm_dll_path is None:
                raise RuntimeError('Could not locate a JLinkARM.dll in the default SEGGER installation path.')
        else:
            if not isinstance(jlink_arm_dll_path, str):
                raise ValueError('Parameter jlink_arm_dll_path must be a string.')

        self._jlink_arm_dll_path = os.path.abspath(jlink_arm_dll_path).encode('ascii')

        if DEBUG_OUTPUT:
            log = True
        self._log_str_cb = self._generate_log_str_cb(log_str_cb, log, log_str, log_file_path)

        this_dir = os.path.dirname(__file__)

        if sys.platform.lower().startswith('win'):
            if sys.maxsize > 2**32:
                nrfjprog_dll_folder = 'win_64bit_dll'
            else:
                nrfjprog_dll_folder = 'win_32bit_dll'
            nrfjprog_dll_name = 'nrfjprog.dll'
        elif sys.platform.lower().startswith('linux'):
            if sys.maxsize > 2**32:
                nrfjprog_dll_folder = 'linux_64bit_so'
            else:
                nrfjprog_dll_folder = 'linux_32bit_so'
            nrfjprog_dll_name = 'libnrfjprogdll.so'
        elif sys.platform.startswith('dar'):
            nrfjprog_dll_folder = 'osx_dylib'
            nrfjprog_dll_name = 'libnrfjprogdll.dylib'

        nrfjprog_dll_path = os.path.join(os.path.abspath(this_dir), nrfjprog_dll_folder, nrfjprog_dll_name)

        if os.path.exists(nrfjprog_dll_path):
            try:
                self._lib = ctypes.cdll.LoadLibrary(nrfjprog_dll_path)
            except Exception as error:
                raise RuntimeError("Could not load the NRFJPROG DLL: '{}'.".format(error))
        else:
            try:
                self._lib = ctypes.cdll.LoadLibrary(nrfjprog_dll_name)
            except Exception as error:
                raise RuntimeError("Failed to load the NRFJPROG DLL by name: '{}.'".format(error))

    """
    nrfjprog.DLL functions.

    """
    def dll_version(self):
        """
        Returns the JLinkARM.dll version.

        @return (int, int, str): Tuple containing the major, minor and revision of the dll.
        """
        major = ctypes.c_uint32()
        minor = ctypes.c_uint32()
        revision = ctypes.c_uint8()

        result = self._lib.NRFJPROG_dll_version(ctypes.byref(major), ctypes.byref(minor), ctypes.byref(revision))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return major.value, minor.value, chr(revision.value)
        
    def is_open(self):
        """
        Checks if the JLinkARM.dll is open.

        @return bool: True if open.
        """
        opened = ctypes.c_bool()

        result = self._lib.NRFJPROG_is_dll_open(ctypes.byref(opened))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)
        
        return opened.value

    def open(self):
        """
        Opens the JLinkARM.dll and sets the log callback. Prepares the dll for work with an nRF5x device.

        """
        # No need to encode self._jlink_arm_dll_path since it is an ASCII string and that is what is expected by ctypes.
        # Function self._log_str_cb has already been encoded in __init__() function.
        device_family = ctypes.c_int(self._device_family.value)

        result = self._lib.NRFJPROG_open_dll(self._jlink_arm_dll_path, self._log_str_cb, device_family)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def close(self):
        """
        Closes and frees the JLinkARM DLL.

        """
        self._lib.NRFJPROG_close_dll()
        if self._log_file is not None and self._log_file is not sys.stderr and self._log_file is not sys.stdout:
            self._log_file.close()

    def enum_emu_snr(self):
        """
        Enumerates the serial numbers of connected USB J-Link emulators.

        @return [int]: A list with the serial numbers.
        """
        serial_numbers_len = ctypes.c_uint32(127)
        serial_numbers = (ctypes.c_uint32 * serial_numbers_len.value)()
        num_available = ctypes.c_uint32()

        result = self._lib.NRFJPROG_enum_emu_snr(ctypes.byref(serial_numbers), serial_numbers_len, ctypes.byref(num_available))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        snr = [int(serial_numbers[i]) for i in range(0, min(num_available.value, serial_numbers_len.value))]

        if len(snr) == 0:
            return None
        else:
            return snr

    def is_connected_to_emu(self):
        """
        Checks if the emulator has an established connection with Segger emulator/debugger.

        @return boolean: True if connected.
        """
        is_connected_to_emu = ctypes.c_bool()

        result = self._lib.NRFJPROG_is_connected_to_emu(ctypes.byref(is_connected_to_emu))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return is_connected_to_emu.value

    def connect_to_emu_with_snr(self, serial_number, jlink_speed_khz=_DEFAULT_JLINK_SPEED_KHZ):
        """
        Connects to a given emulator/debugger.

        @param int serial_number: Serial number of the emulator to connect to.
        @param int jlink_speed_khz: SWDCLK speed [kHz].
        """
        if not self._is_u32(serial_number):
            raise ValueError('The serial_number parameter must be an unsigned 32-bit value.')

        if not self._is_u32(jlink_speed_khz):
            raise ValueError('The jlink_speed_khz parameter must be an unsigned 32-bit value.')

        serial_number = ctypes.c_uint32(serial_number)
        jlink_speed_khz = ctypes.c_uint32(jlink_speed_khz)

        result = self._lib.NRFJPROG_connect_to_emu_with_snr(serial_number, jlink_speed_khz)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def connect_to_emu_without_snr(self, jlink_speed_khz=_DEFAULT_JLINK_SPEED_KHZ):
        """
        Connects to an emulator/debugger.

        @param int jlink_speed_khz: SWDCLK speed [kHz].
        """
        if not self._is_u32(jlink_speed_khz):
            raise ValueError('The jlink_speed_khz parameter must be an unsigned 32-bit value.')

        jlink_speed_khz = ctypes.c_uint32(jlink_speed_khz)

        result = self._lib.NRFJPROG_connect_to_emu_without_snr(jlink_speed_khz)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def read_connected_emu_snr(self):
        """
        Reads the serial number of the emu connected to.

        @return int: emu serial number.
        """
        snr = ctypes.c_uint32()

        result = self._lib.NRFJPROG_read_connected_emu_snr(ctypes.byref(snr))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return snr.value

    def read_connected_emu_fwstr(self):
        """
        Reads the firmware identification string of the connected emulator.
        
        @return str: firmware identification string. 
        """
        buffer_size = ctypes.c_uint32(255)
        fwstr = ctypes.create_string_buffer(buffer_size.value)
        
        result = self._lib.NRFJPROG_read_connected_emu_fwstr(fwstr, buffer_size)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)
        
        return fwstr.value if sys.version_info[0] == 2 else fwstr.value.decode('utf-8')
            
    def disconnect_from_emu(self):
        """
        Disconnects from an emulator.

        """
        result = self._lib.NRFJPROG_disconnect_from_emu()
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def recover(self):
        """
        Recovers the device.

        """
        result = self._lib.NRFJPROG_recover()
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def is_connected_to_device(self):
        """
        Checks if the connected emulator has an established connection with an nRF device.

        @return boolean: True if connected.
        """
        is_connected_to_device = ctypes.c_bool()

        result = self._lib.NRFJPROG_is_connected_to_device(ctypes.byref(is_connected_to_device))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return is_connected_to_device.value

    def connect_to_device(self):
        """
        Connects to the nRF device.

        """
        result = self._lib.NRFJPROG_connect_to_device()
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def disconnect_from_device(self):
        """
        Disconnects from the device.
        
        """
        result = self._lib.NRFJPROG_disconnect_from_device()
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)
            
    def readback_protect(self, desired_protection_level):
        """
        Protects the device against read or debug.

        @param int, str, or ReadbackProtection(IntEnum) desired_protection_level: Readback protection level for the target.
        """
        if not self._is_enum(desired_protection_level, ReadbackProtection):
            raise ValueError('Parameter desired_protection_level must be of type int, str or ReadbackProtection enumeration.')

        desired_protection_level = self._decode_enum(desired_protection_level, ReadbackProtection)
        if desired_protection_level is None:
            raise ValueError('Parameter desired_protection_level must be of type int, str or ReadbackProtection enumeration.')

        desired_protection_level = ctypes.c_int(desired_protection_level.value)

        result = self._lib.NRFJPROG_readback_protect(desired_protection_level)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def readback_status(self):
        """
        Returns the status of the readback protection.

        @return str: Readback protection level of the target.
        """
        status = ctypes.c_int()

        result = self._lib.NRFJPROG_readback_status(ctypes.byref(status))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return ReadbackProtection(status.value).name

    def read_region_0_size_and_source(self):
        """
        Returns the region 0 size and source of protection if any for nRF51 devices.

        @return (int, str): Region size and configuration source of protection (either UICR of FICR).
        """
        size = ctypes.c_uint32()
        source = ctypes.c_int()

        result = self._lib.NRFJPROG_read_region_0_size_and_source(ctypes.byref(size), ctypes.byref(source))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return size.value, Region0Source(source.value).name

    def debug_reset(self):
        """
        Executes a soft reset using the CTRL-AP for nRF52 and onward devices.

        """
        result = self._lib.NRFJPROG_debug_reset()
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def sys_reset(self):
        """
        Executes a system reset request.

        """
        result = self._lib.NRFJPROG_sys_reset()
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def pin_reset(self):
        """
        Executes a pin reset.

        """
        result = self._lib.NRFJPROG_pin_reset()
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def disable_bprot(self):
        """
        Disables BPROT, ACL or NVM protection blocks where appropriate depending on device.

        """
        result = self._lib.NRFJPROG_disable_bprot()
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def erase_all(self):
        """
        Erases all code and UICR flash.

        """
        result = self._lib.NRFJPROG_erase_all()
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def erase_page(self, addr):
        """
        Erases a page of code flash.

        @param int addr: Start address of the page in code flash to erase.
        """
        if not self._is_u32(addr):
            raise ValueError('The addr parameter must be an unsigned 32-bit value.')

        addr = ctypes.c_uint32(addr)

        result = self._lib.NRFJPROG_erase_page(addr)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def erase_uicr(self):
        """
        Erases UICR info page.

        """
        result = self._lib.NRFJPROG_erase_uicr()
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def write_u32(self, addr, data, control):
        """
        Writes one uint32_t data into the given address.

        @param int addr: Address to write.
        @param int data: Value to write.
        @param boolean control: True for automatic control of NVMC by the function.
        """
        if not self._is_u32(addr):
            raise ValueError('The addr parameter must be an unsigned 32-bit value.')

        if not self._is_u32(data):
            raise ValueError('The data parameter must be an unsigned 32-bit value.')

        if not self._is_bool(control):
            raise ValueError('The control parameter must be a boolean value.')

        addr = ctypes.c_uint32(addr)
        data = ctypes.c_uint32(data)
        control = ctypes.c_bool(control)

        result = self._lib.NRFJPROG_write_u32(addr, data, control)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def read_u32(self, addr):
        """
        Reads one uint32_t from the given address.

        @param  int addr: Address to read.
        @return int: Value read.
        """
        if not self._is_u32(addr):
            raise ValueError('The addr parameter must be an unsigned 32-bit value.')

        addr = ctypes.c_uint32(addr)
        data = ctypes.c_uint32()

        result = self._lib.NRFJPROG_read_u32(addr, ctypes.byref(data))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return data.value

    def write(self, addr, data, control):
        """
        Writes data from the array into the device starting at the given address.

        @param int addr: Start address of the memory block to write.
        @param sequence data: Data to write. Any type that implements the sequence API (i.e. string, list, bytearray...) is valid as input.
        @param boolean control: True for automatic control of NVMC by the function.
        """
        if not self._is_u32(addr):
            raise ValueError('The addr parameter must be an unsigned 32-bit value.')

        if not self._is_valid_buf(data):
            raise ValueError('The data parameter must be a sequence type with at least one item.')

        if not self._is_bool(control):
            raise ValueError('The control parameter must be a boolean value.')

        addr = ctypes.c_uint32(addr)
        data_len = ctypes.c_uint32(len(data))
        data = (ctypes.c_uint8 * data_len.value)(*data)
        control = ctypes.c_bool(control)

        result = self._lib.NRFJPROG_write(addr, ctypes.byref(data), data_len, control)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def read(self, addr, data_len):
        """
        Reads data_len bytes from the device starting at the given address.

        @param int addr: Start address of the memory block to read.
        @param int data_len: Number of bytes to read.
        @return [int]: List of values read.
        """
        if not self._is_u32(addr):
            raise ValueError('The addr parameter must be an unsigned 32-bit value.')

        if not self._is_u32(data_len):
            raise ValueError('The data_len parameter must be an unsigned 32-bit value.')

        addr = ctypes.c_uint32(addr)
        data_len = ctypes.c_uint32(data_len)
        data = (ctypes.c_uint8 * data_len.value)()

        result = self._lib.NRFJPROG_read(addr, ctypes.byref(data), data_len)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return list(data)

    def is_halted(self):
        """
        Checks if the device CPU is halted.

        @return boolean: True if halted.
        """
        is_halted = ctypes.c_bool()

        result = self._lib.NRFJPROG_is_halted(ctypes.byref(is_halted))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return is_halted.value

    def halt(self):
        """
        Halts the device CPU.

        """
        result = self._lib.NRFJPROG_halt()
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def run(self, pc, sp):
        """
        Starts the device CPU with the given pc and sp.

        @param int pc: Value for the program counter.
        @param int sp: Value for the stack pointer.
        """
        if not self._is_u32(pc):
            raise ValueError('The pc parameter must be an unsigned 32-bit value.')

        if not self._is_u32(sp):
            raise ValueError('The sp parameter must be an unsigned 32-bit value.')

        pc = ctypes.c_uint32(pc)
        sp = ctypes.c_uint32(sp)

        result = self._lib.NRFJPROG_run(pc, sp)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def go(self):
        """
        Starts the device CPU.

        """
        result = self._lib.NRFJPROG_go()
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def step(self):
        """
        Runs the device CPU for one instruction.

        """
        result = self._lib.NRFJPROG_step()
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def read_ram_sections_count(self):
        """
        Reads the number of RAM sections in the device.

        @return int: number of RAM sections in the device
        """
        count = ctypes.c_uint32()
        
        result = self._lib.NRFJPROG_read_ram_sections_count(ctypes.byref(count))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return count.value

    def read_ram_sections_size(self):
        """
        Reads the size in bytes of the RAM sections in the device.

        @return [int]: List containing the size of each RAM power section. The length of the list is equal to the number of ram sections in the device.
        """
        sections_size_list_size = ctypes.c_uint32(self.read_ram_sections_count())
        sections_size = (ctypes.c_uint32 * sections_size_list_size.value)()
        
        result = self._lib.NRFJPROG_read_ram_sections_size(ctypes.byref(sections_size), sections_size_list_size)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return list(sections_size)
            
    def read_ram_sections_power_status(self):
        """
        Reads the RAM sections power status.

        @return [str]: List containing the power status of each RAM power section. The length of the list is equal to the number of ram sections in the device.
        """
        status_size = ctypes.c_uint32(self.read_ram_sections_count())
        status = (ctypes.c_uint32 * status_size.value)()
        
        result = self._lib.NRFJPROG_read_ram_sections_power_status(ctypes.byref(status), status_size)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return [RamPower(elem).name for elem in list(status)]

    def is_ram_powered(self):
        """
        Reads the RAM power status.

        @return ([str], int, int): Tuple containing three elements, a list of the power status of each RAM block, the number of RAM blocks in the device and the size of the RAM blocks in the device.
        """
        status_size = ctypes.c_uint32(64)
        status = (ctypes.c_uint32 * status_size.value)()
        number = ctypes.c_uint32()
        size = ctypes.c_uint32()

        result = self._lib.NRFJPROG_is_ram_powered(ctypes.byref(status), status_size, ctypes.byref(number), ctypes.byref(size))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return [RamPower(elem).name for elem in list(status)[0:min(number.value, status_size.value)]], number.value, size.value

    def power_ram_all(self):
        """
        Powers up all RAM sections of the device.

        """
        result = self._lib.NRFJPROG_power_ram_all()
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def unpower_ram_section(self, section_index):
        """
        Powers down a RAM section of the device.

        @param int section_index: RAM block index to power off.
        """
        if not self._is_u32(section_index):
            raise ValueError('The section_index parameter must be an unsigned 32-bit value.')

        section_index = ctypes.c_uint32(section_index)

        result = self._lib.NRFJPROG_unpower_ram_section(section_index)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def read_cpu_register(self, register_name):
        """
        Reads a CPU register.

        @param  int, str, or CPURegister(IntEnum) register_name: CPU register to read.
        @return int: Value read.
        """
        if not self._is_enum(register_name, CpuRegister):
            raise ValueError('Parameter register_name must be of type int, str or CpuRegister enumeration.')

        register_name = self._decode_enum(register_name, CpuRegister)
        if register_name is None:
            raise ValueError('Parameter register_name must be of type int, str or CpuRegister enumeration.')

        register_name = ctypes.c_int(register_name.value)
        value = ctypes.c_uint32()

        result = self._lib.NRFJPROG_read_cpu_register(register_name, ctypes.byref(value))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return value.value

    def write_cpu_register(self, register_name, value):
        """
        Writes a CPU register.

        @param int, str, or CPURegister(IntEnum) register_name: CPU register to write.
        @param int value: Value to write.
        """
        if not self._is_u32(value):
            raise ValueError('The value parameter must be an unsigned 32-bit value.')

        if not self._is_enum(register_name, CpuRegister):
            raise ValueError('Parameter register_name must be of type int, str or CpuRegister enumeration.')

        register_name = self._decode_enum(register_name, CpuRegister)
        if register_name is None:
            raise ValueError('Parameter register_name must be of type int, str or CpuRegister enumeration.')

        register_name = ctypes.c_int(register_name.value)
        value = ctypes.c_uint32(value)

        result = self._lib.NRFJPROG_write_cpu_register(register_name, value)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def read_device_version(self):
        """
        Reads the version of the device connected to the emulator.

        @return str: Version of the target device.
        """
        version = ctypes.c_int()

        result = self._lib.NRFJPROG_read_device_version(ctypes.byref(version))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return DeviceVersion(version.value).name
        
    def read_device_family(self):
        """
        Reads the family of the device connected to the emulator. Only if API class has been instantiated with UNKNOWN family.

        @return str: Family of the target device.
        """
        family = ctypes.c_int()

        result = self._lib.NRFJPROG_read_device_family(ctypes.byref(family))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return DeviceFamily(family.value).name

    def read_debug_port_register(self, addr):
        """
        Reads a debug port register.

        @param int addr: Address to read.
        @return int: Value read.
        """
        if not self._is_u8(addr):
            raise ValueError('The addr parameter must be an unsigned 8-bit value.')

        addr = ctypes.c_uint8(addr)
        data = ctypes.c_uint32()

        result = self._lib.NRFJPROG_read_debug_port_register(addr, ctypes.byref(data))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return data.value

    def write_debug_port_register(self, addr, data):
        """
        Writes a debug port register.

        @param int addr: Address to write.
        @param int data: Value to write.
        """
        if not self._is_u8(addr):
            raise ValueError('The addr parameter must be an unsigned 8-bit value.')

        if not self._is_u32(data):
            raise ValueError('The data parameter must be an unsigned 32-bit value.')

        addr = ctypes.c_uint8(addr)
        data = ctypes.c_uint32(data)

        result = self._lib.NRFJPROG_write_debug_port_register(addr, data)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def read_access_port_register(self, ap_index, addr):
        """
        Reads a debugger access port register.

        @param int ap_index: Index of the access port to read.
        @param int addr: Address to read.
        @return int: Value read.
        """
        if not self._is_u8(ap_index):
            raise ValueError('The ap_index parameter must be an unsigned 8-bit value.')

        if not self._is_u8(addr):
            raise ValueError('The addr parameter must be an unsigned 8-bit value.')

        ap_index = ctypes.c_uint8(ap_index)
        addr = ctypes.c_uint8(addr)
        data = ctypes.c_uint32()

        result = self._lib.NRFJPROG_read_access_port_register(ap_index, addr, ctypes.byref(data))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return data.value

    def write_access_port_register(self, ap_index, addr, data):
        """
        Writes a debugger access port register.

        @param int ap_index: Index of the access port to write.
        @param int addr: Address to write.
        @param int data: Value to write.
        """
        if not self._is_u8(ap_index):
            raise ValueError('The ap_index parameter must be an unsigned 8-bit value.')

        if not self._is_u8(addr):
            raise ValueError('The addr parameter must be an unsigned 8-bit value.')

        if not self._is_u32(data):
            raise ValueError('The data parameter must be an unsigned 32-bit value.')

        ap_index = ctypes.c_uint8(ap_index)
        addr = ctypes.c_uint8(addr)
        data = ctypes.c_uint32(data)

        result = self._lib.NRFJPROG_write_access_port_register(ap_index, addr, data)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def is_rtt_started(self):
        """
        Checks if the RTT is started.

        @return bool: True if started.
        """
        started = ctypes.c_bool()
        
        result = self._lib.NRFJPROG_is_rtt_started(ctypes.byref(started))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)
            
        return started.value
    
    def rtt_set_control_block_address(self, addr):
        """
        Indicates to the dll the location of the RTT control block in the device memory.

        @param int addr: Address of the RTT Control Block in memory.
        """
        if not self._is_u32(addr):
            raise ValueError('The address parameter must be an unsigned 32-bit value.')

        addr = ctypes.c_uint32(addr)

        result = self._lib.NRFJPROG_rtt_set_control_block_address(addr)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def rtt_start(self):
        """
        Starts RTT.

        """
        result = self._lib.NRFJPROG_rtt_start()
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def rtt_is_control_block_found(self):
        """
        Checks if RTT control block has been found.

        @return boolean: True if found.
        """
        is_control_block_found = ctypes.c_bool()

        result = self._lib.NRFJPROG_rtt_is_control_block_found(ctypes.byref(is_control_block_found))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return is_control_block_found.value

    def rtt_stop(self):
        """
        Stops RTT.

        """
        result = self._lib.NRFJPROG_rtt_stop()
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

    def rtt_read(self, channel_index, length, encoding='utf-8'):
        """
        Reads from an RTT channel.

        @param int channel_index: RTT channel to read.
        @param int length: Number of bytes to read. Note that depending on the encoding parameter, the number of bytes read and the numbers of characters read might differ.
        @param (optional) str or None encoding: Encoding for the data read in order to build a readable string. Default value 'utf-8'. Note that since Python2 native string is coded in ASCII, only ASCII characters will be properly represented.
        @return str or bytearray: Data read. Return type depends on encoding optional parameter. If an encoding is given, the return type will be Python version's native string type. If None is given, a bytearray will be returned.
        """
        if not self._is_u32(channel_index):
            raise ValueError('The channel_index parameter must be an unsigned 32-bit value.')

        if not self._is_u32(length):
            raise ValueError('The length parameter must be an unsigned 32-bit value.')

        if encoding is not None and not self._is_valid_encoding(encoding):
            raise ValueError('The encoding parameter must be either None or a standard encoding in python.')

        channel_index = ctypes.c_uint32(channel_index)
        length = ctypes.c_uint32(length)
        data = (ctypes.c_uint8 * length.value)()
        data_read = ctypes.c_uint32()

        result = self._lib.NRFJPROG_rtt_read(channel_index, ctypes.byref(data), length, ctypes.byref(data_read))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return bytearray(data[0:data_read.value]) if encoding is None else bytearray(data[0:data_read.value]).decode(encoding).encode('utf-8') if sys.version_info[0] == 2 else bytearray(data[0:data_read.value]).decode(encoding)

    def rtt_write(self, channel_index, msg, encoding='utf-8'):
        """
        Writes to an RTT channel.

        @param int channel_index: RTT channel to write.
        @param sequence msg: Data to write. Any type that implements the sequence API (i.e. string, list, bytearray...) is valid as input.
        @param (optional) str or None encoding: Encoding of the msg to write. Default value 'utf-8'.
        @return int: Number of bytes written.  Note that if non-'latin-1' characters are used, the number of bytes written depends on the encoding parameter given.
        """
        if not self._is_u32(channel_index):
            raise ValueError('The channel_index parameter must be an unsigned 32-bit value.')

        if encoding is not None and not self._is_valid_encoding(encoding):
            raise ValueError('The encoding parameter must be either None or a standard encoding in python.')

        msg = bytearray(msg.encode(encoding)) if encoding else bytearray(msg)
        if not self._is_valid_buf(msg):
            raise ValueError('The msg parameter must be a sequence type with at least one item.')

        channel_index = ctypes.c_uint32(channel_index)
        length = ctypes.c_uint32(len(msg))
        data = (ctypes.c_uint8 * length.value)(*msg)
        data_written = ctypes.c_uint32()

        result = self._lib.NRFJPROG_rtt_write(channel_index, ctypes.byref(data), length, ctypes.byref(data_written))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return data_written.value

    def rtt_read_channel_count(self):
        """
        Gets the number of RTT channels.

        @return (int, int): Tuple containing the number of down RTT channels and the number of up RTT channels.
        """
        down_channel_number = ctypes.c_uint32()
        up_channel_number = ctypes.c_uint32()

        result = self._lib.NRFJPROG_rtt_read_channel_count(ctypes.byref(down_channel_number), ctypes.byref(up_channel_number))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return down_channel_number.value, up_channel_number.value

    def rtt_read_channel_info(self, channel_index, direction):
        """
        Reads the info from one RTT channel.

        @param int channel_index: RTT channel to request info.
        @param int, str, or RTTChannelDirection(IntEnum) direction: Direction of the channel to request info.
        @return (str, int): Tuple containing the channel name and the size of channel buffer.
        """
        if not self._is_u32(channel_index):
            raise ValueError('The channel_index parameter must be an unsigned 32-bit value.')

        if not self._is_enum(direction, RTTChannelDirection):
            raise ValueError('Parameter direction must be of type int, str or RTTChannelDirection enumeration.')

        direction = self._decode_enum(direction, RTTChannelDirection)
        if direction is None:
            raise ValueError('Parameter direction must be of type int, str or RTTChannelDirection enumeration.')

        channel_index = ctypes.c_uint32(channel_index)
        direction = ctypes.c_int(direction.value)
        name_len = ctypes.c_uint32(32)
        name = (ctypes.c_uint8 * 32)()
        size = ctypes.c_uint32()

        result = self._lib.NRFJPROG_rtt_read_channel_info(channel_index, direction, ctypes.byref(name), name_len, ctypes.byref(size))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)

        return ''.join(chr(i) for i in name if i != 0), size.value
        
    def is_qspi_init(self):
        """
        Checks if the QSPI peripheral is initialized.

        @return bool: True if initialized.
        """
        initialized = ctypes.c_bool()
        
        result = self._lib.NRFJPROG_is_qspi_init(ctypes.byref(initialized))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)
            
        return initialized.value
        
    def qspi_init(self, retain_ram=False, init_params=None):
        """
        Initializes the QSPI peripheral.
        
        @param (optional) bool retain_ram: Retain contents of device RAM used in the QSPI operations. RAM contents will be restored in qspi_uninit() operation.
        @param (optional) QSPIInitParams init_params: Configuration for the QSPI operations.
        """
        class _CtypesQSPIInitParams(ctypes.Structure):
            _fields_ = [("read_mode", ctypes.c_int), ("write_mode", ctypes.c_int), ("address_mode", ctypes.c_int), ("frequency", ctypes.c_int), ("spi_mode", ctypes.c_int), ("sck_delay", ctypes.c_uint32), ("custom_instruction_io2_level", ctypes.c_int), ("custom_instruction_io3_level", ctypes.c_int), ("CSN_pin", ctypes.c_uint32), ("CSN_port", ctypes.c_uint32), ("SCK_pin", ctypes.c_uint32), ("SCK_port", ctypes.c_uint32), ("DIO0_pin", ctypes.c_uint32), ("DIO0_port", ctypes.c_uint32), ("DIO1_pin", ctypes.c_uint32), ("DIO1_port", ctypes.c_uint32), ("DIO2_pin", ctypes.c_uint32), ("DIO2_port", ctypes.c_uint32), ("DIO3_pin", ctypes.c_uint32), ("DIO3_port", ctypes.c_uint32), ("WIP_index", ctypes.c_uint32)]
        
        if not self._is_bool(retain_ram):
            raise ValueError('The retain_ram parameter must be a boolean value.')
            
        if not self._is_right_class(init_params, QSPIInitParams) and init_params is not None:
            raise ValueError('The init_params parameter must be an instance of class QSPIInitParams.')
        
        if init_params is None:
            init_params = QSPIInitParams()
        
        retain_ram = ctypes.c_bool(retain_ram)
        qspi_init_params = _CtypesQSPIInitParams(init_params.read_mode, init_params.write_mode, init_params.address_mode, init_params.frequency, init_params.spi_mode, init_params.sck_delay, init_params.custom_instruction_io2_level, init_params.custom_instruction_io3_level, init_params.CSN_pin, init_params.CSN_port, init_params.SCK_pin, init_params.SCK_port, init_params.DIO0_pin, init_params.DIO0_port, init_params.DIO1_pin, init_params.DIO1_port, init_params.DIO2_pin, init_params.DIO2_port, init_params.DIO3_pin, init_params.DIO3_port, init_params.WIP_index)
        
        result = self._lib.NRFJPROG_qspi_init(retain_ram, ctypes.byref(qspi_init_params))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)
            
    def qspi_uninit(self):
        """
        Uninitializes the QSPI peripheral.
        
        """
        result = self._lib.NRFJPROG_qspi_uninit()
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)
            
    def qspi_read(self, addr, length):
        """
        Reads from the external QSPI-connected memory.
        
        @param int addr: Address to read from.
        @param int length: Number of bytes to read.
        @return bytearray: Data read.
        """
        if not self._is_u32(addr):
            raise ValueError('The addr parameter must be an unsigned 32-bit value.')
            
        if not self._is_u32(length):
            raise ValueError('The length parameter must be an unsigned 32-bit value.')
        
        addr = ctypes.c_uint32(addr)
        length = ctypes.c_uint32(length)
        data = (ctypes.c_uint8 * length.value)()
        
        result = self._lib.NRFJPROG_qspi_read(addr, ctypes.byref(data), length)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)
            
        return bytearray(data)
            
    def qspi_write(self, addr, data):
        """
        Writes to the external QSPI-connected memory.
        
        @param int addr: Address to write to.
        @param sequence data: Data to write. Any type that implements the sequence API (i.e. string, list, bytearray...) is valid as input.
        """
        if not self._is_u32(addr):
            raise ValueError('The addr parameter must be an unsigned 32-bit value.')
        
        if not self._is_valid_buf(data):
            raise ValueError('The data parameter must be a sequence type with at least one item.')
        
        addr = ctypes.c_uint32(addr)
        data_len = ctypes.c_uint32(len(data))
        data = (ctypes.c_uint8 * data_len.value)(*data)
        
        result = self._lib.NRFJPROG_qspi_write(addr, ctypes.byref(data), data_len)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)
            
    def qspi_erase(self, addr, length):
        """
        Erases the external QSPI-connected memory.
        
        @param int addr: Address to erase.
        @param int, str, or QSPIEraseLen(IntEnum) length: Erase length.
        """
        if not self._is_u32(addr):
            raise ValueError('The addr parameter must be an unsigned 32-bit value.')
        
        if not self._is_enum(length, QSPIEraseLen):
            raise ValueError('Parameter length must be of type int, str or QSPIEraseLen enumeration.')
        
        length = self._decode_enum(length, QSPIEraseLen)
        if length is None:
            raise ValueError('Parameter length must be of type int, str or QSPIEraseLen enumeration.')
        
        addr = ctypes.c_uint32(addr)
        length = ctypes.c_int(length)
        
        result = self._lib.NRFJPROG_qspi_erase(addr, length)
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)
            
    def qspi_custom(self, code, length, data_in=None, output=False):
        """
        Sends a custom instruction to the external QSPI-connected memory.
        
        @param int code: Code of the custom instruction.
        @param int length: Lenght of the custom instruction.
        @param (optional) sequence data_in: Data to send in the custom instruction. Any type that implements the sequence API (i.e. string, list, bytearray...) is valid as input.
        @param (optional) bool output: Ouput from the custom instruction is desired or not.
        @return None or bytearray: Custom instruction received data. Return type depends on output optional parameter.
        """
        if not self._is_u8(code):
            raise ValueError('The code parameter must be an unsigned 8-bit value.')
            
        if not self._is_u8(length):
            raise ValueError('The length parameter must be an unsigned 8-bit value.')
        
        if not self._is_valid_buf(data_in) and data_in is not None:
            raise ValueError('The data_in parameter must be a sequence type with at least one item.')
            
        if not self._is_bool(output):
            raise ValueError('The output parameter must be a boolean value.')
        
        code = ctypes.c_uint8(code)
        length = ctypes.c_uint8(length)
        data_in = (ctypes.c_uint8 * 8)(*data_in) if data_in is not None else (ctypes.c_uint8 * 8)(*[0 for i in range(8)])
        data_out = (ctypes.c_uint8 * 8)()
        
        result = self._lib.NRFJPROG_qspi_custom(code, length, ctypes.byref(data_in), ctypes.byref(data_out))
        if result != NrfjprogdllErr.SUCCESS:
            raise APIError(result)
            
        if output:
            return bytearray(data_out)

    """
    Internal helper functions.

    """
    def _generate_log_str_cb(self, log_str_cb, log, log_str, log_file):
        """
        Setup API's debug output logging mechanism.

        """
        if log_str_cb is not None:
            return ctypes.CFUNCTYPE(None, ctypes.c_char_p)(log_str_cb)

        if log is True or log_str is not None or log_file is not None:
            if log_str is None:
                log_str = '[NRFJPROG DLL LOG]: '
            if log_file is None:
                log_file = sys.stderr
                
            if log_file is sys.stderr or log_file is sys.stdout:
                self._log_file = log_file
            else:
                self._log_file = open(log_file, 'w')

            return ctypes.CFUNCTYPE(None, ctypes.c_char_p)(lambda x: print(log_str + '{}'.format(x.strip()), file=self._log_file)) if sys.version_info[0] == 2 else ctypes.CFUNCTYPE(None, ctypes.c_char_p)(lambda x: print(log_str + '{}'.format(x.strip().decode('utf-8')), file=self._log_file))

    def _is_u32(self, value):
        return isinstance(value, int) and 0 <= value <= 0xFFFFFFFF

    def _is_u8(self, value):
        return isinstance(value, int) and 0 <= value <= 0xFF

    def _is_bool(self, value):
        return isinstance(value, bool) or 0 <= value <= 1

    def _is_valid_buf(self, buf):
        if buf is None:
            return False
        for value in buf:
            if not self._is_u8(value):
                return False
        return len(buf) > 0

    def _is_valid_encoding(self, encoding):
        try:
            codecs.lookup(encoding)
        except LookupError:
            return False
        else:
            return True

    def _is_right_class(self, instance, class_type):
        if instance is None:
            return False
        return isinstance(instance, class_type)
            
    def _is_enum(self, param, enum_type):
        if isinstance(param, int) and param in [member for name, member in enum_type.__members__.items()]:
            return True
        elif isinstance(param, str) and param in [name for name, member in enum_type.__members__.items()]:
            return True
        return False

    def _decode_enum(self, param, enum_type):
        if not self._is_enum(param, enum_type):
            return None

        if isinstance(param, int):
            return enum_type(param)
        elif isinstance(param, str):
            return enum_type[param]

    def __enter__(self):
        """
        Called automatically when the 'with' construct is used.

        """
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        """
        Called automatically when the 'with' construct is used.

        """
        self.close()
