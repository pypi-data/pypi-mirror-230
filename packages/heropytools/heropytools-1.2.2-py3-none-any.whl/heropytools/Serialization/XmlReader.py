# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

import numpy as np
from typing import Dict
from .Header import Header
from .Reader import Reader
import xml.etree.ElementTree as ET
from datetime import timedelta
from datetime import datetime
import base64
from heropytools.HeroData.Version import Version
from heropytools.HeroData.HeroDataType import HeroDataType
from heropytools.HeroData.Contour import ContourType
from typing import Callable


class XmlReader(Reader):

    _storage_format_name_map = {'COMPOSITE': Header.COMPOSITE, 'ARRAY': Header.ARRAY, 'ATOMIC': Header.ATOMIC}

    def __init__(self, file_name):
        self.fileName = file_name
        self.tree = ET.parse(file_name)
        self._readers = self._setup_readers()
        self.iterator = None
        self.current = None

    def __enter__(self):
        self.iterator = self.tree.iter()
        self.current = None
        return self

    def __exit__(self, t, v, t2):
        self.iterator = None
        self.current = None

    def read_serializer_header(self):
        self.current = next(self.iterator)
        attr = self.current.attrib
        return self.current.tag, attr["Serializer"]

    def read_header(self, name_to_type_str: Callable[[str], str]) -> Header:
        self.current = next(self.iterator)
        attr = self.current.attrib

        if 'F' in attr:
            storage_format = XmlReader._storage_format_name_map[attr['F']]
        else:
            storage_format = Header.ATOMIC

        h = Header(storage_format=storage_format, name=self.current.tag)

        if 'T' in attr:
            h.type_name = name_to_type_str(attr['T'])
        if 'NS' in attr:
            h.name_space = attr['NS']
        if 'N' in attr:
            h.is_null = attr['N'] == '1'
        if 'S' in attr:
            h.content_size = int(attr['S'])
        if 'V' in attr:
            h.version = int(attr['V'])

        return h

    def read_footer(self):
        """"""
        # Nothing to do.
        pass

    def read(self, type_str: str, n: int = 1):
        return self._readers[type_str](n)

    def can_read(self, type_str: str):
        return type_str in self._readers

    def _setup_readers(self) -> Dict:
        readers = {
            # Single elements
            "Boolean": lambda ni: self.current.text == "True",
            "Byte": lambda ni: int(self.current.text),
            "SByte": lambda ni: int(self.current.text),
            "Int16": lambda ni: int(self.current.text),
            "Int32": lambda ni: int(self.current.text),
            "Int64": lambda ni: int(self.current.text),
            "UInt16": lambda ni: int(self.current.text),
            "UInt32": lambda ni: int(self.current.text),
            "UInt64": lambda ni: int(self.current.text),
            "Single": lambda ni: float(self.current.text),
            "Double": lambda ni: float(self.current.text),
            "Complex": lambda ni: self._read_complex(self.current.text),
            "ComplexFloat": lambda ni: self._read_complex(self.current.text),

            "TimeSpan": lambda ni: timedelta(seconds=float(self.current.text)),
            "DateTime": lambda ni: XmlReader._read_date_time(self.current.text),
            "Version": lambda ni: Version.from_string(self.current.text),
            "String": lambda ni: XmlReader._read_string(self.current.text),
            "HeroDataType": lambda ni: HeroDataType(int(self.current.text)),
            "ContourType": lambda ni: ContourType(int(self.current.text)),

            # Arrays
            "Boolean[]": lambda ni: XmlReader._read_bool_array(self.current.text, ni),
            "Int64[]": lambda ni: XmlReader._read_array(self.current.text, ni, int, np.int64),
            "Int32[]": lambda ni: XmlReader._read_array(self.current.text, ni, int, np.int32),
            "Int16[]": lambda ni: XmlReader._read_array(self.current.text, ni, int, np.int16),
            "Single[]": lambda ni: XmlReader._read_array(self.current.text, ni, float, np.float32),
            "Double[]": lambda ni: XmlReader._read_array(self.current.text, ni, float, np.float64),
            "Complex[]": lambda ni: XmlReader._read_complex_array(self.current.text, ni, np.complex128),
            "ComplexFloat[]": lambda ni: XmlReader._read_complex_array(self.current.text, ni, np.complex64),
        }
        return readers

    @staticmethod
    def _read_date_time(v: str):
        n_tot = int(v)
        n_s = n_tot // 10_000_000
        n_us = (n_tot - n_s * 10_000_000) / 10
        return datetime(1, 1, 1) + timedelta(seconds=n_s, microseconds=n_us)

    @staticmethod
    def _read_string(text: str):
        if text is None:
            return ""
        if text.strip() == "":
            return ""
        base64_bytes = bytes(text, 'utf-8')
        text_bytes = base64.b64decode(base64_bytes)
        return text_bytes.decode('utf-8')

    @staticmethod
    def _read_array(text: str, ni: int, interpret_type, np_type):
        if ni == 0:
            return np.zeros([0], dtype=np_type)
        return np.fromstring(text, count=ni, dtype=interpret_type, sep=';').astype(np_type)

    @staticmethod
    def _read_bool_array(text: str, ni: int):
        arr = np.zeros(ni, dtype=bool)
        values = text.split(sep=';')
        for i in range(ni):
            arr[i] = values[i] == '1'
        return arr

    @staticmethod
    def _read_complex(text: str):
        parts = text.strip('()').split(',')
        return float(parts[0]) + 1j * float(parts[1])

    @staticmethod
    def _read_complex_array(text, ni, complex_format):
        elements = text.split(';')
        if len(elements) != ni:
            raise Exception("Actual and expected number of elements in array don't match.")
        values = np.zeros(ni, dtype=complex_format)
        for i in range(ni):
            values[i] = XmlReader._read_complex(elements[i])
        return values

