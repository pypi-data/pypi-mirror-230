# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

from heropytools.Transport.connection import TransportConnection
from heropytools.Serialization.Serializer import Serializer
from heropytools.Serialization.BinaryReader import BinaryReader
from heropytools.Serialization.BinaryWriter import BinaryWriter
from heropytools.Transport.read_stream import ReadStream
from heropytools.Transport.write_stream import WriteStream

from heropytools import HeroData, HeroDataType
from heropytools import InputList, OutputList, InputDescription, OutputDescription, NodeIOType
from heropytools.HeroData import FunctionSpecification

import numpy as np
import pandas as pd
import sys
import inspect
from typing import List
from collections import namedtuple


def get_hero_types() -> List[type]:
    """Get all types that should be possible to serialize."""
    types = list()
    for name, obj in inspect.getmembers(sys.modules["heropytools.HeroData"]):
        if inspect.isclass(obj):
            types.append(obj)
    return types


class HeroCommunication:
    """
    Communicates with Hero. Use this class to get settings, input data and node status.
    Also use this class to set outputs, progress and perform logging.
    """
    type_dict: dict = {str: "HeroString", np.ndarray: "HeroArray", pd.DataFrame: "HeroTable",
                       pd.Series: "HeroColumn", float: "HeroArray", int: "HeroArray", bool: "HeroArray",
                       complex: "HeroArray", dict: "HeroStruct", list: "HeroList"}

    def __init__(self, connection: TransportConnection):
        """
        Create a communication object that can communicate with Hero
        :param connection: The connection used for communication.
        """
        self._connection = connection

        # Initialize a serializer.
        self._serializer = Serializer(get_hero_types())

    def get_specification(self) -> FunctionSpecification:
        """
        Get the specification of the node.
        :return: The specification.
        """
        specification = self._get_data("$SPECIFICATION$")
        return specification

    def get_simple_specification(self) -> dict:
        """
        Get a simplified specification of the node.
        :return: The specification.
        """
        simple_specification = self._get_data("$SIMPLE_SPECIFICATION$")
        return self._interpret_simple_specification(simple_specification)

    def get_input(self, path: str, sub_path: str):
        """
        Get input data to the node from Hero
        :param path: The name of the input
        :param sub_path: Further path into some element in the input object.
        :return: The deserialized object from Hero.
        """
        return self._get_data(f"$INPUTS${path}", sub_path)

    def set_output(self, data, path: str, sub_path: str):
        """
        Set output data to the node in Hero
        :param data: The data to set
        :param path: The name of the output
        :param sub_path: Further path into some element in the output object.
        :return: nothing
        """
        if data is None:
            raise Exception("Cannot set the value 'None'.")
        if isinstance(data, HeroData):
            return self._set_data(data, f"$OUTPUTS${path}", sub_path)
        else:
            if type(data) in HeroCommunication.type_dict:
                type_str = HeroCommunication.type_dict[type(data)]
                return self._set_data(data, f"$OUTPUTS${path}", sub_path, type_str)
            else:
                raise Exception(f"Cannot set data of type {type(data)}")

    def set_progress(self, progress: float):
        """
        Reports back progress to hero
        :param progress: The progress in %.
        :return: nothing
        """
        return self._set_data(progress, f"$PROGRESS$", type_str="HeroArray")

    def log(self, message: str):
        """
        Report back to the Hero node log
        :param message: The log message.
        :return: nothing
        """
        return self._set_data(message, f"$LOG$", "HeroString")

    def is_aborted(self) -> bool:
        """
        Check if the node should abort.
        :return: True if one should abort.
        """
        return bool(self._get_data(f"$ABORTING$"))

    def set_failed(self, failed: bool = True, msg: str = ""):
        """
        Tell back to Hero that the node that has failed
        :param failed: True if the node failed
        :param msg: Error message.
        :return: nothing
        """
        return self._set_data({'Failed': failed, 'Message': msg}, f"$FAILED$", type_str="HeroStruct")

    def get_input_connections_info(self) -> dict:
        """
        Get information about how the node is connected and how the inputs and outputs are defined.
        :return: (dict of IO definitions, dict of node connections)
        """
        info = self._get_data(f"$INPUT_CONNECTIONS$")
        connection_info = dict()
        for e in info:
            name = e[0]
            connection_info[name] = HeroCommunication._decode_frontend_types(e[1])

        return connection_info

    # -------------------------------------------------- #
    #           Private helper methods below.
    # -------------------------------------------------- #

    def _get_data(self, base_path: str, sub_path: str = None):
        """
        Ask for data from Hero
        :param base_path: Name and category of the item
        :param sub_path: Further sub path to an element in the item.
        :return: The item asked for.
        """
        if sub_path is None:
            sub_path = ""
        with ReadStream(self._connection, base_path, sub_path) as stream:
            with BinaryReader(stream) as reader:
                obj = self._serializer.read_object(reader)
                return obj

    def _set_data(self, data, base_path, sub_path=None, type_str=None):
        """
        Set data for the node in Hero
        :param data: The value you set
        :param base_path: Name and category of the item to set
        :param sub_path: Further sub path to some element inside the item to set. Use Hero path syntax for this
        :param type_str: The type of the data. Needed since there might be more than one interpretation of the data in
        terms of Hero serializable types.
        :return: nothing
        """
        if sub_path is None:
            sub_path = ""
        with WriteStream(self._connection, base_path, sub_path) as stream:
            with BinaryWriter(stream) as writer:
                if type_str is None:
                    self._serializer.write_object(data, writer)
                else:
                    self._serializer.write_object(data, writer, type_str=type_str)

    @staticmethod
    def _decode_frontend_types(codes: List[int]):
        types = list()
        for code in codes:
            types.append(HeroDataType(code))
        return types

    @staticmethod
    def _interpret_simple_specification(simple_specification) -> dict:
        return {'inputs': HeroCommunication._interpret_simple_inputs(simple_specification["Inputs"]),
                'outputs': HeroCommunication._interpret_simple_outputs(simple_specification["Outputs"]),
                'settings': HeroCommunication._interpret_group(simple_specification["Settings"])}

    _io_name_to_enum = {'Text': NodeIOType.String, 'Numeric Array': NodeIOType.NumericArray, 
                        'Boolean Array': NodeIOType.BooleanArray, 'Image': NodeIOType.Image,
                        'Mask': NodeIOType.Mask, 'Structure': NodeIOType.Struct, 'Table': NodeIOType.Table,
                        'Column': NodeIOType.Column, 'Contour': NodeIOType.Contour,
                        'Image List': NodeIOType.ImageList, 'Text List': NodeIOType.StringList,
                        'Mask List': NodeIOType.MaskList, 'Structure List': NodeIOType.StructList,
                        'List of Lists':NodeIOType.ListOfLists, 'Table List': NodeIOType.TableList,
                        'Column List': NodeIOType.ColumnList, 'Numeric Array List': NodeIOType.NumericArrayList,
                        'Boolean Array List': NodeIOType.BooleanArrayList, 'Contour List': NodeIOType.ContourList}
        
    @staticmethod
    def _interpret_simple_inputs(inputs):
        result = InputList()
        for input in inputs:
            name = input['Name']
            input_types = [HeroCommunication._io_name_to_enum[type_name] for type_name in input['InputTypes']]
            value = InputDescription(input_types=input_types, soft_type=input['TypeLabel'], id_value=input['ID'])
            result[name] = value
        return result

    @staticmethod
    def _interpret_simple_outputs(outputs):
        result = OutputList()
        for output in outputs:
            name = output['Name']
            output_type = HeroCommunication._io_name_to_enum[output['OutputType']]
            value = OutputDescription(output_type=output_type, soft_type=output['TypeLabel'], id_value=output['ID'])
            result[name] = value
        return result

    @staticmethod
    def _interpret_group(settings):
        group = dict()
        for item in settings:
            value = item['Settings']
            name = item['Name']
            if isinstance(value, list):
                group[name] = HeroCommunication._interpret_group(value)
            elif isinstance(value, dict):
                group[name] = HeroCommunication._interpret_value(value)
            else:
                AssertionError("Settings on an unexpected format was detected.")

        return group

    @staticmethod
    def _interpret_value(item):
        if len(item) == 1:
            # Simple value
            ValueSetting = namedtuple("ValueSetting", "value")
            return ValueSetting(value=item['Value'])
        if len(item) == 2:
            SelectionSetting = namedtuple("SelectionSetting", "value values")
            return SelectionSetting(value=item['Value'], values=item['Values'])


