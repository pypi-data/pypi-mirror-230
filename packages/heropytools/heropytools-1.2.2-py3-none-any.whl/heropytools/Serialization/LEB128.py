# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

class LEB128(object):
    """
    Convenient class for converting variable length integers to fix length byte array corresponding to
    1,2,4, etc. byte integers .
    Provides LEB128 type conversion for integers.
    https://en.wikipedia.org/wiki/LEB128
    """

    @staticmethod
    def encode(integer: int) -> bytearray:
        """
        Encode the integer using unsigned leb128 and return the encoded bytearray
        :param integer: The integer to encode.
        :return:
        """
        if integer < 0:
            raise Exception("Can only encode unsigned integers.")
        if integer < 0x80:
            return bytearray([integer])
        arr = []
        while True:
            byte = integer & 0x7f
            integer = integer >> 7
            if integer == 0:
                arr.append(byte)
                return bytearray(arr)
            arr.append(0x80 | byte)

    @staticmethod
    def decode(data_bytes: bytearray) -> int:
        """
        Decode the unsigned leb128 encoded bytearray to an integer
        :param data_bytes: The bytes to decode.
        :return:
        """
        val = 0
        for i, byte in enumerate(data_bytes):
            masked_byte = byte & 0x7f
            bit_position = i * 7
            val += masked_byte << bit_position
        return val

    @staticmethod
    def decode_steam(stream, max_len=8) -> int:
        """
        Decode the unsigned leb128 encoded int from a steam from which bytes can be read with the method read(n).
        :param stream: The stream. Must support read(n)
        :param max_len: The maximum length to read.
        :return:
        """
        array = stream.read(1)

        # Faster for low values.
        if (array[0] & 0x80) == 0:
            return int(array[0])

        for _ in range(max_len-1):
            read_bytes = stream.read(1)
            array.extend(read_bytes)
            if (read_bytes[0] & 0x80) == 0:
                return LEB128.decode(array)
        
        raise Exception("Failed to decode LEB128 integer.")
        


