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
Digest authentication module for BSD Radius server
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_4/bsdradius/serverModules/mod_digest.py $
# Author:		$Author: valts $
# File version:	$Revision: 201 $
# Last changes:	$Date: 2006-04-04 17:22:11 +0300 (Ot, 04 Apr 2006) $


import urllib2
from bsdradius.logger import *
from bsdradius.DigestAuth import DigestAuth




def digestAuthorization(received, check, reply):
	"""Look for Digest-Response and Digest-Attributes in received
		items. Set Auth-Type to "digest" if found.
		Input: (dict) received attributes, (dict) check attributes, (dict) reply
			attributes
		Output: (bool) modules status (True - ok, False - rejected)
	"""
	# check for Digest-Response and Digest-Attributes in received items
	if 'Digest-Response' in received:
		if not 'Digest-Attributes' in received:
			error('Received Digest-Response without Digest-Attributes')
			return False
		# set auth type
		authType = check['Auth-Type'][0]
		if authType:
			debug ("Auth-Type already set to: %s. I'll not change it" % authType)
		else:
			debug ('Setting Auth-Type to "digest"')
			check['Auth-Type'] = ['digest']
	else:
		debug ('No Digest-Response found in request. Doing nothing.')
	return True
	
	

def digestAuthentication(received, check, reply):
	"""
		Input: (dict) received attributes, (dict) check attributes, (dict) reply
			attributes
		Output: (bool) modules status (True - ok, False - rejected)
	"""
	authType = check['Auth-Type'][0]
	if authType == 'digest':
		debug ('Performing Digest authentication')
		# check for necessary attributes
		user = check.get('User-Name', [None])[0]
		if not user:
			error('Attribute "User-Name" is required for authentication')
			return False
		plainPassword = check.get('User-Password', [None])[0]
		if not plainPassword:
			error('Attribute "User-Password" is required for authentication')
			return False
		digestResponse = received.get('Digest-Response', [None])[0]
		if not digestResponse:
			error('Attribute "Digest-Response" is required for authentication')
			return False
		digestAttributes = received.get('Digest-Attributes', [None])
		if not digestAttributes:
			error('Attribute "Digest-Attributes" is required for authentication')
			return False
		
		authHandler = DigestAuth({user : plainPassword})
		authResult = authHandler.authenticateRadius(digestResponse, digestAttributes)
		if authResult:
			debug ('User "%s" with password "%s" authenticated successfully' % (user, plainPassword))
			return True
		else:
			debug ('Password "%s" for user "%s" not valid' % (plainPassword, user))
			return False
	else:
		debug ('Auth type: %s. Doing nothing' % authType)
		return True
