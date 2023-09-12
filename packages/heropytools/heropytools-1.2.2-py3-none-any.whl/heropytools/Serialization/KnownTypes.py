# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

from .Attributes import Attributes


class TypeInfo:
    """
    Contains information about a serializable type.
    """
    def __init__(self, type_name: str, version: int = 0, ns: str = '', member_count: int = 1,
                 known_types: list = None):
        """
        Construct an object
        :param type_name: Name of the type
        :param version: Version of the type
        :param ns: Namespace for the name of the type
        :param member_count: Number of members in the type or array
        :param known_types: Types that needs to be known to the type. (Not used.)
        """
        self.type_name = type_name
        self.version = version
        self.ns = ns
        self.member_count = member_count
        if known_types is None:
            self.known_types = list()
        else:
            self.known_types = known_types


class KnownTypes:
    """Convenience class for querying information about a type."""

    def __init__(self, known_types: list):
        """
        Construct the object
        :param known_types: A list of all types that can be serialized/deserialized.
        """

        self._know_types, self._classes = self._build_known_table(known_types)
        self._name_map = self._create_name_map()

    def get_type_info(self, prescribed_type_str: str, obj=None) -> TypeInfo:
        """
        Get info about an object (obj) if this is None the info is fetched from the name of the type
        :param prescribed_type_str: Name of the type
        :param obj: An instance of a serializable object
        :return:
        """
        if obj is None:
            return self._know_types[prescribed_type_str]
        else:
            return self._know_types[obj.type_str]

    def get_type_from_alias(self, alias: str) -> str:
        """
        Get the name of the type from the serialized alias.
        :param alias:
        :return:
        """
        return self._name_map[alias]

    def is_known(self, type_str: str) -> bool:
        """
        Check if the type is known
        :param type_str: The name of the type to check.
        :return:
        """
        return type_str in self._know_types

    def get_class(self, type_str):
        """
        Get the class object from the name of the class
        :param type_str: The name.
        :return:
        """
        if type_str in self._know_types:
            return self._classes[type_str]
        else:
            raise Exception(f"Type {type_str} not found.")

    # -------------------------------------------------- #
    #           Private helper methods below.
    # -------------------------------------------------- #

    def _create_name_map(self):
        """
        Build a map from type names to names.
        :return:
        """
        name_map = dict()
        for name in self._know_types:
            name_map[self._know_types[name].type_name] = name
        return name_map

    @staticmethod
    def _build_known_table(known_types: list) -> (dict, dict):
        """
        Build a tables (maps) from names to type information and from names to classes.
        :param known_types:
        :return:
        """
        kt_info = dict()
        classes = dict()
        for element in known_types:
            if hasattr(element, "_type_str") and hasattr(element, "_attributes"):
                type_str = element._type_str # noqa
                attributes: Attributes = element._attributes # noqa
                type_info = TypeInfo(attributes.type_name, attributes.version, attributes.ns, attributes.member_count,
                                     attributes.known_types)
                kt_info[type_str] = type_info
                classes[type_str] = element

        return kt_info, classes


