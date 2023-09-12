# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

from heropytools.Transport.connection import TransportConnection
from collections import deque


class ReadStream:

	def __init__(self, conn: TransportConnection, path: str, subpath: str = ""):
		self._connection = conn
		self._path = path
		self._subpath = subpath
		self._blob = bytearray()
		self._closed = False
		self._exception_closed = False

		self._lastFetched = False
		try:
			self._connection.client().start_data_request(path, subpath)
		except Exception as e:
			self._exception_closed = True
			raise

	def __enter__(self):
		return self

	def read(self, n: int):
		if self._closed:
			raise RuntimeError("Tried to read on closed stream")

		while n >= len(self._blob):
			if self._lastFetched:
				if n != len(self._blob):
					raise RuntimeError("Tried to read more than available")
				else:
					break
			try:
				blob_tup = self._connection.client().get_data_blob()
			except Exception as e:
				self._exception_closed = True
				raise

			if blob_tup[0] is None and blob_tup[1]:
				self._lastFetched = True
			else:
				self._blob += blob_tup[0]

		return self._pop_first_n(n)
	
	def _pop_first_n(self, n: int):
		ret = self._blob[:n]
		del self._blob[:n]
		return ret

	def close(self):
		if self._exception_closed:
			return

		if self._closed:
			raise RuntimeError("Tried to close already closed WriteStream")

		if len(self._blob) > 0:
			raise RuntimeError("Didn't read entire stream")
		self._connection.client().end_data_request()
		self._closed = True

	def __exit__(self, type, value, traceback):
		self.close()
