# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

from typing import Callable, Any, Optional
from heropytools.HeroData.HeroColumn import HeroColumn

from heropytools.Serialization.CustomSerializer import CustomSerializer
import pandas as pd


class DataFrameSerializer(CustomSerializer):

    def write(self, obj, writer_fun: Callable[[Any, str, str, Optional[CustomSerializer]], None]):
        columns = list()
        for c_name in obj:
            columns.append(HeroColumn(obj[c_name]))

        writer_fun(columns, "HeroColumn[]", "Columns", None)

    def read(self, reader_fun: Callable[[str], Any]):
        columns, _ = reader_fun("HeroColumn[]")
        df = pd.concat(columns, axis=1, keys=[s.name for s in columns])
        return df


