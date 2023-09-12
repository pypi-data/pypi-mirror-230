# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

from .Writer import Writer
from .Header import Header
from .KnownTypes import KnownTypes
from .CustomSerializer import CustomSerializer
from .Reader import Reader


class Serializer:
    """
    Serialization / Deserialization class for data between Hero and Python.
    """

    @property
    def version(self):
        return '1.0'

    @version.setter
    def version(self, value):
        raise ValueError("Attribute 'version' is not setable.")

    @version.deleter
    def version(self):
        raise AttributeError("Attribute 'version' is not deletable.")

    def __init__(self, known_types: list[type]):
        """
        Create a serializer that can serialize / deserialize the types given in the known_types list
        :param known_types: The types that can be serialized / deserialized.
        """
        # Set up the known type mappers.
        self._known_types = KnownTypes(known_types)

        # Setup set for keeping track of cycles
        self._cycle_detector_set = set()

    def write_object(self, obj, writer: Writer, name: str = "Root", type_str: str = None):
        """
        Serialize an object
        :param obj: The object to be serialized
        :param writer: The writer to be used in the serialization
        :param name: The name of the object when stored
        :param type_str: String defining the type
        :return: nothing
        """

        writer.write_serializer_header(name, self.version)
        if type_str is None:
            type_str = type(obj).__name__
        self._write_object(obj, type_str, writer, name)
        writer.write_footer()

    def read_object(self, reader: Reader):
        """
        Deserialize an object
        :param reader: The reader used.
        :return:
        """
        if reader is None:
            raise Exception("A reader must be provided.")
        _, v = reader.read_serializer_header()
        if v != self.version:
            raise ValueError(f"The version of the serializer 'v{version}' does not match the version of the "
                             + f"serializer 'v{v}' used for serializing the data.")
        h = reader.read_header(self._known_types.get_type_from_alias)
        obj = self._read_object(h, h.type_name, reader)
        reader.read_footer()
        reader.read_footer()
        return obj

    # -------------------------------------------------- #
    #           Private helper methods below.
    # -------------------------------------------------- #

    def _write_object(self, obj, prescribed_type_str: str, writer: Writer, name: str, custom: CustomSerializer = None):
        """
        Write an object
        :param obj: The object to be written
        :param prescribed_type_str: The name of the type of the object
        :param writer: The writer used
        :param name: The name of the written object
        :param custom: A custom serializer will be used if specified.
        :return: nothing
        """

        # If None is provided as data it will be stored as a null value.
        if obj is None:
            self._write_null_object(name, prescribed_type_str, writer)
            return

        # Use the custom serializer if provided.
        if custom is not None:
            self._write_custom_object(obj, name, writer, custom)
            return

        # Find out information about the type to be stored.
        type_str, storage_format, obj = self._resolve_type(prescribed_type_str, obj, writer)

        # If a composite object. I.e. a class that is serializable.
        if storage_format == Header.COMPOSITE:
            self._write_composite_object(obj, name, type_str, writer)

        # If an atomic object. Basically the object that are serializable even when not specified in the construction
        # of the Serializer. E.g. Float, Double, Int, Byte[] etc.
        elif storage_format == Header.ATOMIC:
            self._write_basic_object(obj, name, type_str, writer)

        # If the object is an array.
        elif storage_format == Header.ARRAY:
            self._write_collection(obj, name, type_str, writer)

        # No matching serialization. Throw and exception. Should never happen.
        else:
            raise Exception("Serialization failed.")

    def _read_object(self, h: Header, type_str: str, reader: Reader, custom: CustomSerializer = None):
        """
        Read a serializable object
        :param h: The header information about the object to be read
        :param type_str: The of object
        :param reader: The reader used
        :param custom: If a custom serializer is used
        :return:
        """

        # Nothing to do if the object is null.
        if h.is_null:
            return None

        # Use custom serializer if provided.
        if custom is not None:
            return self._read_custom_object(reader, custom)

        # Read an atomic object. E.i one that doesn't need to be specified when creating the serializer. E.g.
        # Float, Double, Int etc. Can also be arrays and lists of atomic objects.
        if h.storage_format == Header.ATOMIC:
            if type_str[-2:] == '{}':
                return [reader.read(type_str[:-2], h.content_size) for i in range(h.content_size)]
            else:
                return reader.read(type_str, h.content_size)

        # Read an array of data.
        if h.storage_format == Header.ARRAY:
            n = h.content_size
            element_type_str = type_str[:-2]
            return self._read_array(element_type_str, n, reader)

        # Read a composite object. I.e. a class that is serializable.
        if h.storage_format == Header.COMPOSITE:
            return self._read_composite(h, reader)
        else:
            raise Exception("Deserialization failed.")

    def _read_custom_object(self, reader: Reader, custom: CustomSerializer):
        """
        Read an object using a custom Serializer class
        :param reader: The reader used
        :param custom: The custom serializer class.
        :return: The read object.
        """

        # Creates a lambda based of the provided reader.
        def reader_fun(type_str: str):
            mh = reader.read_header(self._known_types.get_type_from_alias)
            if mh.storage_format == Header.COMPOSITE:
                type_str = mh.type_name
            obj = self._read_object(mh, type_str, reader)
            reader.read_footer()
            return obj, type_str

        # Call the custom read function.
        return custom.read(reader_fun)

    def _read_array(self, element_type_str: str, n: int, reader: Reader):
        """
        Read an array
        :param element_type_str: The name of the type of elements
        :param n: The number of elements to read
        :param reader: The reader used
        :return: The read object.
        """
        arr = list()
        for i in range(n):
            lh = reader.read_header(self._known_types.get_type_from_alias)
            element = self._read_object(lh, element_type_str, reader)
            reader.read_footer()
            arr.append(element)
        return arr

    def _read_composite(self, h: Header, reader: Reader):
        """
        Read a serializable class
        :param h: The header of the object
        :param reader: The reader used.
        :return: The read object
        """

        # Find out the class type
        cl = self._known_types.get_class(h.type_name)

        # Create a reader function
        def reader_fun(type_name: str, custom: CustomSerializer):
            mh = reader.read_header(self._known_types.get_type_from_alias)
            # Type name must be taken from the header if not atomic type.
            if mh.storage_format == Header.COMPOSITE:
                type_name = mh.type_name
            obj = self._read_object(mh, type_name, reader, custom)
            reader.read_footer()
            return obj, mh.name

        # Ask the class to construct itself from a dict of data.
        return cl.create_from_dict(cl.deserialize(reader_fun))

    def _write_null_object(self, name: str, type_str: str, writer: Writer):
        """
        Writes an object that is null (None)
        :param name: The name of the object
        :param type_str: The name of the type
        :param writer: The writer to use
        :return: nothing
        """

        h = self._get_header_from_type_str(name, type_str)

        # Only header and footer are needed. Since there is no data.
        writer.write_header(h)
        writer.write_footer()

    def _write_custom_object(self, obj, name: str, writer: Writer, custom: CustomSerializer):
        """
        Write an object using a custom serializer
        :param obj: The object to be written
        :param name: The name of the object
        :param writer: The writer to be used
        :param custom: The custom serializer.
        :return: nothing
        """
        header = Header(Header.COMPOSITE, name=name)

        # Prevent cycles
        obj_id = id(obj)
        self._push_to_cycle_detector(obj_id)

        # Write header
        writer.write_header(header)

        # Write the content of the object.
        def writer_function(x, t_str: str, n: str, c: CustomSerializer):
            self._write_object(x, t_str, writer, n, c)
        custom.write(obj, writer_fun=writer_function)

        # write footer
        writer.write_footer()

        # Prevent cycles cleanup.
        self._pop_from_cycle_detector(obj_id)

    def _write_composite_object(self, obj, name: str, type_str: str, writer: Writer):
        """
        Write a composite object. I.e. a serializable class
        :param obj: The object to be serialized
        :param name: The name of the object
        :param type_str: The name of the type of the object
        :param writer: The writer to use.
        :return: nothing
        """
        type_info = self._known_types.get_type_info(type_str)
        header = Header(Header.COMPOSITE, type_name=type_info.type_name, name=name,
                        version=type_info.version, ns=type_info.ns, content_size=type_info.member_count,
                        is_null=False)

        # Prevent cycles
        obj_id = obj.get_container_id()
        if obj_id is not None:
            self._push_to_cycle_detector(obj_id)

        # Write header
        writer.write_header(header)

        # Write the content of the composite object.
        def writer_function(x, t_str: str, n: str, custom: CustomSerializer):
            self._write_object(x, t_str, writer, n, custom)

        obj.serialize(writer_function)

        # write footer
        writer.write_footer()

        # Prevent cycles cleanup.
        if obj_id is not None:
            self._pop_from_cycle_detector(obj_id)

    @staticmethod
    def _write_basic_object(obj, name: str, type_str: str, writer: Writer):
        """
        Write a basic object such as Int, float etc.
        :param obj: The object to write
        :param name: The name of the object
        :param type_str: The name of the type
        :param writer: The writer to use.
        :return: nothing
        """
        content_size = writer.get_size(obj, type_str)
        header = Header(Header.ATOMIC, None, name, content_size=content_size)
        writer.write_header(header)
        writer.write(obj, type_str)
        writer.write_footer()

    def _write_collection(self, obj, name: str, type_str: str, writer: Writer):
        """
        Write a collection of objects
        :param obj: The object to be written (list or tuple)
        :param name: The name of the list
        :param type_str: The type of the list
        :param writer: The writer to use.
        :return: nothing
        """
        # Check that the collection is a list or tuple.
        if not isinstance(obj, list) or isinstance(obj, tuple):
            raise Exception("Collections must be lists or tuples.")

        element_type_str = type_str[:-2]

        content_size = len(obj)

        header = Header(Header.ARRAY, name=name, content_size=content_size, is_null=False)

        # Check for cycles.
        self._push_to_cycle_detector(id(obj))

        # Write header
        writer.write_header(header)

        # Write each element in the collection.
        for element in obj:
            self._write_object(element, element_type_str, writer, "I")

        # Write the footer.
        writer.write_footer()

        # Clean up cycle detection
        self._pop_from_cycle_detector(id(obj))

    @staticmethod
    def _is_collection(type_str: str) -> bool:
        """
        Check if the name of a type is collection (array/list) of data
        :param type_str: The name of the type.
        :return: True if collection.
        """
        return '[]' in type_str or '{}' in type_str

    def _get_header_from_type_str(self, name: str, type_str: str) -> Header:
        """
        Used to get a header for types that are only known by their names. I.e. null objects.
        :param name: The name of the object
        :param type_str: The name of the type.
        :return: A Header.
        """
        if self._known_types.is_known(type_str):
            (type_name, ns, version) = self._known_types.get_type_info(type_str)
            header = Header(Header.COMPOSITE, type_name=type_name, name=name, version=version, ns=ns, content_size=1,
                            is_null=True)
        elif self._is_collection(type_str):
            header = Header(Header.ARRAY, name=name)
        else:
            header = Header(Header.ATOMIC, name=name)
        return header

    def _resolve_type(self, prescribed_type_str: str, obj, writer: Writer):
        """
        Resolve the type based on either the type or the name of the type
        :param prescribed_type_str: The name of the type
        :param obj: An object
        :param writer: The writer to be used.
        :return: Tuple[name of type, type code, the object]
        """
        if writer.can_write(prescribed_type_str):
            return prescribed_type_str, Header.ATOMIC, obj

        # The type of obj is complicated. It may be the prescribed type but also a subclass of the prescribed type.
        # Or it may be a built-in type that acts as the prescribed type. If a built-in type acts as a prescribed type
        # the prescribed type must be created.
        if self._known_types.is_known(prescribed_type_str):
            if self._known_types.is_known(type(obj).__name__):
                return obj._type_str, Header.COMPOSITE, obj # noqa
            else:
                obj = self._known_types.get_class(prescribed_type_str).create(obj)
                return obj._type_str, Header.COMPOSITE, obj # noqa

        if self._is_collection(prescribed_type_str):
            return prescribed_type_str, Header.ARRAY, obj

        raise Exception(f"Failed to resolve type: {prescribed_type_str}")

    def _push_to_cycle_detector(self, obj_id: int):
        """
        Add the id of an object to a dict that keep track of if it has been added before. If so, then there is
        a cycle in the data that is serialized. That is an error
        :param obj_id: The id of the object
        :return: nothing
        """
        if obj_id in self._cycle_detector_set:
            raise Exception("Failed to serialize. A cycle was detected in the data.")
        else:
            self._cycle_detector_set.add(obj_id)

    def _pop_from_cycle_detector(self, obj_id: int):
        """
        Remove an id from a dict if not needed anymore
        :param obj_id: The id.
        :return: nothing
        """
        self._cycle_detector_set.remove(obj_id)
