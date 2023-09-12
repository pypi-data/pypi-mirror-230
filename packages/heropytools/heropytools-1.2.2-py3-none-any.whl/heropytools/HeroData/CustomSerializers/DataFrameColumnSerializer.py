# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

from datetime import timedelta
from datetime import datetime
from typing import Callable, Any, Optional
from pandas import Series
import pandas as pd
import numpy as np

from heropytools.Serialization.CustomSerializer import CustomSerializer


class DataFrameColumnSerializer(CustomSerializer):

    _buffer_size_in_bytes = 16_777_216

    _scalar_size = {
        "Boolean": 1,
        "Int32": 4,
        "Int64": 8,
        "Single": 4,
        "Double": 8,
        "ComplexFloat": 8,
        "Complex": 16,
        "TimeSpan": 8,
        "DateTime": 8,
        "String": -1,
    }

    _python_to_data_type_name = {
        "bool": "Boolean",
        "int32": "Int32",
        "int64": "Int64",
        "float32": "Single",
        "float64": "Double",
        "complex64": "ComplexFloat",
        "complex128": "Complex",
        'timedelta64[ns]': "TimeSpan",
        'datetime64[ns]': "DateTime",
        'object': "String",
        'string': "String",
        # additional nullable types
        "boolean": "Boolean",
        "Int32": "Int32",
        "Int64": "Int64",
        "Float32": "Single",
        "Float64": "Double",
        # Note: Complex nullable types are missing in Pandas at this moment. v1.3.4.
    }

    _name_type_map = {
        "TimeSpan": "timedelta64[ns]",
        "DateTime": "datetime64[ns]",
    }

    _is_nullable_type = {
        "boolean",
        "Int32",
        "Int64",
        "Float32",
        "Float64",
        "timedelta64[ns]",
        "datetime64[ns]",
        "object",
        "string",
    }

    _numpy_types = {
        "Boolean": bool,
        "Int32": np.int32,
        "Int64": np.int64,
        "Single": np.float32,
        "Double": np.float64,
        "ComplexFloat": np.complex64,
        "Complex": np.complex128,
    }

    def write(self, obj, writer_fun: Callable[[Any, str, str, Optional[CustomSerializer]], None]):
        if not isinstance(obj, Series):
            raise Exception("Failed to serialize data: Expected a pandas.Series object.")

        name = obj.name
        length = len(obj)

        if not (obj.dtype.name in self._python_to_data_type_name):
            raise Exception(f"Cannot interpret a column of type {obj.dtype.name} as a HeroColumn.")
        data_type_name = self._python_to_data_type_name[obj.dtype.name]

        writer_fun(data_type_name, "String", "DataTypeName", None)
        writer_fun(name, "String", "Name", None)
        writer_fun(length, "Int64", "Length", None)

        if length > 0:
            if data_type_name == "String":
                self._write_string_column(obj, writer_fun)
            else:
                self._write_column(obj, length, self._scalar_size[data_type_name], writer_fun)

    def read(self, reader_fun: Callable[[str], Any]):
        data_type_name, _ = reader_fun("String")
        name, _ = reader_fun("String")
        length, _ = reader_fun("Int64")

        if data_type_name == "String":
            c = self._read_string_column(reader_fun, name, length)
        else:
            c = self._read_column(reader_fun, data_type_name, name, length)
        return c

    @staticmethod
    def is_serializable(column: Series) -> bool:
        return column.dtype.name in DataFrameColumnSerializer._python_to_data_type_name

    def _write_column(self, obj, column_length: int, scalar_size: int, writer_fun):
        array_buffer_size = min(column_length, self._buffer_size_in_bytes // scalar_size)

        # Check if actual null type
        is_nullable = obj.dtype.name in self._is_nullable_type

        # Data type name
        data_type_name = self._python_to_data_type_name[obj.dtype.name]

        # Check if numpy representation exist
        is_numpy = data_type_name in self._numpy_types

        block = 0
        for start in range(0, column_length, array_buffer_size):
            n = min(array_buffer_size, column_length - start)
            block_name = f"B{block}"
            null_name = f"N{block}"

            # Get the block data
            stop = start + n
            buffer = obj[start:stop]

            # Get null mask
            if is_nullable:
                is_null_buffer = buffer.isna().to_numpy()
            else:
                is_null_buffer = np.zeros(n, dtype=bool)

            # Get buffer
            if is_numpy:
                if is_nullable:
                    np_type = self._numpy_types[data_type_name]
                    buffer = buffer.to_numpy(dtype=np_type, na_value=0)
                else:
                    buffer = buffer.to_numpy()
            else:
                buffer = list(buffer)

                # Need to take care of pandas special datetime
                if data_type_name == 'DateTime':
                    for i in range(len(buffer)):
                        if is_null_buffer[i]:
                            buffer[i] = datetime(1, 1, 1)
                        else:
                            dt = buffer[i]
                            buffer[i] = dt.to_pydatetime()
                elif data_type_name == 'TimeSpan':
                    if is_null_buffer.any():
                        for i in range(len(buffer)):
                            if is_null_buffer[i]:
                                buffer[i] = timedelta(seconds=0)

            # Write the data
            writer_fun(buffer, data_type_name + '[]', block_name, None)
            writer_fun(is_null_buffer, 'Boolean[]', null_name, None)

    def _read_column(self, reader_fun, data_type_name, name, length):

        # Check if numpy representation exist
        is_numpy = data_type_name in self._numpy_types

        # Create buffer for the data
        if is_numpy:
            d_type = self._numpy_types[data_type_name]
            data_buffer = np.zeros(length, dtype=d_type)
        else:
            data_buffer = list()

        # Special case
        if length == 0:
            if is_numpy:
                return Series(data_buffer, name=name)
            else:
                return Series(name=name, dtype=self._name_type_map[data_type_name])

        isnull_buffer = np.zeros(length, dtype=bool)

        # Read the data
        n_read = 0
        while n_read < length:
            buffer, _ = reader_fun(data_type_name + '[]')
            isnull, _ = reader_fun('Boolean[]')
            start = n_read
            n_read += isnull.size
            stop = n_read
            isnull_buffer[start:stop] = isnull

            if is_numpy:
                data_buffer[start:stop] = buffer
            else:
                data_buffer.extend(buffer)

        # Convert to pandas columns: Series or arrays
        any_null = isnull_buffer.any()

        if any_null:
            if is_numpy:
                s = Series(pd.array(data_buffer), name=name)
                s[isnull_buffer] = None
            else:
                s = Series(data_buffer, name=name)
                s[isnull_buffer] = pd.NaT
            return s
        else:
            return Series(data_buffer, name=name)

    def _write_string_column(self, column, writer_fun):
        for i, string_block in enumerate(self._string_block_enumerator(column)):
            writer_fun(string_block, "String[]", f"B{i}", None)

    def _string_block_enumerator(self, column):
        block = list()
        m = 0
        for string in column:

            if string is not None and not isinstance(string, str):
                string = str(string)

            if string is None:
                length = 1
            else:
                length = len(string)

            if len(block) > 0 and length > self._buffer_size_in_bytes:
                yield block
                m = 0
                block = list()

            m += length
            block.append(string)

        if len(block) > 0:
            yield block

    @staticmethod
    def _read_string_column(reader_fun, name, length):
        if length == 0:
            return Series(dtype=str, name=name)
        column_data = list()
        n_read = 0
        while n_read < length:
            strings, _ = reader_fun("String[]")
            column_data.extend(strings)
            n_read += len(strings)

        return Series(column_data, dtype=str, name=name)


