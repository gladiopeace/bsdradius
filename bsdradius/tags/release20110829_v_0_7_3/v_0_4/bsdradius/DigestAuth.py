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
Holds digest authentication class for BSD Radius server
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_4/bsdradius/DigestAuth.py $
# Author:		$Author: valts $
# File version:	$Revision: 201 $
# Last changes:	$Date: 2006-04-04 17:22:11 +0300 (Ot, 04 Apr 2006) $


import md5
import time
import exceptions
from types import ListType
from bsdradius.logger import *
from bsdradius.misc import printException


class DigestAuthError(Exception):
	pass

class DigestParseError(Exception):
	pass



# Originally by Peter van Kampen in 2004/08/30
# URL: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/302378
class DigestAuth:
	"""Incomplete Python implementation of Digest Authentication.
		For the full specification. http://www.faqs.org/rfcs/rfc2617.html
		Currently this class is Can operate with HTTP headers and RADIUS
		Digest-Attributes.
	"""
	
	def __init__(self, users, realm = ''):
		"""Constructor. Pass dict of valid users and optional realm to it.
			Input: (dict) user: password; (string) realm - AuthName in httpd.conf
			Output: (DigestAuth) class instance
		"""
		self.realm = realm
		self.users = users
		self._httpHeaders= []
		self.params = {}
		self.method = ''
		self.uri = ''


	def H(self, data):
		return md5.md5(data).hexdigest()


	def KD(self, secret, data):
		return self.H(secret + ":" + data)


	def A1(self):
		# If the "algorithm" directive's value is "MD5" or is
		# unspecified, then A1 is:
		# A1 = unq(username-value) ":" unq(realm-value) ":" passwd
		username = self.params["username"]
		passwd = self.users.get(username, "")
		return "%s:%s:%s" % (username, self.realm, passwd)
		# This is A1 if qop is set
		# A1 = H( unq(username-value) ":" unq(realm-value) ":" passwd )
		#         ":" unq(nonce-value) ":" unq(cnonce-value)


	def A2(self):
		# If the "qop" directive's value is "auth" or is unspecified, then A2 is:
		# A2 = Method ":" digest-uri-value
		return self.method + ":" + self.uri
		# Not implemented
		# If the "qop" value is "auth-int", then A2 is:
		# A2 = Method ":" digest-uri-value ":" H(entity-body)


	def response(self):
		"""Get Digest-Response
			Input: (none)
			Output: (none)
		"""
		if self.params.has_key("qop"):
			# Check? and self.params["qop"].lower()=="auth":
			# If the "qop" value is "auth" or "auth-int":
			# request-digest  = <"> < KD ( H(A1),     unq(nonce-value)
			#                              ":" nc-value
			#                              ":" unq(cnonce-value)
			#                              ":" unq(qop-value)
			#                              ":" H(A2)
			#                      ) <">
			return self.KD(self.H(self.A1()), \
							self.params["nonce"] 
							+ ":" + self.params["nc"]
							+ ":" + self.params["cnonce"]
							+ ":" + self.params["qop"]                    
							+ ":" + self.H(self.A2()))
		else:
			# If the "qop" directive is not present (this construction is
			# for compatibility with RFC 2069):
			# request-digest  =
			#         <"> < KD ( H(A1), unq(nonce-value) ":" H(A2) ) > <">
			return self.KD(self.H(self.A1()), \
						self.params["nonce"] + ":" + self.H(self.A2()))


	def _parseHttpHeader(self, authheader):
		"""Parse HTTP header string
			Input: (string) http header
			Output: none
		"""
		try:
			n = len("Digest ")
			authheader = authheader[n:].strip()
			items = authheader.split(", ")
			keyvalues = [i.split("=", 1) for i in items]
			keyvalues = [(k.strip(), v.strip().replace('"', '')) for k, v in keyvalues]
			self.params = dict(keyvalues)
		except:
			self.params = {}
			raise


	def _parseDigestAttributes(self, digestAttributes):
		"""Parse Digest-Attributes received by RADIUS server
			Input: (list) attributes
				Attribute format:
					<id: 1 byte><length: 1 byte><data: length - 2 bytes>
			Output: none
		"""
		try:
			assert isinstance(digestAttributes, ListType)
			supportedTypes = {
				1: 'realm',
				2: 'nonce',
				3: 'method',
				4: 'uri',
				6: 'algorhytm',
				10: 'username',
			}
			for attr in digestAttributes:
				# Check if those crappy attributes are sent containing correct info
				# check if attribute is long enough
				if len(attr) < 3:
					raise DigestParseError, 'Attribute length too small: %s. Should be at least 3' % len(attr)
				# extract attribute type and check if it is valid
				attrType = ord(attr[0])
				if attrType <=0 or attrType > 10:
					raise DigestParseError, 'Invalid attribute type: %s' % attrType
				# skip unknown types
				if attrType not in supportedTypes:
					continue
				# Extract attribute length and check if it is correct.
				# This is not very necessary but we'll check it anyway - to make pain for crappy
				# implementation "developers".
				attrLength = ord(attr[1])
				if attrLength != len(attr):
					raise DigestParseError, 'Received incorrect attribute length: %s. Real length is %s' % (attrLength, len(attr))
				attrContent = attr[2:]
				
				# assign attribute contents to variables depending on attribute type
				self.params[supportedTypes[attrType]] = attrContent
		except:
			self.params = {}
			raise
			
			
	def _returnHttpTuple(self, code):
		return (code, self._httpHeaders, self.params.get("username", ""))
		
		
	def _createNonce(self):
		return md5.md5("%d:%s" % (time.time(), self.realm)).hexdigest()
		
		
	def createHttpAuthheaer(self):
		self._httpHeaders.append((
			"WWW-Authenticate", 
			'Digest realm="%s", nonce="%s", algorithm="MD5", qop="auth"'
			% (self.realm, self._createNonce())
			))


	def _authenticate(self):
		""" Check the response for this method and uri with authheader
			Input: (none)
			Output: (bool) True - success, False - reject
				Rises DigestAuthError on failure
		"""
		if not self.params:
			raise DigestAuthError, 'Parsed attribute dictinary self.params is empty! ' + \
				'You should be more careful when parsing attributes'
		# Check for required parameters
		required = ["username", "realm", "nonce", "response"]
		for k in required:
			if not self.params.has_key(k):
				raise DigestAuthError, 'Can not find parameter "%s" in self.params' % k
		# If the user is unknown we can deny access right away
		if not self.users.has_key(self.params["username"]):
			debug ('User not found between valid users')
			return False
		# If qop is sent then cnonce and cn MUST be present
		if self.params.has_key("qop"):
			if 'cnonce' not in self.params and 'cn' not in self.params:
				raise DigestAuthError, '"cnonce" or "cn" attributes are required when "qop" supplied'
		# All else is OK, now check the response.
		if self.response() == self.params["response"]:
			return True
		else:
			return False



	def authenticateHttp(self, method, uri, authheader = ''):
		""" Check the response for this method and uri with authheader

		returns a tuple with:
		  - HTTP_CODE
		  - a tuple with header info (key, value) or None
		  - and the username which was authenticated or None
		"""
		# set up and parse received data
		self.method = method
		self.uri = uri
		if authheader.strip() == "":
			self.createHttpAuthHeader()
			return self._returnHttpTuple(401)
		try:
			self._parseHttpHeader(authheader)
		except:
			return self._returnHttpTuple(400)
		# perform authorization
		try:
			if self._authenticate():
				return self._returnHttpTuple(200)
			else:
				self.createHttpAuthHeader()
				return self._returnHttpTuple(401)
		except:
			return self._returnHttpTuple(400)



	def authenticateRadius(self, response, digestAttributes = []):
		"""Check the response for this method with attributes received from
			NAS.
			Input: (string) check method, (string) uri, (list) unparsed Digest-Attributes
			Output: (tuple) result:
				(bool) status, True - OK, False - Failure
				(tuple) Digest-Attributes 
		"""
		# set up and parse received data
		try:
			self._parseDigestAttributes(digestAttributes)
		except:
			printException()
			return False
		required = ['realm', 'method', 'uri']
		for attr in required:
			if attr not in self.params:
				error('Can not find parameter "%s" in self.params' % key)
				return False
		# HACK: put attributes in correct places
		self.params['response'] = response
		self.realm = self.params['realm']
		self.method = self.params.pop('method')
		self.uri = self.params.pop('uri')
		# perform authorization
		try:
			if self._authenticate():
				return True
			else:
				return False
		except:
			printException()
			return False
