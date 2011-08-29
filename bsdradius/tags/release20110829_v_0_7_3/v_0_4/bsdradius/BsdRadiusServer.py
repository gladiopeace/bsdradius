## BSDRadius is released under BSD license.
## Copyright (c) 2006, DATA TECH LABS
## All rights reserved. 
## 
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met: 
## * Redistributions of source code must retain the above copyright notice,
##   this list of conditions and the following disclaimer. 
## * Redistributions in binary form must reproduce the above copyright notice,
##   this list of conditions and the following disclaimer in the documentation
##   and/or other materials provided with the distribution. 
## * Neither the name of the DATA TECH LABS nor the names of its contributors
##   may be used to endorse or promote products derived from this software without
##   specific prior written permission. 
## 
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
## ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""
BSD Radius server class definition
Derived from Wichert Akkerman's <wichert@wiggy.net> pyrad.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_4/bsdradius/BsdRadiusServer.py $
# Author:		$Author: valts $
# File version:	$Revision: 201 $
# Last changes:	$Date: 2006-04-04 17:22:11 +0300 (Ot, 04 Apr 2006) $


# import modules
import select, socket
from bsdradius import Syncdeque
from threading import Thread
import time
from bsdradius.pyrad import packet
from bsdradius.logger import *
from bsdradius.Config import main_config
from bsdradius import modules
from bsdradius import logger
from bsdradius import misc
from bsdradius.serverModules import dumpPacket



# socket types
SOCKTYPE_AUTH = 1
SOCKTYPE_ACCT = 2

# maximum radius packet size
MAXPACKETSZ = 8192


# dropped packet exception
class DroppedPacket(Exception):
	pass

# authentication failure exception
class AuthFailure(Exception):
	pass

# accounting failure exception
class AcctFailure(Exception):
	pass


class BsdRadiusServer:
	"""BSD Radius Server class defnition
	
		@ivar  hosts: hosts who are allowed to talk to us
		@type  hosts: dictionary of Host class instances
		@ivar  pollobj: poll object for network sockets
		@type  pollobj: select.poll class instance
		@ivar fdmap: map of filedescriptors to network sockets
		@type fdmap: dictionary
	"""
	
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
		self.dict = dict
		self.authport = authport
		self.acctport = acctport
		self.hosts = hosts

		self.authfds = []
		self.acctfds = []

		for addr in addresses:
			self.BindToAddress(addr)


	
	def BindToAddress(self, addr):
		"""Add an address to listen to.

		An empty string indicates you want to listen on all addresses.

		@param addr: IP address to listen on
		@type  addr: string
		"""
		authfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		authfd.bind((addr, self.authport))

		acctfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		acctfd.bind((addr, self.acctport))

		self.authfds.append(authfd)
		self.acctfds.append(acctfd)



	def CreateThreads(self):
		"""Starts all threads"""
		# start thread which listens to sockets
		#thread.start_new_thread(self.Listen, ())
		tListen = ListenThread(self)
		tListen.start()
		
		# start worker threads
		numthreads = 1
		if not main_config['SERVER']['no_threads']:
			numthreads =  main_config['SERVER']['number_of_threads']
		for x in range(numthreads):
			#thread.start_new_thread(self.WorkThread, (x,))
			tWorking = WorkingThread(self)
			tWorking.start()
			



	def RegisterSockets(self):
		"""Prepare all sockets to receive packets."""
		events = select.POLLIN | select.POLLPRI | select.POLLERR

		# register auth sockets
		for sock in self.authfds:
			self.fdmap[sock.fileno()] = (sock, SOCKTYPE_AUTH)
			self.pollobj.register(sock, events)

		# register accounting sockets
		for sock in self.acctfds:
			self.fdmap[sock.fileno()] = (sock, SOCKTYPE_ACCT)
			self.pollobj.register(sock, events)



	def Run(self):
		"""Main loop.

		Wait for packets to arrive via network and place them on
		synchronization queues for other threads to process.
		"""
		# we map socket descriptors (integers) to their socket objects
		# because when polling for events we only receive the
		# descriptor int and must find which object it refers to
		self.fdmap = {}
		
		# register sockets for event polling
		self.pollobj = select.poll()
		self.RegisterSockets()

		# get queue limits
		auth_qlen = main_config["AUTHORIZATION"]["auth_queue_maxlength"]
		acct_qlen = main_config["ACCOUNTING"]["acct_queue_maxlength"]
		
		# create synchronization queue
		self.packets = Syncdeque.RadiusDeque(auth_qlen, acct_qlen)

		self.CreateThreads()



	def addClientHosts(self, hostsInfo):
		"""Simplify adding client hosts.
			Input: (dict) clients configuration data.
				Format: {'address': {'name' : name, 'secret': secret}}
			Output: none
		"""
		for address, tokens in hostsInfo.items():
			# print what we are doing
			if str(address) not in self.hosts:
				debug ('Adding client %s: %s' % (address, tokens['name']))
			else:
				oldItem = self.hosts[str(address)]
				if oldItem.name != tokens['name']:
					debug ('Changing client\'s "%s" name from "%s" to "%s"' % (address, oldItem.name, tokens['name']))
				if oldItem.secret != tokens['secret']:
					debug ('Changing client\'s "%s" secret' % address)
			# if we need to log from one client only let's set the needed attributes to
			# client's host entry
			enableLogging = False
			if address == main_config['SERVER']['log_client']:
				enableLogging = True
				if address not in self.hosts:
					debug ('Enabling unrestricted logging for client "%s"' % tokens['name'])
				elif not self.hosts[address].enableLogging:
					debug ('Enabling unrestricted logging for client "%s"' % tokens['name'])
			
			# replace old or create new client record
			self.hosts[str(address)] = RemoteHost(address, tokens['secret'], tokens['name'], enableLogging)



