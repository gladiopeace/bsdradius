# BSD Radius server class definition
# Derived from Wichert Akkerman's <wichert@wiggy.net> pyrad.


# import modules
import select, socket
from pyrad import host, packet



class BsdRadiusServer(host.Host):
	"""BSD Radius Server class defnition
		This class implements the basics of a RADIUS server. It takes care
		of the details of receiving and decoding requests; processing of
		the requests should be done by overloading the appropriate methods
		in derived classes.
	
		@ivar  hosts: hosts who are allowed to talk to us
		@type  hosts: dictionary of Host class instances
		@ivar  _poll: poll object for network sockets
		@type  _poll: select.poll class instance
		@ivar _fdmap: map of filedescriptors to network sockets
		@type _fdmap: dictionary
		@cvar MaxPacketSize: maximum size of a RADIUS packet
		@type MaxPacketSize: integer
	"""



	MaxPacketSize	= 8192



	def __init__(self, addresses = [], authport = 1812, acctport = 1813, hosts = {}, dict = None):
		"""Constructor.

		@param addresses: IP addresses to listen on
		@type  addresses: sequence of strings
		@param  authport: port to listen on for authentication packets
		@type   authport: integer
		@param  acctport: port to listen on for accounting packets
		@type   acctport: integer
		@param     hosts: hosts who we can talk to
		@type      hosts: dictionary mapping IP to RemoteHost class instances
		@param      dict: RADIUS dictionary to use
		@type       dict: Dictionary class instance
		"""
		host.Host.__init__(self, authport, acctport, dict)
		self.hosts = hosts

		self.authfds = []
		self.acctfds = []

		for addr in addresses:
			self.BindToAddress(addr)
	


	def BindToAddress(self, addr):
		"""Add an address to listen to.

		An empty string indicated you want to listen on all addresses.

		@param addr: IP address to listen on
		@type  addr: string
		"""
		authfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		authfd.bind((addr, self.authport))

		acctfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		acctfd.bind((addr, self.acctport))

		self.authfds.append(authfd)
		self.acctfds.append(acctfd)
	


	def HandleAuthPacket(self, pkt):
		"""Handle authentication request
		"""
		
		print "Received authorization request"
		print "Attributes: "
		for attr in pkt.keys():
			print "%s: %s" % (attr, pkt[attr])
		return (True, {'Acct-Session-Time': 30})



	def HandleAcctPacket(self, pkt):
		"""Handle accounting packet
		"""
		print "Received accounting request"
		print "Attributes: "
		for attr in pkt.keys():
			print "%s: %s" % (attr, pkt[attr])
		
		return (True, {'kaka': 'oi'})



	def _HandleAuthPacket(self, pkt, fd):
		"""Process a packet received on the authentication port

		If this packet should be dropped instead of processed a
		PacketError exception should be raised. The main loop will
		drop the packet and log the reason.

		@param pkt: packet to process
		@type  pkt: Packet class instance
		@param  fd: socket to read packet from
		@type   fd: socket class instance
		"""
		if not self.hosts.has_key(pkt.source[0]):
			raise PacketError, "Received packet from unknown host"

		pkt.secret = self.hosts[pkt.source[0]].secret

		if pkt.code != packet.AccessRequest:
			raise PacketError, "Received non-authentication packet on authentication port"
		
		try:
			reply = self.HandleAuthPacket(pkt)
		except:
			print "Error processing auth packet"
			
		if reply:
			reply = self.CreateReplyPacket(pkt)
			self.SendReplyPacket(fd, reply)



	def _HandleAcctPacket(self, pkt, fd):
		"""Process a packet received on the accounting port

		If this packet should be dropped instead of processed a
		PacketError exception should be raised. The main loop will
		drop the packet and log the reason.

		@param pkt: packet to process
		@type  pkt: Packet class instance
		@param  fd: socket to read packet from
		@type   fd: socket class instance
		"""
		if not self.hosts.has_key(pkt.source[0]):
			raise PacketError, "Received packet from unknown host"

		pkt.secret = self.hosts[pkt.source[0]].secret

		if not pkt.code in [ packet.AccountingRequest,
				packet.AccountingResponse ]:
			raise PacketError, "Received non-accounting packet on accounting port"

		try:
			reply = self.HandleAcctPacket(pkt)
		except:
			print "Error processing auth packet"
			
		if reply:
			reply = self.CreateReplyPacket(pkt)
			self.SendReplyPacket(fd, reply)
	


	def _GrabPacket(self, pktgen, fd):
		"""Read a packet from a network connection.

		This method assumes there is data waiting for to be read.

		@param fd: socket to read packet from
		@type  fd: socket class instance
		@return: RADIUS packet
		@rtype:  Packet class instance
		"""
		(data,source) = fd.recvfrom(self.MaxPacketSize)
		pkt = pktgen(data)
		pkt.source = source
		pkt.fd = fd

		return pkt



	def _PrepareSockets(self):
		"""Prepare all sockets to receive packets.
		"""
		for fd in self.authfds + self.acctfds:
			self._fdmap[fd.fileno()] = fd
			self._poll.register(fd.fileno(), select.POLLIN|select.POLLPRI|select.POLLERR)

		self._realauthfds = map(lambda x: x.fileno(), self.authfds)
		self._realacctfds = map(lambda x: x.fileno(), self.acctfds)
	


	def CreateReplyPacket(self, pkt, **attributes):
		"""Create a reply packet.

		Create a new packet which can be returned as a reply to a received
		packet.

		@param pkt:   original packet 
		@type pkt:    Packet instance
		"""

		reply = pkt.CreateReply(**attributes)
		reply.source = pkt.source

		return reply



	def _ProcessInput(self, fd):
		"""Process available data.

		If this packet should be dropped instead of processed a
		PacketError exception should be raised. The main loop will
		drop the packet and log the reason.

		This function calls either HandleAuthPacket() or
		HandleAcctPacket() depending on which socket is being
		processed.

		@param  fd: socket to read packet from
		@type   fd: socket class instance
		"""
		if fd.fileno() in self._realauthfds:
			pkt = self._GrabPacket(lambda data, s = self: s.CreateAuthPacket(packet = data), fd)
			self._HandleAuthPacket(pkt, fd)
		else:
			pkt = self._GrabPacket(lambda data, s = self: s.CreateAcctPacket(packet = data), fd)
			self._HandleAcctPacket(pkt, fd)



	def Run(self):
		"""Main loop.

		This method is the main loop for a RADIUS server. It waits
		for packets to arrive via the network and calls other methods
		to process them.
		"""
		self._poll = select.poll()
		self._fdmap = {}
		self._PrepareSockets()

		while 1:
			for (fd, event) in self._poll.poll():
				fdo = self._fdmap[fd]
				if event == select.POLLIN:
					try:
						fdo = self._fdmap[fd]
						self._ProcessInput(fdo)
					except PacketError, err:
						print "Dropping packet: " + str(err)
					except packet.PacketError, err:
						print "Received a broken packet: " + str(err)
				else:
					print "Unexpected event!"
