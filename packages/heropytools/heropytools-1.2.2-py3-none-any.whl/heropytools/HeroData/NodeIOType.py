from enum import Enum


class NodeIOType(Enum):
    String = 1
    NumericArray = 2
    BooleanArray = 3
    Image = 4
    Mask = 5
    Column = 6
    Table = 7
    Contour = 8
    Struct = 9
    StringList = 10
    NumericArrayList = 11
    BooleanArrayList = 12
    ImageList = 13
    MaskList = 14
    ColumnList = 15
    TableList = 16
    ContourList = 17
    StructList = 18
    ListOfLists = 19


