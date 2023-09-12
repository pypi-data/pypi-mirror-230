# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

from __future__ import annotations
from typing import Callable, Any, Optional
from abc import ABC, abstractmethod


class CustomSerializer(ABC):
    """
    Abstract baseclass for all custom serializers.
    """

    @abstractmethod
    def write(self, obj, writer_fun:  Callable[[Any, str, str, Optional[CustomSerializer]], None]):
        """
        Writes the custom object
        :param obj: Object to be written
        :param writer_fun: Lambda used for writing members of the object
        :return:
        """
        pass

    @abstractmethod
    def read(self, reader_fun:  Callable[[str], Any]):
        """
        Reads the custom object
        :param reader_fun: Lambda used for reading members of the object.
        :return:
        """
        pass

