# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

class Header:
    """
    Represents the header used when reading and writing data elements in the serialization.
    """

    # Constants for the 3 top level formats of data that can be serialized.
    COMPOSITE = 1
    ARRAY = 2
    ATOMIC = 3

    def __init__(self, storage_format: int, type_name: str = None, name: str = "", version: int = 0, ns: str = None,
                 content_size: int = 1, is_null: bool = False):
        """
        Create a header object
        :param storage_format: The top level format for data that can be stored. Can be 1, 2 or 3. See above
        :param type_name: Name of the type
        :param name: Name of the element this is a header for
        :param version: Version of the element this is a header for
        :param ns: Namespace of the name of the element this is a header for
        :param content_size: If a composite or array type of element. The number of members.
        :param is_null: If the element is null.
        """
        self.name = name
        self.version = version
        self.type_name = type_name
        self.name_space = ns
        self.content_size = content_size
        self.storage_format = storage_format
        self.is_null = is_null
