from .NodeIOType import NodeIOType


class NodeIOUtils:
    _enum2name = {1: "Text", 2: "Numeric Array", 3: "Boolean Array", 4: "Image",
                  5: "Mask", 6: "Column", 7: "Table", 8: "Contours",
                  9: "Struct", 10: "Text List", 11: "Numeric Array List",
                  12: "Boolean Array List", 13: "Image List", 14: "Mask List",
                  15: "Column List", 16: "Table List", 17: "Contour List",
                  18: "Struct List", 19: "List of Lists"}

    _name2enum = {"Text": NodeIOType.String, "Numeric Array": NodeIOType.NumericArray,
                  "Boolean Array": NodeIOType.BooleanArray, "Image": NodeIOType.Image,
                  "Mask": NodeIOType.Mask, "Column": NodeIOType.Column,
                  "Table": NodeIOType.Table, "Contour": NodeIOType.Contour,
                  "Struct": NodeIOType.Struct, "Text List": NodeIOType.StringList,
                  "Numeric Array List": NodeIOType.NumericArrayList,
                  "Boolean Array List": NodeIOType.BooleanArrayList,
                  "Image List": NodeIOType.ImageList, "Mask List": NodeIOType.MaskList,
                  "Column List": NodeIOType.ColumnList,
                  "Table List": NodeIOType.TableList,
                  "Contour List": NodeIOType.ContourList,
                  "Struct List": NodeIOType.StructList,
                  "List of Lists": NodeIOType.ListOfLists}

    @staticmethod
    def name2enum(name: str):
        return NodeIOUtils._name2enum[name]

    @staticmethod
    def enum2name(t: NodeIOType):
        return NodeIOUtils._enum2name[t.value]

