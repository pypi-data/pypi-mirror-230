# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

from typing import Callable, Any, Optional

from heropytools.Serialization.CustomSerializer import CustomSerializer


class DictionarySerializer(CustomSerializer):

    def __init__(self, t_key: str, t_value: str):
        self.t_key = t_key
        self.t_value = t_value

    def write(self, obj, writer_fun: Callable[[Any, str, str, Optional[CustomSerializer]], None]):
        keys = list(obj.keys())
        values = list(obj.values())
        writer_fun(keys, f"{self.t_key}[]", "K", None)
        writer_fun(values, f"{self.t_value}[]", "V", None)

    def read(self, reader_fun: Callable[[str], Any]):
        keys, _ = reader_fun(f"{self.t_key}[]")
        values, _ = reader_fun(f"{self.t_value}[]")
        dictionary = {keys[i]: values[i] for i in range(len(keys))}
        return dictionary