class NodeInputs:
    """
    Communicates with Hero inputs for specific node.
    """

    def __init__(self, hero_communication: HeroCommunication, input_specification: InputList, input_connections: dict):
        self._hero_communication = hero_communication
        self._specification = input_specification
        self._connections = input_connections

    def __getitem__(self, key):
        """
        Get node input data from Hero
        :param key: Can be 1 to 3 arguments.
        - 1 argument: A string specifying the name of the input.
        - 2 arguments: The name of the input, the index(es) of the elements in the input list (int or str). Note that
        the string uses Hero type indexing not python syntax.
        - 3 arguments:  The name of the input, the index(es) of the elements in the input list (int or str),
        sub path of an element in the input as a string.
        :return:
        """
        if isinstance(key, tuple):
            if 1 < len(key) <= 3:
                path = key[0]
                index = key[1]
                sub_path = f"[{index}]"
                if len(key) == 3:
                    sub_path += f".{key[2]}"
                return self._hero_communication.get_input(path, sub_path)
                    
        elif isinstance(key, str):
            return self._hero_communication.get_input(key, "")
        else:
            raise IndexError(f"zero to three arguments are needed: ")

    def input_names(self):
        return [name for name in self._specification.keys()]

    @property
    def specification(self):
        return self._specification

    @specification.setter
    def specification(self, value):
        raise Exception("The specification cannot be set.")

    @specification.deleter
    def specification(self):
        raise AttributeError("The specification is not deletable.")

    @property
    def connections(self):
        return self._connections

    @connections.setter
    def connections(self, value):
        raise Exception("The connections cannot be set.")

    @connections.deleter
    def connections(self):
        raise AttributeError("The connections is not deletable.")


