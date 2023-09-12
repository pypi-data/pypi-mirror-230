# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

from abc import ABC, abstractmethod
from typing import Callable
from .Header import Header


class Reader(ABC):
    """
    Abstract baseclass defining the interface for a reader.
    """

    @abstractmethod
    def read_serializer_header(self):
        """
        Read information about the serializer
        :return:
        """
        pass

    @abstractmethod
    def read_header(self, name_to_type_str: Callable[[str], str]) -> Header:
        """
        Read the header
        :param name_to_type_str: Name of the type to be read.
        :return:
        """
        pass

    @abstractmethod
    def read_footer(self):
        """ Read the footer. No footer data is returned."""
        pass

    @abstractmethod
    def read(self, type_str: str, n: int = 1):
        """
        Read an object of specific type and length
        :param type_str: The name of the type
        :param n: If an array or composite object. The number of elements or members
        :return: The read object
        """
        pass

    @abstractmethod
    def can_read(self, type_str: str) -> bool:
        """
        Tell if a specific type can be read
        :param type_str: Name of the type.
        :return: True if it can be read.
        """
        pass

