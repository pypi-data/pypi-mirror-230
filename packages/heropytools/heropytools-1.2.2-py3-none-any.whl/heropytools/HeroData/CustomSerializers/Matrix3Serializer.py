# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

from typing import Callable, Any, Optional

import numpy as np

from heropytools.Serialization.CustomSerializer import CustomSerializer


class Matrix3Serializer(CustomSerializer):

    def write(self, obj, writer_fun: Callable[[Any, str, str, Optional[CustomSerializer]], None]):
        if not isinstance(obj, np.ndarray):
            raise Exception("An orientation matrix must be a 3 x 3 double numpy array.")
        if obj.shape != (3, 3) or obj.dtype != np.float64:
            raise Exception("An orientation matrix must be a 3 x 3 double numpy array.")
        writer_fun(obj.flatten(), "Double[]", "M3", None)

    def read(self, reader_fun: Callable[[str], Any]):
        arr, _ = reader_fun("Double[]")
        return np.reshape(arr, [3, 3])