class NodeOutputs:
    """
    Communicates with Hero outputs for specific node.
    """

    def __init__(self, hero_communication: HeroCommunication, output_specification: OutputList):
        self._hero_communication = hero_communication
        self._specification = output_specification

    def __setitem__(self, key, value):
        """
        Set node output data in Hero
        :param key: Can be 1 or 2 arguments.
        - 1 argument: A string specifying the name of the input.
        - 2 arguments: The name of the input, sub path (as a string) of an element in the output
        :param value: The value that is set.
        :return: nothing
        """
        if isinstance(key, tuple):
            if len(key) == 2:
                path = key[0]
                sub_path = key[1]
            else:
                raise IndexError(f"One or two arguments are needed for the indexing.")
        else:
            path = key
            sub_path = ""

        return self._hero_communication.set_output(value, path, sub_path)

    def output_names(self):
        return [name for name in self._specification.keys()]

    @property
    def specification(self):
        return self._specification

    @specification.setter
    def specification(self, value):
        raise Exception("The specification cannot be set.")

    @specification.deleter
    def specification(self):
        raise AttributeError("The specification is not deletable.")


class NodeStatus:
    """
    Communicates with Hero status for specific node. Can report progress and access abort status.
    """

    def __init__(self, hero_communication: HeroCommunication):
        self._hero_communication = hero_communication

    def set_progress(self, progress: float):
        """
        Set the progress in %.
        :param progress: The progress value in %.
        :return: Nothing
        """
        self._hero_communication.set_progress(progress)

    def is_aborted(self):
        """
        Get if the user has pressed abort in Hero.
        :return: True if aborted.
        """
        return self._hero_communication.is_aborted()
