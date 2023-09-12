# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

class Attributes:
    """
    Represents attributes needed for serialization of a class.
    """
    def __init__(self, type_name: str, version: int = 0, ns: str = None, member_count: int = 1,
                 known_types: list = None):
        """
        Construct an attributes object
        :param type_name: Name of the serializable object
        :param version: Version of the serializable object
        :param ns: Name space of the serializable object
        :param member_count: Count of the number of members in the serializable object
        :param known_types: The types that needs to be known to the serializable object.
        """
        self.type_name = type_name
        self.version = version
        self.ns = ns
        self.member_count = member_count
        if known_types is None:
            known_types = list()
        self.known_types = list(known_types)
