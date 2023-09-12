# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

from typing import Callable, Any, Optional
import numpy as np

from heropytools.Serialization.CustomSerializer import CustomSerializer


class TensorSerializer(CustomSerializer):

    _buffer_size_in_bytes = 16_777_216
    _small_1d_array_max_size = 4096

    # Note: Half support is excluded. Untested feature in cstorch.
    _scalar_id_map = {np.uint8.__name__: 0, np.int8.__name__: 1, np.int16.__name__: 2, np.int32.__name__: 3,
                      np.int64.__name__: 4, np.float32.__name__: 6, np.float64.__name__: 7, np.complex64.__name__: 9,
                      np.complex128.__name__: 10, bool.__name__: 11}
    _scalar_type_map = {0: np.uint8, 1: np.int8, 2: np.int16, 3: np.int32, 4: np.int64, 6: np.float32,
                        7: np.float64, 9: np.complex64, 10: np.complex128, 11: bool}
    _scalar_name = {0: "UInt8", 1: "Int8", 2: "Int16", 3: "Int32", 4: "Int64", 6: "Single",
                    7: "Double", 9: "ComplexFloat", 10: "Complex", 11: "Boolean"}

    def write(self, obj, writer_fun: Callable[[Any, str, str, Optional[CustomSerializer]], None]):

        if isinstance(obj, float):
            obj = np.array(obj)
        elif isinstance(obj, int):
            obj = np.array(obj)
        elif isinstance(obj, bool):
            obj = np.array(obj)
        elif isinstance(obj, complex):
            # Odd type hint issue here. Probably numpy typehint issue. Cause no problem
            obj = np.array(obj)

        if not isinstance(obj, np.ndarray):
            raise Exception("Data could not be interpreted as a numeric array.")

        shape = obj.shape
        n = obj.size
        d_type = obj.dtype
        scalar_type_id = self._get_scalar_id(d_type)
        d_type_size = obj.itemsize

        is_scalar = obj.ndim == 0
        is_small_array = True if not is_scalar and len(shape) == 1 and shape[0] <= self._small_1d_array_max_size else False

        scalar_info = scalar_type_id << 8 | (int(is_small_array) << 1) | int(is_scalar)
        writer_fun(scalar_info, "Int16", "SI", None)

        if is_scalar:
            writer_fun(obj, self._scalar_name[scalar_type_id], "V", None)
        elif is_small_array:
            array_type_str = self._scalar_name[scalar_type_id] + '[]'
            writer_fun(obj, array_type_str, "V", None)
        else:
            array_buffer_size = min(self._buffer_size_in_bytes // d_type_size, n)
            n_blocks = n // array_buffer_size if array_buffer_size > 0 else 0
            if n_blocks * array_buffer_size < n:
                n_blocks += 1

            writer_fun(shape, "Int64[]", "SH", None)
            writer_fun(array_buffer_size, "Int32", "BS", None)
            writer_fun(n_blocks, "Int32", "NB", None)

            array_type_str = self._scalar_name[scalar_type_id] + '[]'
            self._write_tensor(obj, n, array_buffer_size, n_blocks, array_type_str, writer_fun)

    def read(self, reader_fun: Callable[[str], Any]):
        scalar_info, _ = reader_fun("Int16")
        scalar_type_id = scalar_info >> 8
        is_scalar = scalar_info & 0x01
        is_small_array = scalar_info & 0x02
        d_type = self._scalar_type_map[scalar_type_id]

        if is_scalar:
            t, _ = reader_fun(self._scalar_name[scalar_type_id])
            #t = np.array(t, dtype=d_type)
        elif is_small_array:
            array_type_str = self._scalar_name[scalar_type_id] + '[]'
            t, _ = reader_fun(array_type_str)
        else:
            shape, _ = reader_fun("Int64[]")
            n = np.prod(shape)
            array_buffer_size, _ = reader_fun("Int32")
            n_blocks, _ = reader_fun("Int32")
            array_type_str = self._scalar_name[scalar_type_id] + '[]'
            t = self._read_tensor(shape, n, array_buffer_size, n_blocks, array_type_str, d_type, reader_fun)
        return t

    @staticmethod
    def _get_scalar_id(d_type):
        if not (d_type.name in TensorSerializer._scalar_id_map):
            raise Exception(f"Writing an array of type: {d_type.name} is not supported.")
        return TensorSerializer._scalar_id_map[d_type.name]

    @staticmethod
    def _write_tensor(obj, n: int, array_buffer_size: int, n_blocks: int, array_type_str: str, writer_fun):
        flat_data = obj.reshape(n)
        for i in range(n_blocks):
            start = array_buffer_size * i
            stop = min(start + array_buffer_size, n)
            block = flat_data[start:stop]
            block_name = f"B{i}"
            writer_fun(block, array_type_str, block_name, None)

    @staticmethod
    def _read_tensor(shape, n, array_buffer_size, n_blocks, array_type_str, d_type, reader_fun):
        t = np.zeros(shape, dtype=d_type)
        for i in range(n_blocks):
            start = array_buffer_size * i
            stop = min(start + array_buffer_size, n)
            t.flat[start:stop], _ = reader_fun(array_type_str)
        return t
