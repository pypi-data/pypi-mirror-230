# *************************************************************** #
#               Copyright © Hero Imaging AB 2022. 				  #
#  					  All Rights Reserved.						  #
# *************************************************************** #

from heropytools.Transport.client_handle import ClientHandle

class TransportConnection:

	_client: ClientHandle

	def __init__(self, userid, url):
		self._client = ClientHandle(userid, url)

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self._client._del()

	def client(self):
		return self._client