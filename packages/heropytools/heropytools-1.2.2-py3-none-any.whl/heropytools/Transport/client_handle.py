# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

import ctypes
from enum import Enum
from sre_constants import SUCCESS
from typing import Tuple
import pathlib

from numpy import byte

class GrpcLibCode(Enum):
	GRPC_LIB_SUCCESS = 0
	GRPC_LIB_ERROR = 1


class ClientHandle:

	def __init__(self, userid: str, channelUrl: str, max_push_blobs: int = 8, max_request_blobs: int = 8, sleep_micros: int = 20):

		self._pClientHandle = (ctypes.c_void_p)()
		self._bytes = ctypes.POINTER(ctypes.c_uint8)()
		self._bytesSize = (ctypes.c_uint32)()
		#self._grpclib = ctypes.CDLL(r"C:\Users\ander\Documents\GitHub\mice\software\PluginSupport\x64\Release\HeroTransportLib.dll") # change to be relative to pypy package
		dll_file = f"{pathlib.Path(__file__).parent}\\HeroTransportLib.dll"
		self._grpclib = ctypes.CDLL(dll_file)
		self._hasBeendFreed = False

		self.userid = userid
		self.channelUrl = channelUrl

		success = self._grpclib.CreateClientHandleExtra(
			ctypes.byref(self._pClientHandle),
			userid.encode(),
			channelUrl.encode(),
			ctypes.c_uint32(max_push_blobs),
			ctypes.c_uint32(max_request_blobs),
			ctypes.c_uint32(sleep_micros))

		self.check_error(success, "Failed to create grpc client handle : ")
	
	def _del(self):
		success = self._grpclib.FreeClientHandle(self._pClientHandle)

		self.check_error(success, "Failed to free grpc client handle : ")

		self._hasBeendFreed = True

	def __del__(self):
		if not self._hasBeendFreed:
			self._del()
	
	# ERROR CHECKING

	def check_error(self, success, msg):
		if success != GrpcLibCode.GRPC_LIB_SUCCESS.value:
			error_msg = (ctypes.c_char_p)()
			success2 = self._grpclib.GetLastErrorMsg(ctypes.byref(error_msg))
			if success2 != GrpcLibCode.GRPC_LIB_SUCCESS.value:
				raise RuntimeError("Couldn't fetch last error : ")
			raise RuntimeError(msg + error_msg.value.decode("ascii"))

	# GET GRPCLIB DLL HANDLE
	def get_dll_handle(self):
		return self._grpclib

	# REQUEST

	def start_data_request(self, path: str, subpath: str = ''):
		success = self._grpclib.StartDataRequest(
			self._pClientHandle,
			path.encode(),
			subpath.encode())

		self.check_error(success, "Failed to start data request : ")

	def get_data_blob(self) -> Tuple[bytearray, bool]:

		success = self._grpclib.GetDataBlob(
			self._pClientHandle,
			ctypes.byref(self._bytes),
			ctypes.byref(self._bytesSize))

		self.check_error(success, "Failed to get data blob : ")

		if not bool(self._bytes) and self._bytesSize.value == 0:
			return (None, True)

		bytes_copy = ctypes.cast(self._bytes, ctypes.POINTER(ctypes.c_char * self._bytesSize.value))[0].raw
		
		return (bytes_copy, False)

	def end_data_request(self):
		success = self._grpclib.EndDataRequest(self._pClientHandle)

		self.check_error(success, "Failed to end data request : ")

	# PUSH

	def start_data_push(self, path: str, subpath: str = ''):

		success = self._grpclib.StartDataPush(
			self._pClientHandle,
			path.encode(),
			subpath.encode())

		self.check_error(success, "Failed to start data push : ")

	def push_data_blob(self, blob: bytearray):

		bytes_arr = (ctypes.c_uint8 * len(blob)).from_buffer(blob)

		success = self._grpclib.PushDataBlob(
			self._pClientHandle,
			bytes_arr,
			len(blob))

		self.check_error(success, "Failed to push blob : ")

	def end_data_push(self):

		success = self._grpclib.EndDataPush(self._pClientHandle)

		self.check_error(success, "Failed to end data push : ")


	# ABORT

	def abort(self):

		success = self._grpclib.Abort(self._pClientHandle)

		self.check_error(success, "Failed to Abort : ")






