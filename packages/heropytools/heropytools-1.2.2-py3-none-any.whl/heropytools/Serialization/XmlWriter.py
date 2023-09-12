# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

import numpy as np
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import timedelta
from datetime import datetime
import base64
import numbers

from .Header import Header
from heropytools.HeroData.Version import Version
from heropytools.HeroData.HeroDataType import HeroDataType
from heropytools.HeroData.Contour import ContourType
from .Writer import Writer

from pathlib import Path


class XmlWriter(Writer):

    _storage_format_names = ['', 'COMPOSITE', 'ARRAY', 'ATOMIC' ]

    def __init__(self, file_name):
        self.fileName = file_name
        self.root = None
        self.stack = None
        self.current = None

        self._setup_writers()

    def __enter__(self):
        self.stack = list()
        self.root = None
        return self

    def __exit__(self, t, v, t2):
        xml_str = minidom.parseString(ET.tostring(self.root)).toprettyxml(indent="   ")
        with open(self.fileName, 'wb') as f:
            f.write(xml_str.encode('utf-8'))

    def write_serializer_header(self, object_name: str, version: str):
        attrib = {"Serializer": version}
        if self.root is None:
            self.root = Element(object_name)
            self.current = self.root
            self.stack.append(self.root)
            self.current.attrib = attrib
        else:
            child = SubElement(self.current, object_name)
            self.current = child
            self.stack.append(child)
            self.current.attrib = attrib

    def write_header(self, h: Header):
        attrib = self._get_attribute(h)
        if self.root is None:
            self.root = Element(h.name)
            self.current = self.root
            self.stack.append(self.root)
            self.current.attrib = attrib
        else:
            child = SubElement(self.current, h.name)
            self.current = child
            self.stack.append(child)
            self.current.attrib = attrib

    def write_footer(self):
        self.stack.pop()
        if len(self.stack) > 0:
            self.current = self.stack[-1]
        else:
            self.current = None

    def write(self, obj, type_str):
        self.current.text = self._writers[type_str](obj)

    def can_write(self, type_str):
        return type_str in self._writers

    def get_size(self, obj, type_str: str) -> int:
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

    @staticmethod
    def _get_attribute(h):
        attr = dict()
        if h.type_name is not None:
            attr["T"] = h.type_name
        if h.storage_format != Header.ATOMIC:
            attr["F"] = XmlWriter._storage_format_names[h.storage_format]
        if h.name_space is not None:
            attr["NS"] = h.name_space
        if h.is_null:
            attr["N"] = "1"
        if h.content_size != 1:
            attr["S"] = str(h.content_size)
        if h.version != 0:
            attr["V"] = str(h.version)

        return attr

    @staticmethod
    def _write_bool(value):
        if isinstance(value, bool):
            return str(value)
        elif isinstance(value, np.ndarray):
            if value.ndim != 0:
                raise Exception(f"A bool cannot be represented by an numpy array with more than 0 "
                                "dimension.")
            if value.dtype != bool:
                raise Exception(f"A single bool cannot be represented by a non bool numpy array.")
            return str(value)
        else:
            raise Exception(f"The type {type(value)} cannot be used to represent a bool.")

    @staticmethod
    def _write_sbyte(value):
        return XmlWriter._write_any_int(value, np.int8, "8-bit integer")

    @staticmethod
    def _write_short(value):
        return XmlWriter._write_any_int(value, np.int16, "16-bit integer")

    @staticmethod
    def _write_int(value):
        return XmlWriter._write_any_int(value, np.int32, "32-bit integer")

    @staticmethod
    def _write_long(value):
        return XmlWriter._write_any_int(value, np.int64, "64-bit integer")

    @staticmethod
    def _write_byte(value):
        return XmlWriter._write_any_int(value, np.uint8, "8-bit unsigned integer")

    @staticmethod
    def _write_ushort(value):
        return XmlWriter._write_any_int(value, np.uint16, "16-bit unsigned integer")

    @staticmethod
    def _write_uint(value):
        return XmlWriter._write_any_int(value, np.uint32, "32-bit unsigned integer")

    @staticmethod
    def _write_ulong(value):
        return XmlWriter._write_any_int(value, np.uint64, "64-bit unsigned integer")

    @staticmethod
    def _write_float(value):
        return XmlWriter._write_any_float(value, np.float32, "32-bit float")

    @staticmethod
    def _write_double(value):
        return XmlWriter._write_any_float(value, np.float64, "64-bit float")

    @staticmethod
    def _write_complex_float(value):
        return XmlWriter._write_any_complex(value, np.float32, np.complex64, "64-bit complex")

    @staticmethod
    def _write_complex_double(value):
        return XmlWriter._write_any_complex(value, np.float64, np.complex128, "128-bit complex")

    @staticmethod
    def _write_time_span(value):
        if isinstance(value, timedelta):
            return str(value.total_seconds())
        else:
            raise Exception(f"A TimeSpan must be of type: timedelta")

    @staticmethod
    def _write_date_time(value):
        if isinstance(value, datetime):
            # Convert it to ticks
            delta = value - datetime(1, 1, 1)
            # Need to do this to avoid round-off
            ticks = int(delta.total_seconds()) * 10_000_000 + delta.microseconds * 10
            return str(ticks)
        else:
            raise Exception(f"A DateTime must be of type: datetime")

    @staticmethod
    def _write_version(value):
        if isinstance(value, Version):
            return str(value)
        else:
            raise Exception(f"A Version must be of type: Version")

    @staticmethod
    def _write_string(value):
        if isinstance(value, str):
            return base64.b64encode(bytes(value, 'utf-8')).decode('utf-8')
        else:
            raise Exception(f"A string must be of type: str")

    @staticmethod
    def _write_Hero_data_type(value):
        if isinstance(value, HeroDataType):
            return str(value.value)
        else:
            raise Exception(f"A HeroDataType must be of type: HeroDataType")

    @staticmethod
    def _write_contour_type(value):
        if isinstance(value, ContourType):
            return str(value.value)
        else:
            raise Exception(f"A HeroDataType must be of type: ContourType")

    @staticmethod
    def _write_bool_array(value):
        if isinstance(value, np.ndarray):
            if value.ndim != 1:
                raise Exception("A bool array must be 1D.")
            if value.dtype != bool:
                raise Exception(f"Expected a bool array, but got: {value.dtype}.")
            str_list = list()
            for v in value:
                str_list.append(XmlWriter._bool_str(v))
                str_list.append(";")
            if len(str_list) > 0:
                str_list.pop()
            return ''.join(str_list)

        elif isinstance(value, list):
            str_list = list()
            for v in value:
                if not isinstance(v, bool):
                    raise Exception("A non bool element was encountered in a bool array.")
                str_list.append(XmlWriter._bool_str(v))
                str_list.append(";")
            if len(str_list) > 0:
                str_list.pop()
            return ''.join(str_list)
        else:
            raise Exception("Writing failed.")

    @staticmethod
    def _bool_str(value):
        if value:
            return '1'
        else:
            return '0'

    @staticmethod
    def _write_long_array(value):
        return XmlWriter._write_any_int_array(value, np.int64, "64-bit integer")

    @staticmethod
    def _write_int_array(value):
        return XmlWriter._write_any_int_array(value, np.int32, "32-bit integer")

    @staticmethod
    def _write_short_array(value):
        return XmlWriter._write_any_int_array(value, np.int16, "16-bit integer")

    @staticmethod
    def _write_float_array(value):
        return XmlWriter._write_any_int_array(value, np.float32, "32-bit float")

    @staticmethod
    def _write_double_array(value):
        return XmlWriter._write_any_float_array(value, np.float64, "64-bit float")

    @staticmethod
    def _write_complex_double_array(value):
        return XmlWriter._write_any_complex_array(value, np.float64, np.complex128, "128-bit complex")

    @staticmethod
    def _write_complex_float_array(value):
        return XmlWriter._write_any_complex_array(value, np.float32, np.complex64, "64-bit complex")

    # ------------------------------------------------------------------------------------------------- #

    @staticmethod
    def _write_any_int_array(value, int_type, type_str):
        if isinstance(value, np.ndarray):
            if value.ndim != 1:
                raise Exception(f"A {type_str} can only be represented by numpy arrays that are 1D.")
            if value.dtype != int_type:
                raise Exception(f"A {type_str} array cannot be represented by a non {type_str} numpy array.")
            str_list = list()
            for v in value:
                str_list.append(str(v))
                str_list.append(";")
            if len(str_list) > 0:
                str_list.pop()
            return ''.join(str_list)
        elif isinstance(value, list) or isinstance(value, tuple):
            str_list = list()
            for v in value:
                if not isinstance(v, int):
                    raise Exception("A non int element was encountered in an int array.")
                if not XmlWriter.validate_integer_range(v, int_type):
                    raise Exception(f"Value {v} out of range for type {type_str}.")
                str_list.append(str(v))
                str_list.append(";")
            if len(str_list) > 0:
                str_list.pop()
            return ''.join(str_list)
        else:
            raise Exception("Writing failed.")

    @staticmethod
    def _write_any_float_array(value, float_type, type_str):
        if isinstance(value, np.ndarray):
            if value.ndim != 1:
                raise Exception(f"A {type_str} can only be represented by numpy arrays that are 1D.")
            if value.dtype != float_type:
                raise Exception(f"A {type_str} array cannot be represented by a {value.dtype} numpy array.")
            str_list = list()
            for v in value:
                str_list.append(str(v))
                str_list.append(";")
            if len(str_list) > 0:
                str_list.pop()
            return ''.join(str_list)
        elif isinstance(value, list):
            str_list = list()
            for v in value:
                if isinstance(v, numbers.Number):
                    if isinstance(v, complex):
                        raise Exception("Cannot write a complex number as a real number.")
                else:
                    raise Exception("Element is not a real number.")
                if not XmlWriter.validate_float_range(v, float_type):
                    raise Exception(f"Value {v} out of range for type {type_str}.")
                str_list.append(str(v))
                str_list.append(";")
            if len(str_list) > 0:
                str_list.pop()
            return ''.join(str_list)
        else:
            raise Exception("Writing failed.")

    @staticmethod
    def _write_any_complex_array(value, float_type, complex_type, type_str):
        if isinstance(value, np.ndarray):
            if value.ndim != 1:
                raise Exception(f"A {type_str} can only be represented by numpy arrays that are 1D.")
            if value.dtype != complex_type:
                raise Exception(f"A {type_str} array cannot be represented by a non {type_str} numpy array.")
            str_list = list()
            for v in value:
                str_list.append(f"({v.real},{v.imag})")
                str_list.append(";")
            if len(str_list) > 0:
                str_list.pop()
            return ''.join(str_list)
        elif isinstance(value, list):
            str_list = list()
            for v in value:
                if isinstance(v, numbers.Number):
                    if isinstance(v, complex):
                        if not XmlWriter.validate_float_range(v.real, float_type):
                            raise Exception(f"{type_str} out of range.")
                        if not XmlWriter.validate_float_range(v.imag, float_type):
                            raise Exception(f"{type_str} out of range.")
                    else:
                        if not XmlWriter.validate_float_range(v, float_type):
                            raise Exception(f"{type_str} out of range.")

                    str_list.append(f"({v.real},{v.imag})")
                    str_list.append(";")
                else:
                    raise Exception("Element cannot be interpreted as a complex number.")
            if len(str_list) > 0:
                str_list.pop()
            return ''.join(str_list)
        else:
            raise Exception("Writing failed.")

    @staticmethod
    def _write_any_int(value, int_type, type_str):
        if isinstance(value, int):
            if not XmlWriter.validate_integer_range(value, int_type):
                raise Exception(f"{type_str} out of range.")
            return str(value)
        elif isinstance(value, np.ndarray):
            if value.ndim != 0:
                raise Exception(f"A {type_str} cannot be represented by an numpy array with more than 0 "
                                "dimension.")
            if value.dtype != int_type:
                raise Exception(f"A single {type_str} cannot be represented by a non {type_str} numpy array.")
            return str(value)
        else:
            raise Exception(f"The type {type(value)} cannot be used to represent a {type_str}.")

    @staticmethod
    def _write_any_float(value, float_type, type_str):
        if isinstance(value, numbers.Number):
            if isinstance(value, complex):
                raise Exception("Cannot write a complex number as a real number.")
            if not XmlWriter.validate_float_range(value, float_type):
                raise Exception(f"{type_str} out of range.")
            return str(value)
        elif isinstance(value, np.ndarray):
            if value.ndim != 0:
                raise Exception(f"A {type_str} cannot be represented by an numpy array with more than 0 "
                                "dimension.")
            if value.dtype != float_type:
                raise Exception(f"A single {type_str} cannot be represented by a non {type_str} numpy array.")
            return str(value)
        else:
            raise Exception(f"The type {type(value)} cannot be used to represent a {type_str}.")

    @staticmethod
    def _write_any_complex(value, float_type, complex_type, type_str):
        if isinstance(value, complex):
            if not XmlWriter.validate_float_range(value.real, float_type):
                raise Exception(f"{type_str} out of range.")
            if not XmlWriter.validate_float_range(value.imag, float_type):
                raise Exception(f"{type_str} out of range.")
            return f"({value.real},{value.imag})"
        elif isinstance(value, np.ndarray):
            if value.ndim != 0:
                raise Exception(f"A {type_str} cannot be represented by an numpy array with more than 0 "
                                "dimension.")
            if value.dtype != complex_type:
                raise Exception(f"A single {type_str} cannot be represented by a non {type_str} numpy array.")
            return f"({value.real},{value.imag})"
        else:
            raise Exception(f"The type {type(value)} cannot be used to represent a {type_str}.")

    @staticmethod
    def validate_integer_range(value, int_info):
        return np.iinfo(int_info).min <= value <= np.iinfo(int_info).max

    @staticmethod
    def validate_float_range(value, float_info):
        if not np.isfinite(value):
            return True
        return np.finfo(float_info).min <= value <= np.finfo(float_info).max

    def _setup_writers(self):
        self._writers = {
            # Single elements
            "Boolean": lambda v: XmlWriter._write_bool(v),
            "Byte": lambda v: XmlWriter._write_byte(v),
            "SByte": lambda v: XmlWriter._write_sbyte(v),
            "Int16": lambda v: XmlWriter._write_short(v),
            "Int32": lambda v: XmlWriter._write_int(v),
            "Int64": lambda v: XmlWriter._write_long(v),
            "UInt16": lambda v: XmlWriter._write_ushort(v),
            "UInt32": lambda v: XmlWriter._write_uint(v),
            "UInt64": lambda v: XmlWriter._write_ulong(v),
            "Single": lambda v: XmlWriter._write_float(v),
            "Double": lambda v: XmlWriter._write_double(v),
            "ComplexFloat": lambda v: XmlWriter._write_complex_float(v),
            "Complex": lambda v: XmlWriter._write_complex_double(v),
            "TimeSpan": lambda v: XmlWriter._write_time_span(v),
            "DateTime": lambda v: XmlWriter._write_date_time(v),
            "Version": lambda v: XmlWriter._write_version(v),
            "String": lambda v: XmlWriter._write_string(v),
            "HeroDataType": lambda v: XmlWriter._write_Hero_data_type(v),
            "ContourType": lambda v: XmlWriter._write_contour_type(v),


            # Arrays
            "Boolean[]": lambda v: XmlWriter._write_bool_array(v),
            "Int64[]": lambda v: XmlWriter._write_long_array(v),
            "Int32[]": lambda v: XmlWriter._write_int_array(v),
            "Int16[]": lambda v: XmlWriter._write_short_array(v),
            "Single[]": lambda v: XmlWriter._write_float_array(v),
            "Double[]": lambda v: XmlWriter._write_double_array(v),
            "Complex[]": lambda v: XmlWriter._write_complex_double_array(v),
            "ComplexFloat[]": lambda v: XmlWriter._write_complex_float_array(v),
        }
"""
        "byte[]": lambda v: XmlWriter._write_byte_array(v),
        "sbyte[]": lambda v: XmlWriter._write_sbyte_array(v),

        "ushort[]": lambda v: XmlWriter._write_ushort_array(v),
        "uint[]": lambda v: XmlWriter._write_uint_array(v),
        "ulong[]": lambda v: XmlWriter._write_ulong_array(v),

        "TimeSpan[]": lambda v: XmlWriter._write_time_span_array(v),
        "DateTime[]": lambda v: XmlWriter._write_data_time_array(v),
        "Version[]": lambda v: XmlWriter._write_version_array(v),

}
"""