class RemoteHost:
	"""Remote RADIUS capable host we can talk to."""

	def __init__(self, address, secret, name, enableLogging = False, authport = 1812, acctport = 1813):
		"""Constructor.

		@param   address: IP address
		@type    address: string
		@param    secret: RADIUS secret
		@type     secret: string
		@param      name: short name (used for logging only)
		@type       name: string
		@param  authport: port used for authentication packets
		@type   authport: integer
		@param  acctport: port used for accounting packets
		@type   acctport: integer
		"""
		self.address	= str(address)
		self.secret		= str(secret)
#		self.authport	= int(authport)
#		self.acctport	= int(acctport)
		self.name		= str(name)
		self.enableLogging = bool(enableLogging)
		
		
		
class WorkingThread(Thread):
	_threadTopId = 0
	
	def __init__(self, server):
		# call base class' constructor
		Thread.__init__(self)
		self.server = server
		# assign id to this thread
		self.setName('Working thread ' + str(WorkingThread._threadTopId))
		WorkingThread._threadTopId += 1
		self.threadMayRun = True
		
		
		
	def run(self):
		"""Thread that does the actual job of processing RADIUS packets"""
		# since this method is assigned to thread we have to catch all exceptions
		# by ourselves
		try:
			threadnum = self.getName()
			hosts = self.server.hosts
			packets = self.server.packets
			auth_timeout = main_config["AUTHORIZATION"]["packet_timeout"]
			
			info("--- started %s ---" % threadnum)
			while self.threadMayRun:
				# grab a RADIUS packet and process it
				pkt = packets.remove_packet(blocking = False)
				if not pkt:
					continue
				
				# check if this thread should be allowed for logging
				if pkt.source[0] in hosts and hosts[pkt.source[0]].enableLogging:
					logger.addUnrestrictedThread()
				
				info('thread "%s" grabbed a packet for processing' % threadnum)
				if isinstance(pkt, packet.AuthPacket):
					
					# check if packet is too old
					if (time.time() - pkt.timestamp > auth_timeout):
						continue
					
					try:
						authResult = self.ProcessAuthPacket(pkt)		
					except AuthFailure, err:
						error ("auth failure: ", err)
						continue
					except:
						misc.printException()
						continue
	
					# create and send a reply packet
					address = pkt.source[0]
					client = hosts[address]
					if authResult[0]:
						# access accept
						code = packet.AccessAccept
						debug ("Sending Authorization ACCEPT to %s (%s)" % (client.name, address))
					else:
						# access reject
						code = packet.AccessReject
						debug ("Sending Authorization REJECT to %s (%s)" % (client.name, address))
						
					reply = pkt.CreateReply(**authResult[1])
					reply.source = pkt.source
					reply.code = code
					debug (reply)
					pkt.fd.sendto(reply.ReplyPacket(), reply.source)
	
				elif isinstance(pkt, packet.AcctPacket):
					try:
						self.ProcessAcctPacket(pkt)
					except AcctFailure, err:
						error ("acct failure: ", err)
						continue
					except:
						misc.printException()
						continue
				else:
					error('Wrong packet received: ', pkt)
						
				info ('%s\n\n' % ('=' * 62))
				
				# remove this thread from non-restricted thread list
				logger.rmUnrestrictedThread()
		except:
			logger.addUnrestrictedThread()
			misc.printException()
			error ('Error in working thread')
			logger.rmUnrestrictedThread()


			
	def ProcessAuthPacket(self, pkt):
		# decrypt crypted attributes
		pkt.decryptAttributes()
		#debug (pkt)
		
		received = dict(pkt) # don't use packet instance any more
		check = {'Auth-Type': [None]}
		reply = {}
		
		debug (misc.authPacketToStr(received))
		
		# wait for authorization modules to process the request
		authzModulesResult = modules.execAuthorizationModules(received, check, reply)
		if authzModulesResult == modules.MODULE_OK:
			# execute authentication modules
			authcModulesResult = modules.execAuthenticationModules(received, check, reply)
			if authcModulesResult == modules.MODULE_OK:
				info ('===\n')
				info ('Authorization and authentication successful')
				return (True, reply)
			else:
				info ('===\n')
				info ('Authentication phase failed')
				if authcModulesResult == modules.MODULE_FAILED:
					dumpPacket.dumpFailedAuthPacket(received)
				return (False, reply)
		else:
			info ('===\n')
			info ('Authorization phase failed')
			if authzModulesResult == modules.MODULE_FAILED:
				dumpPacket.dumpFailedAuthPacket(received)
			return (False, reply)
			
			
			
	def ProcessAcctPacket(self, pkt):
		#debug (pkt)
		received = dict(pkt)
		debug (misc.acctPacketToStr(received))
		
		# wait for accounting modules to process the request
		acctModulesResult = modules.execAccountingModules(received)
		if acctModulesResult == modules.MODULE_OK:
			info ('===\n')
			info ('Accounting successful')
		else:
			info ('===\n')
			info ('Accounting failed')
			dumpPacket.dumpFailedAcctPacket(received)
			
			
			
	def exit(self):
		debug ('Thread "%s" exiting' % self.getName())
		self.threadMayRun = False
			
			
			
