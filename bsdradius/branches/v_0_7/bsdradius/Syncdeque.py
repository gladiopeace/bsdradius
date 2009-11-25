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
Various synchronization queues
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_7/bsdradius/Syncdeque.py $
# Author:		$Author: atis $
# File version:	$Revision: 313 $
# Last changes:	$Date: 2007-07-02 16:56:26 +0300 (Pr, 02 Jūl 2007) $


import collections, thread
from bsdradius.pyrad import packet
import time


class Syncdeque:
	"""Synchronized double-ended queue"""

	def __init__(self, maxsize = 0):
		"""maxsize = 0 means infinite size"""
		self.dq = collections.deque()
		self.maxsize = maxsize

		# create locks
		self.access_lock = thread.allocate_lock()
		self.get_lock = thread.allocate_lock()
		self.empty_lock = thread.allocate_lock()


		
	def put(self, item):
		self.access_lock.acquire()

		# check if queue is full
		if (self.maxsize > 0 and len(self.dq) == self.maxsize):
			return False
		
		self.dq.append(item)

		if self.empty_lock.locked():
			self.empty_lock.release()
		self.access_lock.release()
		return True



	def putleft(self, item):
		self.access_lock.acquire()

		# check if queue is full
		if (self.maxsize > 0 and len(self.dq) == self.maxsize):
			return False
		
		self.dq.appendleft(item)
		if self.empty_lock.locked():
			self.empty_lock.release()
		self.access_lock.release()



	def get(self):
		self.get_lock.acquire()
		self.access_lock.acquire()
		if len(self.dq) == 0:
			self.empty_lock.acquire()
			self.access_lock.release()
			self.empty_lock.acquire()
			self.access_lock.acquire()
			item = self.dq.pop()
			if self.empty_lock.locked():
				self.empty_lock.release()
			self.access_lock.release()
			self.get_lock.release()
			return item

		item = self.dq.pop()
		self.access_lock.release()
		self.get_lock.release()		
		return item



	def __str__(self):
		return str(self.dq)



	def __len__(self):
		return len(self.dq)



class RadiusDeque:

	def __init__(self, maxauth_packets = 100, maxacct_packets = 100):
		# init queue object
		self.dq = collections.deque()

		# create locks
		self.access_lock = thread.allocate_lock()
		self.get_lock = thread.allocate_lock()
		self.empty_lock = thread.allocate_lock()

		# packet counters and limits
		self.num_auth = 0 # number of auth packets
		self.num_acct = 0 # number of acct packets
		self.max_auth = maxauth_packets;
		self.max_acct = maxacct_packets;



	def add_auth_packet(self, pkt):
		"""Add auth packet"""
		self.access_lock.acquire()

		if (self.num_auth == self.max_auth):
			# remove oldest auth packet & add the new one
			del self.dq[self.num_acct]
			self.dq.append(pkt)
		else:
			self.dq.append(pkt)
			self.num_auth += 1
			
		if self.empty_lock.locked():
			self.empty_lock.release()
		self.access_lock.release()
		return True



	def add_acct_packet(self, pkt):
		"""Add accounting packet"""
		self.access_lock.acquire()

		if (self.num_acct == self.max_acct):
			self.access_lock.release()
			return False
		
		self.dq.appendleft(pkt)
		self.num_acct += 1
		if self.empty_lock.locked():
			self.empty_lock.release()
		self.access_lock.release()
		return True
		
		

	def remove_packet(self, blocking = True):
		"""Retrieve a RADIUS packet, block if there are none"""
		self.get_lock.acquire()
		self.access_lock.acquire()
		if len(self.dq) == 0:
			if not blocking:
				self.access_lock.release()
				self.get_lock.release()
				time.sleep(0.0001)
				return None
			self.empty_lock.acquire()
			self.access_lock.release()
			self.empty_lock.acquire()
			
			self.access_lock.acquire()
			pkt = self.dq.pop()
			# check packet type and decrement respective counter
			if isinstance(pkt, packet.AuthPacket):
				self.num_auth -= 1
			if isinstance(pkt, packet.AcctPacket):
				self.num_acct -= 1
				
			if self.empty_lock.locked():
				self.empty_lock.release()
			self.access_lock.release()
			self.get_lock.release()
			return pkt

		pkt = self.dq.pop()
		# check packet type and decrement respective counter
		if isinstance(pkt, packet.AuthPacket):
			self.num_auth -= 1
		if isinstance(pkt, packet.AcctPacket):
			self.num_acct -= 1
		
		self.access_lock.release()
		self.get_lock.release()
		return pkt
