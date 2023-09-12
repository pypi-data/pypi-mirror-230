from heropytools.Serialization.Serializer import Serializer
from heropytools.Serialization.BinaryReader import BinaryReader
from heropytools.Serialization.BinaryWriter import BinaryWriter
from heropytools.api.HeroCommunication import get_hero_types
from heropytools import HeroData, NodeIOType, HeroString, HeroStruct, HeroImage, HeroList, HeroArray, HeroTable, \
    HeroColumn, HeroContour
from heropytools.api.HeroCommunication import HeroCommunication
import gzip
import os
import numpy as np
import pandas as pd


def _get_type_string(data):
    """
    Get storage type string.
    :param data:
    :return:
    """
    if data is None:
        raise Exception("Cannot set the value 'None'.")
    if isinstance(data, HeroData):
        return type(data).__name__
    else:
        if type(data) in HeroCommunication.type_dict:
            return HeroCommunication.type_dict[type(data)]
        else:
            raise Exception(f"Cannot set data of type {type(data)}")


def _get_io_type(data) -> NodeIOType:
    if isinstance(data, str) or isinstance(data, HeroString):
        return NodeIOType.String
    elif isinstance(data, float) or isinstance(data, int):
        return NodeIOType.NumericArray
    elif isinstance(data, bool):
        return NodeIOType.BooleanArray
    elif isinstance(data, np.ndarray):
        if data.dtype == bool:
            return NodeIOType.BooleanArray
        else:
            return NodeIOType.NumericArray
    elif isinstance(data, HeroArray):
        if data.is_boolean:
            return NodeIOType.BooleanArray
        else:
            return NodeIOType.NumericArray
    elif isinstance(data, pd.DataFrame) or isinstance(data, HeroTable):
        return NodeIOType.Table
    elif isinstance(data, pd.Series) or isinstance(data, HeroColumn):
        return NodeIOType.Column
    elif isinstance(data, dict) or isinstance(data, HeroStruct):
        return NodeIOType.Struct
    elif isinstance(data, HeroContour):
        return NodeIOType.Contour
    elif isinstance(data, HeroImage):
        if data.Array.dtype == bool:
            return NodeIOType.Mask
        else:
            return NodeIOType.Image
    else:
        raise Exception(f"The data provided ({type(data).__name__}) is not supported by the hdata file format.")


def _get_list_io_type(data):
    element_io_type = _get_io_type(data[0])
    for e in data:
        if element_io_type != _get_io_type(e):
            raise Exception("A list in Hero cannot currently contain a mixture of types.")

    list_types = {NodeIOType.String: NodeIOType.StringList,
                  NodeIOType.NumericArray: NodeIOType.NumericArrayList,
                  NodeIOType.BooleanArray: NodeIOType.BooleanArrayList,
                  NodeIOType.Image: NodeIOType.ImageList,
                  NodeIOType.Mask: NodeIOType.MaskList,
                  NodeIOType.Column: NodeIOType.Column,
                  NodeIOType.Table: NodeIOType.TableList,
                  NodeIOType.Contour: NodeIOType.ContourList,
                  NodeIOType.Struct: NodeIOType.StructList}
    return list_types[element_io_type]


