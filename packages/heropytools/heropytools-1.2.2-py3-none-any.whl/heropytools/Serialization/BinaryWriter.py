# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

import struct
from typing import Union
import numpy as np
from datetime import timedelta
from datetime import datetime
from .Header import Header
from heropytools.HeroData.HeroDataType import HeroDataType
from heropytools.HeroData.Contour import ContourType
from .LEB128 import LEB128
from .Writer import Writer


class BinaryWriter(Writer):
    """
    Implements a Writer for binary data for Hero.
    """

    def __init__(self, stream):
        """
        Initializes a writer and connects it to a stream
        :param stream:
        """
        self.stream = stream
        self._setup_writers()

    def __enter__(self):
        """
        Called when entering a with statement.
        :return: self
        """
        return self

    def __exit__(self, t, v, t2):
        """
        Called when exiting a with statement.
        :param t:
        :param v:
        :param t2:
        :return:
        """
        self.stream = None

    def write_serializer_header(self, object_name: str, version: str):
        bytes_to_write = bytearray()
        bytes_to_write += self._write_raw_string(object_name)
        bytes_to_write += self._write_raw_string(version)
        self.stream.write(bytes_to_write)

    def write_header(self, h: Header):
        """
        Write the header to the stream
        :param h: The header
        :return: nothing
        """

        # Writes the name of the object.
        bytes_to_write = bytearray()
        bytes_to_write += self._write_raw_string(h.name)

        # Write a short code describing basic info about the object and what additional information that is stored.
        info: int = h.storage_format << 8
        has_type_name = 0x0 if h.type_name is None else 0x1 
        has_name_space = 0x0 if h.name_space is None else 0x2 
        is_null = 0x4 if h.is_null is None else 0x0 
        has_default_size = 0x8 if h.content_size == 1 else 0x0 
        has_non_default_version = 0x0 if h.version is None else 0x10
        info |= has_name_space | has_type_name | is_null | has_default_size | has_non_default_version
        info_bytes = info.to_bytes(2, 'little')
        bytes_to_write += info_bytes

        # Writes possible additional information.
        if not h.is_null:
            if has_type_name != 0:
                bytes_to_write += self._write_raw_string(h.type_name) # noqa
            if has_name_space != 0:
                bytes_to_write += self._write_raw_string(h.name_space) # noqa
            if has_default_size == 0:
                content_size_bytes = h.content_size.to_bytes(4, 'little')
                bytes_to_write += content_size_bytes
            if has_non_default_version != 0:
                version_bytes = h.version.to_bytes(2, 'little') # noqa
                bytes_to_write += version_bytes

        # Write the data to the stream. Store it in a byte_array for more efficiency.
        self.stream.write(bytes_to_write)

    def write_footer(self):
        """
        Binary format footer writes nothing.
        """
        pass

    def write(self, obj, type_str: str):
        """
        Write data of a specific type
        :param obj: The object to be written
        :param type_str: The type of data.
        :return: nothing
        """
        bytes_arr = self._writers[type_str](obj)
        self.stream.write(bytes_arr)

    def can_write(self, type_str: str) -> bool:
        """
        Tell if a specific type can be written
        :param type_str: Name of the type.
        :return: True if it can be written.
        """
        return type_str in self._writers

    def get_size(self, obj, type_str: str) -> int:
        """
        Get size of an object
        :param obj: The object for which to get the size. Will differ from 1 only for arrays
        :param type_str: The type of data as a string.
        :return: The size.
        """
        if '[]' in type_str:
            if isinstance(obj, list):
                return len(obj)
            if isinstance(obj, tuple):
                return len(obj)
            elif isinstance(obj, np.ndarray):
                return obj.size
            else:
                raise Exception("Serialization failed.")
        else:
            return 1

    # -------------------------------------------------- #
    #           Private helper methods below.
    # -------------------------------------------------- #

    def _setup_writers(self):
        """
        Set up writers for all supported atomic types. Both single elements and arrays.
        :return: A dictionary of methods to write each type.
        """
        self._writers = {
            # Single elements
            "Boolean": lambda v: BinaryWriter._write_bool(v),
            "Byte": lambda v: BinaryWriter._write_int(v, np.uint8, 1, "8-bit unsigned integer"),
            "SByte": lambda v: BinaryWriter._write_int(v, np.int8, 1, "8-bit integer"),
            "Int16": lambda v: BinaryWriter._write_int(v, np.int16, 2, "16-bit integer"),
            "Int32": lambda v: BinaryWriter._write_int(v, np.int32, 4, "32-bit integer"),
            "Int64": lambda v: BinaryWriter._write_int(v, np.int64, 8, "64-bit integer"),
            "UInt16": lambda v: BinaryWriter._write_int(v, np.uint16, 2, "16-bit unsigned integer"),
            "UInt32": lambda v: BinaryWriter._write_int(v, np.uint32, 4, "32-bit unsigned integer"),
            "UInt64": lambda v: BinaryWriter._write_int(v, np.uint64, 8, "64-bit unsigned integer"),
            "Single": lambda v: BinaryWriter._write_float(v, np.float32, "32-bit float"),
            "Double": lambda v: BinaryWriter._write_float(v, np.float64, "64-bit float"),
            "ComplexFloat": lambda v: BinaryWriter._write_complex(v, np.float32, "64-bit complex"),
            "Complex": lambda v: BinaryWriter._write_complex(v, np.float64, "128-bit complex"),
            "TimeSpan": lambda v: BinaryWriter._write_time_span(v),
            "DateTime": lambda v: BinaryWriter._write_date_time(v),
            "Version": lambda v: BinaryWriter._write_version(v),
            "String": lambda v: BinaryWriter._write_string(v),
            "HeroDataType": lambda v: BinaryWriter._write_enum(v, HeroDataType),
            "ContourType": lambda v: BinaryWriter._write_enum(v, ContourType),

            # Arrays
            "Boolean[]": lambda v: BinaryWriter._write_np_like_array(v, bool, BinaryWriter._write_bool,
                                                                     "Expected a bool array, but got: "),
            "Int64[]": lambda v: BinaryWriter._write_np_like_array(v, np.int64, lambda vv: BinaryWriter._write_int(vv, np.int64, 8, "64-bit integer"), # noqa
                                                                   "Expected a signed long array, but got: "),
            "Int32[]": lambda v: BinaryWriter._write_np_like_array(v, np.int32, lambda vv: BinaryWriter._write_int(vv, np.int32, 4, "32-bit integer"), # noqa
                                                                   "Expected a signed int array, but got: "),
            "Int16[]": lambda v: BinaryWriter._write_np_like_array(v, np.int16, lambda vv: BinaryWriter._write_int(vv, np.int16, 2, "16-bit integer"), # noqa
                                                                   "Expected a signed short array, but got: "),
            "SByte[]": lambda v: BinaryWriter._write_np_like_array(v, np.int8, lambda vv: BinaryWriter._write_int(vv, np.int8, 1, "8-bit integer"), # noqa
                                                                   "Expected a signed byte array, but got: "),
            "UInt64[]": lambda v: BinaryWriter._write_np_like_array(v, np.uint64, lambda vv: BinaryWriter._write_int(vv, np.uint64, 8, "64-bit integer"), # noqa
                                                                    "Expected a unsigned long array, but got: "),
            "UInt32[]": lambda v: BinaryWriter._write_np_like_array(v, np.uint32, lambda vv: BinaryWriter._write_int(vv, np.uint32, 4, "32-bit integer"), # noqa
                                                                    "Expected a unsigned int array, but got: "),
            "UInt16[]": lambda v: BinaryWriter._write_np_like_array(v, np.uint16, lambda vv: BinaryWriter._write_int(vv, np.uint16, 2, "16-bit integer"), # noqa
                                                                    "Expected a unsigned short array, but got: "),
            "Byte[]": lambda v: BinaryWriter._write_np_like_array(v, np.uint8, lambda vv: BinaryWriter._write_int(vv, np.uint8, 1, "8-bit integer"), # noqa
                                                                  "Expected a unsigned byte array, but got: "),
            "Single[]": lambda v: BinaryWriter._write_np_like_array(v, np.float32, lambda vv: BinaryWriter._write_float(vv, np.float32, "32-bit float"),  # noqa
                                                                    "Expected a float array, but got: "),
            "Double[]": lambda v: BinaryWriter._write_np_like_array(v, np.float64, lambda vv: BinaryWriter._write_float(vv, np.float64, "64-bit float"),  # noqa
                                                                    "Expected a double array, but got: "),
            "Complex[]": lambda v: BinaryWriter._write_np_like_array(v, np.complex128, lambda vv:  BinaryWriter._write_complex(vv, np.float64, "128-bit complex"),  # noqa
                                                                    "Expected a complex double array, but got: "),
            "ComplexFloat[]": lambda v: BinaryWriter._write_np_like_array(v, np.complex64, lambda vv:  BinaryWriter._write_complex(vv, np.float32, "64-bit complex"),  # noqa
                                                                    "Expected a complex float array, but got: "),
            "TimeSpan[]": lambda v: BinaryWriter._write_simple_array(v, BinaryWriter._write_time_span),
            "DateTime[]": lambda v: BinaryWriter._write_simple_array(v, BinaryWriter._write_date_time),
            "Version[]": lambda v: BinaryWriter._write_simple_array(v, BinaryWriter._write_version),
            "String[]": lambda v: BinaryWriter._write_simple_array(v, BinaryWriter._write_string),
            "HeroDataType[]": lambda v: BinaryWriter._write_simple_array(v, lambda w: BinaryWriter._write_enum(w, HeroDataType)), # noqa
            "ContourType[]": lambda v: BinaryWriter._write_simple_array(v, lambda w: BinaryWriter._write_enum(w, ContourType)), # noqa
        }

    # -------------------------------------------------- #
    #          Writer for single elements.
    # -------------------------------------------------- #

    @staticmethod
    def _write_bool(value: [np.array, bool]) -> bytes:
        """
        Write a single bool
        :param value: The bool to write. Can be a python bool or a 0-dim numpy array.
        :return: nothing
        """
        if isinstance(value, bool):
            return value.to_bytes(1, 'little')
        elif isinstance(value, np.ndarray):
            if value.ndim != 0:
                raise Exception(f"A bool cannot be represented by an numpy array with more than 0 "
                                "dimension.")
            if value.dtype != bool:
                raise Exception(f"A single bool cannot be represented by a non bool numpy array.")
            return value.tobytes()
        else:
            raise Exception(f"The type {type(value)} cannot be used to represent a bool.")

    @staticmethod
    def _write_time_span(value: timedelta) -> bytes:
        """
        Write a timespan (timedelta) as a double
        :param value: The value to write.
        :return: The value as a byte array.
        """
        if isinstance(value, timedelta):
            dt = value.total_seconds()
            return struct.pack("<d", dt)
        else:
            raise Exception(f"A TimeSpan must be of type: timedelta")

    @staticmethod
    def _write_date_time(value: datetime) -> bytes:
        """
        Write a datetime element as a long number of ticks
        :param value: A datetime element.
        :return: The value as a byte array.
        """
        if isinstance(value, datetime):
            # Convert it to ticks
            delta = value - datetime(1, 1, 1)
            # Need to do this to avoid round-off
            ticks = int(delta.total_seconds()) * 10_000_000 + delta.microseconds * 10
            return ticks.to_bytes(8, 'little')
        else:
            raise Exception(f"A DateTime must be of type: datetime")

    @staticmethod
    def _write_version(value) -> bytes:
        """
        Write a version object as a string
        :param value: A Version object.
        :return: The value as a byte array.
        """
        if value is None:
            return BinaryWriter._write_string(value)
        else:
            return BinaryWriter._write_string(str(value))

    @staticmethod
    def _write_enum(value, enum_type) -> bytes:
        """
        Write any enum object (with values less than 2^16) using a short int
        :param value: The enum value
        :param enum_type: The enum type.
        :return: The value as a byte array.
        """
        if isinstance(value, enum_type):
            return int(value.value).to_bytes(2, 'little')
        else:
            raise Exception(f"The value was not of type {type(enum_type)}.")

    @staticmethod
    def _write_string(value: str) -> bytes:
        """
        Write a string that can be null to a bytearray. First a byte indicated if it is null is written, then a 7bit
        integer is used to encode the length of the string. Following that the utf-8 encoded byte content of the string
        is written
        :param value: The string to be written.
        :return: The value as a byte array.
        """
        is_null = 1 if value is None else 0
        value = "" if value is None else value
        arr = bytearray(is_null.to_bytes(1, 'little'))

        if isinstance(value, str):
            arr.extend(BinaryWriter._write_raw_string(value))
            return arr
        else:
            raise Exception(f"A string must be of type: str")

    @staticmethod
    def _write_raw_string(value: str) -> bytes:
        """
        Write a string without the null check and assuming that we know it is a string. Will use UTF-8 encoding and
        7-bit integer to encode the length of the string
        :param value: The string
        :return: The value as a byte array.
        """
        value_byte_array = value.encode("UTF-8")
        length = len(value_byte_array)
        if length < 0x80:
            byte_size = bytes([length])
        else:
            byte_size = LEB128.encode(length)
        byte_size += value_byte_array
        return byte_size

    @staticmethod
    def _write_int(value: Union[np.array, int], int_type, int_size: int, type_str: str) -> bytes:
        """
        Write an integer to a bytearray. Can be numpy integers or python builtin type
        :param value: The integer to write
        :param int_type: The type of integer to write. Use numpy types here
        :param int_size: The size of the integer. Used only for the builtin type
        :param type_str: String identifying the integer. Used only for error messages.
        :return: The value as a bytearray
        """
        if isinstance(value, int):
            if not BinaryWriter.validate_integer_range(value, int_type):
                raise Exception(f"{type_str} out of range.")
            return value.to_bytes(int_size, 'little')
        elif isinstance(value, np.ndarray):
            if value.ndim != 0:
                raise Exception(f"A {type_str} cannot be represented by an numpy array with more than 0 "
                                "dimension.")
            return value.tobytes()
        else:
            raise Exception(f"The type {type(value)} cannot be used to represent a {type_str}.")

    @staticmethod
    def _write_float(value: Union[np.array, float], float_type, type_str: str) -> bytes:
        """
        Write floating point numbers to bytes. Can be builtin python float or numpy array
        :param value: The floating point number
        :param float_type: The type expressed as
        :param type_str: Type info for error messages.
        :return: The fp number as an array of bytes.
        """
        if isinstance(value, np.ndarray):
            if value.ndim != 0:
                raise Exception(f"A {type_str} cannot be represented by an numpy array with more than 0 "
                                "dimension.")
            return value.tobytes()
        elif isinstance(value, float):
            if not BinaryWriter.validate_float_range(value, float_type):
                raise Exception(f"{type_str} out of range.")
            if float_type == np.float32:
                return struct.pack("<f", value)
            if float_type == np.float64:
                return struct.pack("<d", value)
            else:
                raise Exception(f"Can only write 32 and 64 bit floating point numbers.")
        else:
            raise Exception(f"The type {type(value)} cannot be used to represent a {type_str}.")

    @staticmethod
    def _write_complex(value: Union[np.array, complex], float_type, type_str: str) -> bytes:
        """
        Write floating point complex numbers to bytes. Can be builtin python complex or numpy array
        :param value: The floating point complex number
        :param float_type: The type of the real and imaginary parts. Can be np.float32 and np.float64
        :param type_str: Type info for error messages.
        :return: The fp number as an array of bytes.
        """
        if isinstance(value, complex):
            if not BinaryWriter.validate_float_range(value.real, float_type):
                raise Exception(f"{type_str} out of range.")
            if not BinaryWriter.validate_float_range(value.imag, float_type):
                raise Exception(f"{type_str} out of range.")
            if float_type == np.float32:
                return b''.join((struct.pack("<f", value.real), struct.pack("<f", value.imag)))
            if float_type == np.float64:
                return b''.join((struct.pack("<d", value.real), struct.pack("<d", value.imag)))
            else:
                raise Exception(f"Can only write 64 and 128 bit complex numbers.")
        elif isinstance(value, np.ndarray):
            if value.ndim != 0:
                raise Exception(f"A {type_str} cannot be represented by an numpy array with more than 0 "
                                "dimension.")
            return value.tobytes()
        else:
            raise Exception(f"The type {type(value)} cannot be used to represent a {type_str}.")

    # -------------------------------------------------- #
    #          Writer for arrays of elements.
    # -------------------------------------------------- #

    @staticmethod
    def _write_np_like_array(value: Union[np.array, tuple, list], d_type, single_writer, msg: str) -> bytes:
        """
        Write an array of values to bytes. Normally this will be given as a numpy array making the operation fast.
        However, list and tuples of builtin python number are allowed too. But will be significantly slower
        :param value: The array to write
        :param d_type: The data type. As numpy data type
        :param single_writer: Writes a single element
        :param msg: Part of error message.
        :return: The data in the array as bytes.
        """
        if isinstance(value, np.ndarray):
            if value.ndim != 1:
                raise Exception("An array must be 1D.")
            if value.dtype != d_type:
                raise Exception(msg + f"{value.dtype}")
            return value.tobytes()

        elif isinstance(value, list) or isinstance(value, tuple):
            byte_array = bytearray()
            for v in value:
                byte_array.extend(single_writer(v))
            return byte_array
        else:
            raise Exception("Writing failed.")

    @staticmethod         
    def _write_simple_array(value: Union[list, tuple], single_writer) -> bytes:
        """
        When no specific writer exists for an array. This code is used. It will be a bit slow but for the
        types that are likely to have big arrays there are fast alternatives
        :param value: The array (list or tuple) of data
        :param single_writer: Function to write a single element.
        :return: Bytes for all elements.
        """
        if isinstance(value, list) or isinstance(value, tuple):
            byte_array = bytearray()
            for v in value:
                byte_array.extend(single_writer(v))

            return byte_array
        else:
            raise Exception("Writing failed.")

    @staticmethod
    def validate_integer_range(value: int, int_info) -> bool:
        """
        Check that the integer is withing the range of fixed size integer
        :param value: The integer to validate
        :param int_info: The integer type. In numpy format.
        :return: True if valid integer of given type.
        """
        return np.iinfo(int_info).min <= value <= np.iinfo(int_info).max

    @staticmethod
    def validate_float_range(value: float, float_info) -> bool:
        """
        Check that a number is withing the range of floating allowed point values
        :param value: The integer to validate
        :param float_info: The data type. In numpy format.
        :return: True if within valid range of given type.
        """
        if not np.isfinite(value):
            return True
        return np.finfo(float_info).min <= value <= np.finfo(float_info).max
