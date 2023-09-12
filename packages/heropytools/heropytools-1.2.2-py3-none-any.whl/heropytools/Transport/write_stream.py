# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

from ctypes.wintypes import BYTE
from heropytools.Transport.connection import TransportConnection

import ctypes

class WriteStream:

	def __init__(self, conn: TransportConnection, path: str, subpath: str = ""):
		self._connection = conn
		#self._path = path
		#self._subpath = subpath
		self._pwstream = (ctypes.c_void_p)()

		self._client = conn.client()
		self._dll = self._client.get_dll_handle()

		success = self._dll.CreateWriteStream(
			ctypes.byref(self._pwstream),
			path.encode(),
			subpath.encode())

		self._client.check_error(success, "Failed to create WriteStream : ")
	
	def __enter__(self):
		return self

	def write(self, data: bytes):
		bytes_arr = (ctypes.c_uint8 * len(data)).from_buffer(bytearray(data))

		success = self._dll.WriteWriteStream(
			self._pwstream,
			bytes_arr,
			len(data))

		self._client.check_error(success, "Failed to write to stream : ")

	def write_raw_string(self, string: str):
		arr = string.encode('UTF-8')
		
		success = self._dll.WriteWriteRawStringStream(
			self._pwstream,
			arr,
			len(arr))

		self._client.check_error(success, "Failed to write to stream : ")


		

	def close(self):
		success = self._dll.CloseWriteStream(
			self._pwstream)
		self._client.check_error(success, "Failed to close WriteStream : ")

	def __exit__(self, type, value, traceback):
		self.close()
		

class WriteStreamOld:

	def __init__(self, conn: TransportConnection, path: str, subpath: str = '', max_blobsize: int = 3*1024*1024):
		self._connection = conn
		self._path = path
		self._subpath = subpath
		self._closed = False
		self._exception_closed = False
		self._blob = bytearray()

		self._max_blobsize = max_blobsize

		try:
			self._connection.client().start_data_push(path, subpath)
		except Exception as e:
			self._exception_closed = True
			raise


	def __enter__(self):
		return self

	def write(self, data: bytearray):
		if self._closed:
			raise RuntimeError("Tried to write on closed stream")
		
		# Possible major performance drop
		while len(data) + len(self._blob) > self._max_blobsize:
			leftsize = self._max_blobsize - len(self._blob)
			self._blob += data[:leftsize]

			try:
				self._connection.client().push_data_blob(self._blob)
			except Exception as e:
				self._exception_closed = True
				raise

			data = data[leftsize:]

			self._blob = bytearray()
		
		self._blob += data
			

	def close(self):
		if self._exception_closed:
			return

		if self._closed:
			raise RuntimeError("Tried to close already closed WriteStreamt")

		if len(self._blob) > 0:
			try:
				self._connection.client().push_data_blob(self._blob)
			except Exception as e:
				self._exception_closed = True
				raise

		try:
			self._connection.client().end_data_push()
		except Exception as e:
			self._exception_closed = True
			raise
		self._closed = True

	def __exit__(self, type, value, traceback):
		self.close()