def _create_hdata_header(data, compress: bool, io_type: NodeIOType):
    """
    Create a header for the data.
    :param data:
    :param compress:
    :param io_type:
    :return:
    """
    if isinstance(data, list) or isinstance(data, HeroList):
        if len(data) == 0:
            if io_type is None:
                io_type = NodeIOType.ListOfLists
        else:
            if isinstance(data[0], list) or isinstance(data[0], HeroList):
                io_type = NodeIOType.ListOfLists
            else:
                io_type = _get_list_io_type(data)
    else:
        io_type = _get_io_type(data)

    display_names = {
        NodeIOType.String: "Text",
        NodeIOType.NumericArray: "Numeric Array",
        NodeIOType.BooleanArray: "Boolean Array",
        NodeIOType.Image: "Image",
        NodeIOType.Mask: "Mask",
        NodeIOType.Column: "Column",
        NodeIOType.Table: "Table",
        NodeIOType.Contour: "Countour",
        NodeIOType.Struct: "Structure",
        NodeIOType.StringList: "Text List",
        NodeIOType.NumericArrayList: "Numeric Array List",
        NodeIOType.BooleanArrayList: "Boolean Array List",
        NodeIOType.ImageList: "Image List",
        NodeIOType.MaskList: "Mask List",
        NodeIOType.ColumnList: "Column List",
        NodeIOType.TableList: "Table List",
        NodeIOType.ContourList: "Contour List",
        NodeIOType.StructList: "Structure List",
        NodeIOType.ListOfLists: "List of Lists"
    }

    return {"FileVersion": "1.0", "NodeIOTypeName": display_names[io_type], "TypeLabel": "", "Compress": compress}


def _get_filename(filename, compress):
    filename_base, file_extension = os.path.splitext(filename)
    if compress:
        if file_extension == '.gz':
            filename_base, file_extension = os.path.splitext(filename_base)
            if file_extension == '.hdata':
                return filename
            elif file_extension == ".hxdata":
                raise Exception("Saving as Xml format (.hxdata) is currently not supported in python.")
            else:
                return filename + ".hdata.gz"
        elif file_extension == '.hdata':
            return filename + ".gz"
        elif file_extension == ".hxdata":
            raise Exception("Saving as Xml format (.hxdata) is currently not supported in python.")
        else:
            return filename + ".hdata.gz"
    else:
        if file_extension == ".hdata":
            return filename
        elif file_extension == ".hxdata":
            raise Exception("Saving as Xml format (.hxdata) is currently not supported in python.")
        else:
            return filename + ".hdata"


def save(filename: str, data, compress: bool = False, io_type: NodeIOType = None):
    """
    Save to hdata format.
    :param filename: Full path to the file. If hdata or hdata.gz is missing this will be appended.
    :param data: Data to be saved.
    :param compress: If data is going to be compressed. Note if gz extension is missing this will be added when this
    flag is set.
    :param io_type: Specify the io_type manually. Can be useful for empty lists.
    :return:
    """

    # Get filename with proper file-ending
    filename = _get_filename(filename, compress)

    # Create serializer
    serializer = Serializer(get_hero_types())

    # Find storage type
    type_str = _get_type_string(data)

    # Create hdata header
    hdata_header = _create_hdata_header(data, compress, io_type)

    # Write the header and data (compressed if required).
    with open(filename, 'wb') as f:
        with BinaryWriter(f) as w:
            serializer.write_object(hdata_header, w, type_str="HeroStruct")

    if compress:
        with gzip.open(filename, 'ab') as zip_stream:
            with BinaryWriter(zip_stream) as w:
                serializer.write_object(data, w, type_str=type_str)
    else:
        with open(filename, 'ab') as f:
            with BinaryWriter(f) as w:
                serializer.write_object(data, w, type_str=type_str)


def load(filename: str):
    """
    Load hdata/hdata.gz format.
    :param filename: Full path to the file. Including the extension.
    :return:
    """

    # Create serializer
    serializer = Serializer(get_hero_types())

    # Read header
    with open(filename, 'rb') as f:
        with BinaryReader(f) as r:
            header = serializer.read_object(r)

        # Check version -- Current: 1.0'
        current_version = "1.0"
        if header["FileVersion"] != current_version:
            raise Exception(f"Could not load the data. Saved version: {header['FileVersion']} is not supported.")

        # Read data
        if header["Compress"]:
            with gzip.open(f) as zip_stream:
                with BinaryReader(zip_stream) as r:
                    data = serializer.read_object(r)
        else:
            with BinaryReader(f) as r:
                data = serializer.read_object(r)

        return data