class ListenThread(Thread):
	def __init__(self, server):
		# call base class' constructor
		Thread.__init__(self)
		self.server = server
		self.setName('Listen thread')
		self.threadMayRun = True

	def run(self):
		"""Listen to sockets and put received packets in raw
			data queue for later operations.
			Input: none
			Output: none
		"""
		# since this method is assigned to thread we have to catch all exceptions
		# by ourselves
		try:
			info ('--- Started Listen thread ---')
			# poll packets and put them onto rawpacket sync queue
			while self.threadMayRun:
				for (socknum, event) in self.server.pollobj.poll(1000):
					if event != select.POLLIN:
						logger.addUnrestrictedThread()
						error ("unexpected event!")
						logger.rmUnrestrictedThread()
						continue
						
					# receive packet
					(sock, socktype) = self.server.fdmap[socknum]
					(data, addr) = sock.recvfrom(MAXPACKETSZ)
	
					# process the raw packet
					if addr[0] in self.server.hosts and self.server.hosts[addr[0]].enableLogging:
						logger.addUnrestrictedThread()
					self.ProcessPacket(data, addr, sock, socktype)
					logger.rmUnrestrictedThread()
		except:
			logger.addUnrestrictedThread()
			misc.printException()
			error ('Error in listen thread')
			logger.rmUnrestrictedThread()
			
			
			
	def ProcessPacket(self, data, addr, sock, socktype):
		"""
			The purpose of this function is to create a RADIUS packet
			structure, quickly dispatch an accounting-ok packet back
			to the sender (in case we recieved an acct packet) and
			possibly start logging (instead of dispatching for further
			processing) new accounting packets under heavy server load
			when the packet queue becomes overpopulated with accounting
			packets.
		"""
		if socktype == SOCKTYPE_AUTH:
			# create auth packet
			pkt = packet.AuthPacket(dict = self.server.dict, packet = data)
			pkt.timestamp = time.time()
			pkt.source = addr
			pkt.fd = sock
			pkt.addClientIpAddress()
			pkt.addRequestAuthenticator()
			
			if not pkt.source[0] in self.server.hosts:
				error ("dropped packet: received packet from unknown host")
				return

			pkt.secret = self.server.hosts[pkt.source[0]].secret

			if pkt.code != packet.AccessRequest:
				error ("dropped packet: received non-authentication packet on authentication port")
				return

			self.server.packets.add_auth_packet(pkt)
			return

		if socktype == SOCKTYPE_ACCT:
			# create acct packet
			pkt = packet.AcctPacket(dict = self.server.dict, packet = data)
			pkt.timestamp = time.time()
			pkt.source = addr
			pkt.fd = sock			
			pkt.addClientIpAddress()

			if not pkt.source[0] in self.server.hosts:
				error ("dropped packet: received packet from unknown host")
				return
			
			pkt.secret = self.server.hosts[pkt.source[0]].secret
			
			if not pkt.code in [packet.AccountingRequest, packet.AccountingResponse]:
				error ("dropped packet: received non-accounting packet on accounting port")
				return
				
			# create and send a reply packet
			client = self.server.hosts[pkt.source[0]]
			address = pkt.source[0]
			debug ("Sending Accounting ACCEPT to %s (%s)" % (client.name, address))
			reply = pkt.CreateReply()
			reply.source = pkt.source
			sock.sendto(reply.ReplyPacket(), reply.source)
			
			# put the whole packet into packet queue for later processing
			if self.server.packets.add_acct_packet(pkt) == False:
				info ("acct packet queue full, must start logging")
				dumpPacket.dumpUnhandledAcctPacket(pkt)
			return


			
	def exit(self):
		debug ('Thread "%s" exiting' % self.getName())
		self.threadMayRun = False
