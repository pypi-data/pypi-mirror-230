# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

from __future__ import annotations
from typing import Callable, Any, Optional, Union
from heropytools.Serialization.Attributes import Attributes
from heropytools.Serialization.CustomSerializer import CustomSerializer
from .CustomSerializers.TensorSerializer import TensorSerializer

from .SettingsValue import SettingsValue
import numpy as np


class SettingsNDArray(SettingsValue):

    def __init__(self,  
                 value: np.ndarray, 
                 min_number_of_dimensions: int = 0,
                 max_number_of_dimensions: int = 1024,
                 general_min_dimension_size: int = 0,
                 general_max_dimension_size: int = 1024,
                 min_dimension_sizes: Union[list, tuple, np.ndarray] = None,
                 max_dimension_sizes: Union[list, tuple, np.ndarray] = None,
                 max_number_of_elements: int = 1024,
                 read_only: bool = False,
                 visible: bool = True,
                 description: str = "",
                 can_be_input: bool = False,
                 is_input: bool = False,
                 full_input_name: bool = False):

        SettingsValue.__init__(self, read_only, visible, description, can_be_input, is_input, full_input_name)

        self._min_number_of_dimensions = min_number_of_dimensions
        self._max_number_of_dimensions = max_number_of_dimensions

        self._general_min_dimension_size = general_min_dimension_size
        self._general_max_dimension_size = general_max_dimension_size

        self._min_dimension_sizes = self._get_as_np_array(min_dimension_sizes, 'min_dimension_sizes')
        self._max_dimension_sizes = self._get_as_np_array(max_dimension_sizes, 'max_dimension_sizes')
        self._max_number_of_elements = max_number_of_elements

        self._validate_constraints()

        self._value = None
        self._set_value(value)

    @staticmethod
    def _get_as_np_array(sizes, name):
        if sizes is None:
            return np.zeros([0], dtype=np.int64)
        else:
            if isinstance(sizes, (list, tuple)):
                if len(sizes) == 0:
                    return np.zeros([0], dtype=np.int64)
                else:
                    return np.ndarray(sizes, dtype=np.int64)
            elif isinstance(sizes, np.ndarray):
                if sizes.ndim != 1 or not np.issubdtype(sizes.dtype, np.integer):
                    raise ValueError(f"{name} must be 1-D vector of integers.")
                return sizes.astype(dtype=np.int64)
            else:
                raise ValueError(f"{name} is of wrong type.")

    def _validate_constraints(self):
        if self._min_number_of_dimensions < 0:
            raise ValueError("The allowed minimum number of dimension cannot be set less than 0.")

        if self._max_number_of_dimensions < 0:
            raise ValueError("The allowed maximum number of dimension cannot be set less than 0.")

        if self._max_number_of_dimensions < self._min_number_of_dimensions:
            raise ValueError("The allowed maximum number of dimension cannot be smaller than the allowed minimum number of dimension.")

        if self._general_min_dimension_size < 0:
            raise ValueError("The general allowed minimum dimension size cannot be set less than 0.")

        if self._general_max_dimension_size < 0:
            raise ValueError("The general allowed maximum dimension size cannot be set less than 0.")

        if self._general_max_dimension_size < self._general_min_dimension_size:
            raise ValueError("The allowed general maximum dimension size cannot be smaller than the allowed general minimum dimension size.")

        if self._max_number_of_elements < 0:
            raise ValueError("The maximum number of elements cannot be less than 0.")

        for i in range(self._min_dimension_sizes.size, self._max_dimension_sizes.size):
            min_size = self._min_dimension_sizes[i] if i < self._min_dimension_sizes.size else self._general_min_dimension_size
            max_size = self._max_dimension_sizes[i] if i < self._max_dimension_sizes.size else self._general_max_dimension_size

            if max_size < min_size:
                raise ValueError(f"The maximum size of dimension {i} is {max_size} and it is smaller than the minimum size {min_size} of the dimension.")

    def _set_value(self, value: np.ndarray):

        if not isinstance(value, np.ndarray):
            raise Exception("The value must be a numpy array.")

        self._validate_shape(value)

        if self._value is None:
            self._value = value
        else:
            if self._value.dtype == bool and value.dtype != bool:
                raise TypeError("Cannot convert number array to a bool array.")

            if self._value.dtype != bool and value.dtype == bool:
                raise TypeError("Cannot convert bool array to a number array.")

            if self._value.dtype != value.dtype:
                self._value = value.astype(self._value.dtype)
            else:
                self._value = value

    def _validate_shape(self, value: np.ndarray):

        shape = value.shape
        if len(shape) < self._min_number_of_dimensions or len(shape) > self._max_number_of_dimensions:
            raise ValueError(f"The number of dimensions {len(shape)} is not in the allowed range [{self._min_number_of_dimensions}, {self._max_number_of_dimensions}].")

        n_elements = value.size
        if n_elements > self._max_number_of_elements:
            raise ValueError(f"The number of elements {n_elements} is larger than the maximum allowed: {self._max_number_of_elements}.")

        for i in range(len(shape)):
            min_size = self._min_dimension_sizes[i] if i < self._min_dimension_sizes.size else self._general_min_dimension_size
            max_size = self._max_dimension_sizes[i] if i < self._max_dimension_sizes.size else self._general_max_dimension_size

            if shape[i] < min_size or shape[i] > max_size:
                raise ValueError(f"The size of dimension {i} is {shape[i]} and it is not in the allowed range [{min_size}, {max_size}].")
        
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        self._set_value(value)

    @value.deleter
    def value(self):
        raise AttributeError("Attribute is not deletable.")

    @property
    def dtype(self):
        return self._value.dtype
    
    @dtype.setter
    def dtype(self, value):
        raise AttributeError("Attribute is not writable.")

    @dtype.deleter
    def dtype(self):
        raise AttributeError("Attribute is not deletable.")

    @staticmethod
    def create_from_dict(data: dict):
        s = SettingsNDArray(data["_value"], data["_min_number_of_dimensions"], data["_max_number_of_dimensions"], data["_general_min_dimension_size"], 
                            data["_general_max_dimension_size"], data["_min_dimension_sizes"], data["_max_dimension_sizes"], data["_max_number_of_elements"], 
                            data["_read_only"], data["_visible"], data["_description"], data["_can_be_input"], data["_is_input"], data["_full_input_name"])
        s._id = data["_id"]
        return s

    def __eq__(self, other):
        return super(SettingsNDArray, self).__eq__(other) and \
                np.all(self._value == other._value) and \
                self._value.dtype == other._value.dtype and \
                self._min_number_of_dimensions == other._min_number_of_dimensions and \
                self._max_number_of_dimensions == other._max_number_of_dimensions and \
                self._general_min_dimension_size == other._general_min_dimension_size and \
                self._general_max_dimension_size == other._general_max_dimension_size and \
                self._compare_lists(self._min_dimension_sizes, other._min_dimension_sizes) and \
                self._compare_lists(self._max_dimension_sizes, other._max_dimension_sizes) and \
                self._max_number_of_elements == other._max_number_of_elements

    def __repr__(self) -> str:
        return f'SettingsNDArray: [value: {self.value}, ' + super().__repr__()

    @staticmethod
    def _compare_lists(x, y):
        if len(x) != len(y):
            return False
        for i in range(len(x)):
            if x[i] != y[i]:
                return False
        return True
    
    # --- Autogenerated --- #

    # Name of the type.
    _type_str = "SettingsNDArray"

    # Datatype attributes.
    _attributes = Attributes("SettingsNDArray", version=0, member_count=15)

    # Serialization.
    def serialize(self, writer_fun: Callable[[Any, str, str, Optional[CustomSerializer]], None]):
        super(SettingsNDArray, self).serialize(writer_fun)
        writer_fun(self._general_max_dimension_size, "Int64", "GMA", None)
        writer_fun(self._general_min_dimension_size, "Int64", "GMI", None)
        writer_fun(self._max_number_of_dimensions, "Int32", "MA", None)
        writer_fun(self._max_number_of_elements, "Int64", "MAE", None)
        writer_fun(self._min_number_of_dimensions, "Int32", "MI", None)
        writer_fun(self._max_dimension_sizes, "Int64[]", "SMA", None)
        writer_fun(self._min_dimension_sizes, "Int64[]", "SMI", None)
        writer_fun(self._value, "Tensor", "V", TensorSerializer())

    # Deserialization.
    @staticmethod
    def deserialize(reader_fun: Callable[[str, Optional[CustomSerializer]], Any]):
        data = super(SettingsNDArray, SettingsNDArray).deserialize(reader_fun)
        data["_general_max_dimension_size"], _ = reader_fun("Int64", None)
        data["_general_min_dimension_size"], _ = reader_fun("Int64", None)
        data["_max_number_of_dimensions"], _ = reader_fun("Int32", None)
        data["_max_number_of_elements"], _ = reader_fun("Int64", None)
        data["_min_number_of_dimensions"], _ = reader_fun("Int32", None)
        data["_max_dimension_sizes"], _ = reader_fun("Int64[]", None)
        data["_min_dimension_sizes"], _ = reader_fun("Int64[]", None)
        data["_value"], _ = reader_fun("Tensor", TensorSerializer())
        return data
