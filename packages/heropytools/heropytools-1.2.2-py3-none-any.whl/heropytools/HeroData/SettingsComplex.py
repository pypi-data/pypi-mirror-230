# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

from __future__ import annotations
from typing import Callable, Any, Optional
from heropytools.Serialization.Attributes import Attributes
from heropytools.Serialization.CustomSerializer import CustomSerializer

from .SettingsValue import SettingsValue


class SettingsComplex(SettingsValue):

    def __init__(self, value = 0, min_real = float('-inf'), max_real = float('inf'),
            min_imag = float('-inf'), max_imag = float('inf'),
            min_magnitude = 0, max_magnitude = float('inf'), allow_nan = True, read_only=False, visible=True, description="", can_be_input=False, is_input=False, full_input_name=True):

        SettingsValue.__init__(self, read_only, visible, description, can_be_input, is_input, full_input_name)
        self._value = value
        self._min_real = min_real
        self._max_real = max_real
        self._min_imag = min_imag
        self._max_imag = max_imag
        self._min_magnitude = min_magnitude
        self._max_magnitude = max_magnitude
        self._allow_nan = allow_nan
        
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        raise AttributeError("Attribute is not writable.")

    @value.deleter
    def value(self):
        raise AttributeError("Attribute is not deletable.")
    
    @property
    def min_real(self):
        return self._min_real
    
    @min_real.setter
    def min_real(self, value):
        raise AttributeError("Attribute is not writable.")

    @min_real.deleter
    def min_real(self):
        raise AttributeError("Attribute is not deletable.")
    
    @property
    def max_real(self):
        return self._max_real
    
    @max_real.setter
    def val_max_real(self, value):
        raise AttributeError("Attribute is not writable.")

    @max_real.deleter
    def max_real(self):
        raise AttributeError("Attribute is not deletable.")
    
    @property
    def min_imag(self):
        return self._min_imag
    
    @min_imag.setter
    def min_real(self, value):
        raise AttributeError("Attribute is not writable.")

    @min_imag.deleter
    def min_imag(self):
        raise AttributeError("Attribute is not deletable.")
    
    @property
    def max_imag(self):
        return self._max_imag
    
    @max_imag.setter
    def max_imag(self, value):
        raise AttributeError("Attribute is not writable.")

    @max_imag.deleter
    def max_imag(self):
        raise AttributeError("Attribute is not deletable.")
    
    @property
    def min_magnitude(self):
        return self._min_magnitude
    
    @min_magnitude.setter
    def min_magnitude(self, value):
        raise AttributeError("Attribute is not writable.")

    @min_magnitude.deleter
    def min_magnitude(self):
        raise AttributeError("Attribute is not deletable.")
    
    @property
    def max_magnitude(self):
        return self._max_magnitude
    
    @max_magnitude.setter
    def max_magnitude(self, value):
        raise AttributeError("Attribute is not writable.")

    @max_magnitude.deleter
    def max_magnitude(self):
        raise AttributeError("Attribute is not deletable.")
    
    @property
    def allow_nan(self):
        return self._allow_nan
    
    @allow_nan.setter
    def allow_nan(self, value):
        raise AttributeError("Attribute is not writable.")

    @allow_nan.deleter
    def allow_nan(self):
        raise AttributeError("Attribute is not deletable.")
    
    def __repr__(self) -> str:
        return f'Complex: [value: {self.value}, min_real: {self.min_real}, max_real: {self.max_real}, min_imag: {self.min_imag}, max_imag: {self.max_imag}, min_magnitude: {self.min_magnitude}, max_imag: {self.max_magnitude}, allow_nan: {self.allow_nan}, ' + super().__repr__()

    @staticmethod
    def create_from_dict(data: dict):
        s = SettingsComplex(data["_value"], data["_min_real"], data["_max_real"], data["_min_imag"], data["_max_imag"], data["_min_magnitude"], data["_max_magnitude"], data["_allow_nan"],
        data["_read_only"], data["_visible"], data["_description"], data["_can_be_input"], data["_is_input"], data["_full_input_name"])
        s._id = data["_id"]
        return s

    def __eq__(self, other):
        return super(SettingsComplex, self).__eq__(other) and self._value == other._value and self._min_real == other._min_real and self._max_real == other._max_real and \
        self._min_imag == other._min_imag and self._max_imag == other._max_imag and self._min_magnitude == other._min_magnitude and self._max_magnitude == other._max_magnitude and self._allow_nan == other._allow_nan
    
    # --- Autogenerated --- #

    # Name of the type.
    _type_str = "SettingsComplex"

    # Datatype attributes.
    _attributes = Attributes("SettingsComplex", version=0, member_count=15)

    # Serialization.
    def serialize(self, writer_fun: Callable[[Any, str, str, Optional[CustomSerializer]], None]):
        super(SettingsComplex, self).serialize(writer_fun)
        writer_fun(self._max_imag, "Double", "MaxI", None)
        writer_fun(self._max_magnitude, "Double", "MaxM", None)
        writer_fun(self._max_real, "Double", "MaxR", None)
        writer_fun(self._min_imag, "Double", "MinI", None)
        writer_fun(self._min_magnitude, "Double", "MinM", None)
        writer_fun(self._min_real, "Double", "MinR", None)
        writer_fun(self._allow_nan, "Boolean", "NaN", None)
        writer_fun(self._value, "Complex", "V", None)

    # Deserialization.
    @staticmethod
    def deserialize(reader_fun: Callable[[str, Optional[CustomSerializer]], Any]):
        data = super(SettingsComplex, SettingsComplex).deserialize(reader_fun)
        data["_max_imag"], _ = reader_fun("Double", None)
        data["_max_magnitude"], _ = reader_fun("Double", None)
        data["_max_real"], _ = reader_fun("Double", None)
        data["_min_imag"], _ = reader_fun("Double", None)
        data["_min_magnitude"], _ = reader_fun("Double", None)
        data["_min_real"], _ = reader_fun("Double", None)
        data["_allow_nan"], _ = reader_fun("Boolean", None)
        data["_value"], _ = reader_fun("Complex", None)
        return data
