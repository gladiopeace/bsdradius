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
CHAP module for BSD Radius server
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_7/bsdradius/serverModules/mod_chap.py $
# Author:		$Author: valts $
# File version:	$Revision: 333 $
# Last changes:	$Date: 2007-08-17 02:38:15 +0300 (Pk, 17 Aug 2007) $


import md5
from bsdradius.logger import *
import types



def chapAuthorization(received, check, reply):
	"""Check for CHAP-Password presence in received attributes and
		set Auth-Type to chap. Later modules should extract User-Name and
		User-Password (plain text) and put them into check dictionary.
		Input: (dict) received attributes, (dict) check attributes, (dict) reply
			attributes
		Output: (bool) modules status (True - ok, False - rejected)
	"""
	if 'CHAP-Password' in received:
		authType = check.get('Auth-Type', [None])[0]
		if authType:
			debug ("Auth-Type already set to: %s. I'll not change it" % authType)
		else:
			debug ("Setting Auth-Type to chap")
			check['Auth-Type'] = ['chap']
	else:
		debug ('No CHAP-Password found in request. Doing nothing.')
	return True


	
def chapAuthentication(received, check, reply):
	"""If Auth-Type is set to chap look for User-Name and plain text User-Password
		in check items. Recelculate digest from plain text password and clarify if
		it is the same as received CHAP-Password
		Input: (dict) received attributes, (dict) check attributes, (dict) reply
			attributes
		Output: (bool) modules status (True - ok, False - rejected)
	"""
	authType = check['Auth-Type'][0]
	if authType == 'chap':
		debug ('Performing CHAP authentication')
		# check for necessary attributes
		chapPassword = received.get('CHAP-Password', [None])[0]
		if not chapPassword:
			error('Attribute "CHAP-Password" is required for authentication')
			return False
		user = check.get('User-Name', [None])[0]
		if not user:
			error('Attribute "User-Name" is required for authentication')
			return False
		plainPassword = check.get('User-Password', [None])[0]
		if not plainPassword:
			error('Attribute "User-Password" is required for authentication')
			return False
		
		# Use CHAP-Challenge from received attribues or Request-Authenticator if CHAP-Challnege not available
		challenge = received.get('CHAP-Challenge', [None])[0]
		if challenge:
			debug ('Using CHAP-Challenge received from client')
		else:
			debug ('Using Request-Authenticator as CHAP challenge')
			challenge = received['Request-Authenticator'][0]
		
		# calculate the digest and check password
		if chapPassword == chapEncode(chapPassword[0], challenge, plainPassword):
			debug ('User "%s" with password "%s" authenticated successfully' % (user, plainPassword))
			return True
		else:
			debug ('Password "%s" for user "%s" not valid' % (plainPassword, user))
			return False
	else:
		debug ('Auth type: %s. Doing nothing' % authType)
		return True



def chapEncode(id, challenge, secret):
	"""hash id, challenge and secret togeather using md5 digest algorhytm
		Input: (string) 1 byte long unique id; (string) 16 byte long random string;
			(string) plain text shared secret (password)
		Output: (string) 1 byte long unique id + 16 byte long md5 digest
			
	"""
	digest = md5.new(id + secret + challenge).digest()
	return id + digest
