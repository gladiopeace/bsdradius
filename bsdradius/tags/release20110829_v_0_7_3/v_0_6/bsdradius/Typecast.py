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
Functions and methods for casting types from string to
other types.
Contains functions and class for inheritance in other classes.
Supported types: 'str', 'string', 'int', 'hex', 'oct', 'dec', 'bool', 'Template'
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_6/bsdradius/Typecast.py $
# Author:		$Author: valts $
# File version:	$Revision: 236 $
# Last changes:	$Date: 2006-06-27 13:48:36 +0300 (Ot, 27 Jūn 2006) $


# for typecasting to Template
from string import Template

### functions ###
def getstr (input):
	return str(input)

def getstring (input):
	return getstr(input)

def getint (input):
	return int(str(input))
		
def gethex (input):
	return int(str(input), 16)

def getoct (input):
	return int(str(input), 8)

def getdec (input):
	return int(str(input), 10)


_booleanStates = {
	True: True, 1: True, '1': True, 'yes': True, 'y': True, 'true': True, 'on': True,
	False: False, 0: False, '0': False, 'no': False, 'n': False, 'false': False, 'off': False
}
def getbool (input):
	inp = str(input)
	if inp.lower() not in _booleanStates:
		raise ValueError, 'Not a boolean value: %s' % inp
	return _booleanStates[inp.lower()]

def getTemplate (input):
	return Template(str(input))



class Typecast:
	"""Use this class as base class in your classes to 
		add typecasting functionality. This class defines
		methods which are wrappers to functions in module
		namespace.
		You can override attribute "data" in derived classes.
		Since self.data is dictionary (with multiple levels) you can
		pass any number of keys to typecasting methods. They all use method
		_getItem() which searches recursively in self.data for rightmost key value.
	"""
	
	_booleanStates = _booleanStates
	
	def __init__(self):
		self.data = {}
		
	def _getItem(self, keys):
		"""Search recursively for item by given keys
			Input: (str) keys Example: t._getItem('key1', 'key2', 'key3')
			Output: (mixed) value
		"""
		if not keys:
			raise KeyError, 'No key specified'
		tmp = None
		for key in keys:
			if tmp is None:
				tmp = self.data[key]
			else:
				tmp = tmp[key]
		return tmp
	
	def getstr (self, *keys):
		return getstr(self._getItem(keys))
	
	def getstring (self, *keys):
		return getstring(self._getItem(keys))
	
	def getint (self, *keys):
		return getint(self._getItem(keys))
	
	def gethex (self, *keys):
		return gethex(self._getItem(keys))
	
	def getoct (self, *keys):
		return getoct(self._getItem(keys))
	
	def getdec (self, *keys):
		return getdec(self._getItem(keys))
	
	def getbool (self, *keys):
		return getbool(self._getItem(keys))
	
	def getTemplate (self, *keys):
		return getTemplate(self._getItem(keys))
		
# holds references to all supported typecast methods
typecastMethods = {
	'str' : getstr,
	'string' : getstring,
	'int' : getint,
	'hex' : gethex,
	'oct' : getoct,
	'dec' : getdec,
	'bool' : getbool,
	'Template' : getTemplate,
}
	
# holds references to all supported typecast methods
Typecast.typecastMethods = {
	'str' : Typecast.getstr,
	'string' : Typecast.getstring,
	'int' : Typecast.getint,
	'hex' : Typecast.gethex,
	'oct' : Typecast.getoct,
	'dec' : Typecast.getdec,
	'bool' : Typecast.getbool,
	'Template' : Typecast.getTemplate,
}
