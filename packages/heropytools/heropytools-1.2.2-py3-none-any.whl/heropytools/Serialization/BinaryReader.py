# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

import struct

import numpy as np
from typing import Dict
from .Header import Header
from .Reader import Reader
from datetime import timedelta
from datetime import datetime
from heropytools.HeroData.Version import Version
from heropytools.HeroData.HeroDataType import HeroDataType
from heropytools.HeroData.Contour import ContourType
from typing import Callable
from .LEB128 import LEB128


class BinaryReader(Reader):
    """
    Implements a Reader that can read binary Hero data.
    """

    def __init__(self, stream):
        """
        Creates a BinaryReader and connects it to a stream
        :param stream: A ReadStream class that implements a read(n) function.
        """
        self.stream = stream
        self._readers = self._setup_readers()

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
        pass

    def read_serializer_header(self):
        object_name = self._read_raw_string()
        version = self._read_raw_string()
        return object_name, version

    def read_header(self, name_to_type_str: Callable[[str], str]) -> Header:
        """
        Read a header
        :param name_to_type_str: Method to convert a name of a type to its actual type name.
        :return: A header.
        """

        name = self._read_raw_string()
        info: int = int.from_bytes(self.stream.read(2), 'little')
        sf = info >> 8
        is_null: bool = info & 0x04 != 0

        if is_null:
            return Header(sf, name=name, is_null=True, content_size=0)

        has_type_name = (info & 0x01) != 0
        has_name_space = (info & 0x02) != 0
        has_default_size = (info & 0x08) != 0
        has_non_default_version = (info & 0x10) != 0

        type_name = None
        name_space = None
        content_size = 1
        version = 0
        
        if has_type_name:
            type_name = name_to_type_str(self._read_raw_string())
        if has_name_space:
            name_space = self._read_raw_string()
        if not has_default_size:
            content_size = int.from_bytes(self.stream.read(4), 'little')
        if has_non_default_version:
            version = int.from_bytes(self.stream.read(2), 'little')

        return Header(sf, type_name, name, version, name_space, content_size, False)

    def read_footer(self):
        """
        Binary format footer reads nothing.
        """
        pass

    def read(self, type_str: str, n: int = 1):
        """
        Read data of a specific type
        :param type_str: The type of data
        :param n: The number of elements. Differ from 1 for arrays.
        :return: The data read.
        """
        return self._readers[type_str](n)

    def can_read(self, type_str: str):
        """
        Tell if a specific type can be read
        :param type_str: Name of the type.
        :return: True if it can be read.
        """
        return type_str in self._readers

    # -------------------------------------------------- #
    #           Private helper methods below.
    # -------------------------------------------------- #

    def _setup_readers(self) -> Dict:
        """
        Set up readers for all supported atomic types. Both single elements and arrays.
        :return: A dictionary of methods to read each type.
        """
        readers = {
            # Single elements
            "Boolean": lambda n: self._read_bool(),
            "Byte": lambda n: self._read_any_number(np.uint8, 1),
            "SByte": lambda n: self._read_any_number(np.int8, 1),
            "Int16": lambda n: self._read_any_number(np.int16, 2),
            "Int32": lambda n: self._read_any_number(np.int32, 4),
            "Int64": lambda n: self._read_any_number(np.int64, 8),
            "UInt16": lambda n: self._read_any_number(np.uint16, 2),
            "UInt32": lambda n: self._read_any_number(np.uint32, 4),
            "UInt64": lambda n: self._read_any_number(np.uint64, 8),
            "Single": lambda n: self._read_any_number(np.float32, 4),
            "Double": lambda n: self._read_any_number(np.float64, 8),
            "ComplexFloat": lambda n: self._read_any_number(np.complex64, 8),
            "Complex": lambda n: self._read_any_number(np.complex128, 16),
            "TimeSpan": lambda n: self._read_time_span(),
            "DateTime": lambda n: self._read_date_time(),
            "Version": lambda n: self._read_version(),
            "String": lambda n: self._read_string(),
            "HeroDataType": lambda n: self._read_enum(HeroDataType),
            "ContourType": lambda n: self._read_enum(ContourType),

            # Arrays
            "Boolean[]": lambda n: self._read_np_array(n, bool, 1),
            "Int64[]": lambda n: self._read_np_array(n, np.int64, 8),
            "Int32[]": lambda n: self._read_np_array(n, np.int32, 4),
            "Int16[]": lambda n: self._read_np_array(n, np.int16, 2),
            "SByte[]": lambda n: self._read_np_array(n, np.int8, 1),
            "UInt64[]": lambda n: self._read_np_array(n, np.uint64, 8),
            "UInt32[]": lambda n: self._read_np_array(n, np.uint32, 4),
            "UInt16[]": lambda n: self._read_np_array(n, np.uint16, 2),
            "Byte[]": lambda n: self._read_np_array(n, np.uint8, 1),
            "Single[]": lambda n: self._read_np_array(n, np.float32, 4),
            "Double[]": lambda n: self._read_np_array(n, np.float64, 8),
            "Complex[]": lambda n: self._read_np_array(n, np.complex128, 16),
            "ComplexFloat[]": lambda n: self._read_np_array(n, np.complex64, 8),
            "TimeSpan[]": lambda n: self._read_simple_array(n, self._read_time_span),
            "DateTime[]": lambda n: self._read_simple_array(n, self._read_date_time),
            "Version[]": lambda n: self._read_simple_array(n, self._read_version),
            "String[]": lambda n: self._read_simple_array(n, self._read_string),
            "HeroDataType[]": lambda n: self._read_simple_array(n, lambda: self._read_enum(HeroDataType)),
            "ContourType[]": lambda n: self._read_simple_array(n, lambda: self._read_enum(ContourType)),
        }
        return readers

    def _read_bool(self) -> bool:
        """
        Read a bool.
        :return: The bool read as a numpy array.
        """
        byte_array = self.stream.read(1)
        return bool.from_bytes(byte_array, 'little')

    def _read_any_number(self, d_type, number_size: int) -> np.array:
        """
        Read a number
        :param d_type: The data type for the number. Specified with numpy data type format
        :param number_size: The size of the number in bytes
        :return: The read number as a numpy array.
        """
        byte_array = self.stream.read(number_size)
        return np.frombuffer(byte_array, dtype=d_type, count=1).reshape([])

    def _read_time_span(self) -> timedelta:
        """
        Read a timespan defined as a double in seconds.
        :return: A timedelta object.
        """
        byte_array = self.stream.read(8)
        f = struct.unpack('<f', byte_array)
        return timedelta(seconds=f[0])

    def _read_date_time(self):
        """
        Read a datetime object.
        :return: The read datetime object
        """
        byte_array = self.stream.read(8)
        n_tot = int.from_bytes(byte_array, 'little')
        n_s = n_tot // 10_000_000
        n_us = (n_tot - n_s * 10_000_000) / 10
        return datetime(1, 1, 1) + timedelta(seconds=n_s, microseconds=n_us)

    def _read_string(self):
        """
        Read a nullable string.
        :return: The string or None if null.
        """
        is_null_array = self.stream.read(1)
        is_null = bool.from_bytes(is_null_array, 'little')
        string = self._read_raw_string()
        if is_null:
            return None
        else:
            return string

    def _read_raw_string(self):
        """
        Read a string that is not null.
        :return: The string.
        """
        length = LEB128.decode_steam(self.stream, max_len=8)
        byte_array = self.stream.read(length)
        return byte_array.decode('utf8', 'strict')

    def _read_version(self):
        """
        Read a version object.
        :return: The read version object.
        """
        string = self._read_string()
        if string is None:
            return None
        else:
            return Version.from_string(string)

    def _read_enum(self, enum_type):
        """
        Read any enum type
        :param enum_type: The enum type class.
        :return: The read enum object.
        """
        value = self._read_any_number(np.int16, 2)
        return enum_type(value)

    def _read_np_array(self, n, d_type, dsize):
        """
        Read a numpy array from the stream
        :param n: The number of elements in the array
        :param d_type: The data type specified as numpy type
        :param dsize: The size of the object. I.e. the number of elements.
        :return: The read numpy array.
        """
        byte_array = self.stream.read(n * dsize)
        return np.frombuffer(byte_array, d_type)

    @staticmethod
    def _read_simple_array(n, single_reader):
        """
        Read an array by reading one by one element using the single_reader
        :param n: The number of elements to read
        :param single_reader: The reader for a single element.
        :return: The read array.
        """
        arr = list()
        for _ in range(n):
            value = single_reader()
            arr.append(value)
        return arr
