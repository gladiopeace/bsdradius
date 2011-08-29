"""Higher level Radius client implementation.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_7/bsdradius/RadClient.py $
# Author:		$Author: valts $
# File version:	$Revision: 333 $
# Last changes:	$Date: 2007-08-17 02:38:15 +0300 (Pk, 17 Aug 2007) $


import random, socket
import bsdradius.pyrad.packet as packet
from bsdradius.pyrad.dictionary import Dictionary
from bsdradius.pyrad.client import Client, Timeout


class RadClientError(Exception):
	pass


class RadClient(object):
	"""Describes interface to RADIUS server. Don't mix this with
		pyrad.client.Client. RadClient encapsulates pyrad's Client and makes it
		easier to send and receive radius packets,
	"""
	hexSymbols = '0123456789abcdef'

	def __init__(self, dictFile = "./dictionary", host = '127.0.0.1',
		authport = 1812, acctport = 1813, secret = 'testing123',
		retries = 3, timeout = 5):
		"""Create new radius client instance.
			Input: (str) path to radius dictionary file;
				(str) radius server address;
				(int) radius server authorization message port;
				(int) radius server accounting message port;
				(str) secret password known by radius server and client only;
				(int) packet send retries
				(int) packet send timeout
		"""
		self.dictFile = dictFile
		self.host = host
		self.authport = authport
		self.acctport = acctport
		self.secret = secret
		
		# parse dictionaries and create radius server descriptor instance
		self.dict = Dictionary(dictFile)
		self.srv = Client(server = host, secret = secret, dict = self.dict,
			authport = authport, acctport = acctport)
		
		self.srv.retries = retries
		self.srv.timeout = timeout


	def getAuthPacket(self, attributes = {}, **kwattrs):
		"""Get RADIUS authorization packet.
			Input: (dict) attributes for RADIUS server.
			Output: (pyrad.packet.AcctPacket) RADIUS authorization packet.
		"""
		if not attributes:
			attributes = kwattrs
		req = self.srv.CreateAuthPacket(code = packet.AccessRequest, **attributes)
		if 'User-Password' in attributes or 'User_Password' in attributes:
			req["User-Password"] = req.PwCrypt(req["User-Password"][0])
		return req
	
	
	def getAcctPacket(self, attributes = {}, **kwattrs):
		"""Get RADIUS accounting packet.
			Input: (dict) attributes for RADIUS server.
			Output: (pyrad.packet.AcctPacket) RADIUS accounting packet.
		"""
		if not attributes:
			attributes = kwattrs
		req = self.srv.CreateAcctPacket(code = packet.AccountingRequest, **attributes)
		return req
	
	
	def sendPacket(self, req):
		"""Send packet to RADIUS server.
			Raises exception upon error.
			Input: (pyrad.packet.Packet) RADIUS packet
			Output: RADIUS server response
		"""
		try:
			reply = self.srv.SendPacket(req)
			return reply
		except Timeout:
			raise RadClientError("RADIUS server does not reply")
		except socket.error, error:
			raise RadClientError("Network error: " + error[1])


	def bind(self, addr):
		"""Bind socket to an address.
			Binding the socket used for communicating to an address can be
			usefull when working on a machine with multiple addresses.
			Input: (pyrad.packet.Packet) Address tuple (ip, port for AF_INET)
		"""
		try:
			self.srv.bind(addr)
		except socket.error, error:
			print "Network error: " + error[1]
			sys.exit(1)


	@classmethod
	def genAcctSessionId(cls, length = 16, symbols = None):
		"""Generate random string for Acct-Session-Id.
			Input: (int) string length;
				(sequence type) list of valid characters (default: all
					hexadecimal symbols)
			Output: (str) generated accounting session id
		"""
		if symbols is None:
			symbols = cls.hexSymbols
		sesid = ''
		for i in range(length):
			sesid += random.choice(symbols)
		return sesid
	
	
	@classmethod
	def genH323ConfId(cls):
		"""Generate random h323 conference id.
			Input: none
			Output: (str) generated h323 conference id
		"""
		sesid = ''
		for i in range(4):
			for j in range(8):
				sesid += random.choice(cls.hexSymbols)
			sesid += ' '
		sesid = sesid.rstrip(' ')
		return sesid
