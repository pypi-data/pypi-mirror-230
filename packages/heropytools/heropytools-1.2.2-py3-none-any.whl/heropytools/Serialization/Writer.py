# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

from abc import ABC, abstractmethod
from .Header import Header


class Writer(ABC):
    """
    Abstract baseclass defining the interface for a writer.
    """

    @abstractmethod
    def write_serializer_header(self, object_name: str, version: str):
        """
        Write information about the serializer.
        :param object_name:
        :param version: The version of the serializer
        :return:
        """
        pass

    @abstractmethod
    def write_header(self, h: Header):
        """
        Write a header
        :param h: The header to be written.
        :return: Return nothing.
        """
        pass

    @abstractmethod
    def write_footer(self):
        """
        Writes a footer
        :return: Returns nothing.
        """
        pass

    @abstractmethod
    def write(self, obj, type_str: str):
        """
        Write an object
        :param obj: Object to write
        :param type_str: The name of the type.
        :return: Returns nothing.
        """
        pass

    @abstractmethod
    def can_write(self, type_str: str) -> bool:
        """
        Tell if specific type can be written
        :param type_str: Name of the type.
        :return: True if it can be written.
        """
        pass

    @abstractmethod
    def get_size(self, obj, type_str: str) -> int:
        """
        Get size of an object
        :param obj: The object
        :param type_str: Name of the object type
        :return: Returns the size.
        """
        pass
