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
BSD Radius preprocessing module. Changes and adds some
useful attributes in received packet data.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_6/bsdradius/serverModules/preprocess.py $
# Author:		$Author: valts $
# File version:	$Revision: 217 $
# Last changes:	$Date: 2006-05-18 15:25:31 +0300 (Ce, 18 Mai 2006) $


from types import *
from bsdradius.logger import *



def addMissingAttributes(received):
	"""Add missing attributes such as Client-IP-Address and
		NAS-IP-Address
		Input: (dict) received attributes
		Output: none
	"""
	if 'NAS-IP-Address' not in received:
		debug ('Adding missing attribute: NAS-IP-Address')
		received['NAS-IP-Address'] = [received['Client-IP-Address'][0]]



def preprocessAuthorization(received, check, reply):
	"""Do everything that's necessary to prepare received attributes
		for authorization.
		Input: (dict) received, (dict) check, (reply) reply attributes
		Output: (bool) True - success, False - failure
	"""
	addMissingAttributes(received)
	fixVsa(received)
	return True
	
	
	
def preprocessAccounting(received):
	"""Do everything that's necessary to prepare received attributes
		for accounting.
		Input: (dict) received
		Output: none
	"""
	addMissingAttributes(received)
	fixVsa(received)



# pssibly crypted attributes which could contain "=" sometimes
skipAttrs = ['Request-Authenticator', 'User-Password']
def fixVsa(received):
	"""Fix VSA attributes which values contain attribute name before "=" sign.
		Add new items to request data if neccessary.
		Input: (dict) received packet data
		Output: (none)
	"""
	info ('--- Fixing VSA attributes ---')
	for key, values in received.items():
		if key in skipAttrs:
			continue
		for i in xrange(len(values)):
			if not isinstance(values[i], StringType):
				continue
			# split by 1st '=' symbol. Result should be ['key', 'value'] pair
			tokens = values[i].split('=', 1)
			if len(tokens) != 2:
				continue
			
			debug ('Fixing attribute: %r' % key)
			newkey, newval = tokens[:]
			# replace current value with stripped value if extracted attribute
			# name is the same as current attribute name
			if newkey == key:
				debug ('  [Replace] %r: %r' % (key, newval))
				values[i] = newval
			# add new item to request data if extracted attribute name is not
			# yet present in request items
			elif newkey not in received:
				debug ('  [New] %r: %r' % (newkey, newval))
				received[newkey] = [newval]
			# append stripped value if extracted attribute name is already
			# present in request items
			else:
				debug ('  [Append] %r: %r' % (newkey, newval))
				received[newkey].append(newval)
