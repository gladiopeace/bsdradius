"""
Functions and methods for casting types from string to
other types.
Contains functions and class for inheritance in other classes.
Supported types: 'str', 'string', 'int', 'hex', 'oct', 'dec', 'bool', 'Template'
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/tags/release20050113_v_0_1_0/lib/Typecast.py $
# Author:		$Author: valts $
# File version:	$Revision: 85 $
# Last changes:	$Date: 2005-12-01 11:11:11 +0200 (Ce, 01 Dec 2005) $


# for typecasting to Template
from string import Template

supportedTypes = ['str', 'string', 'int', 'hex', 'oct', 'dec', 'bool', 'Template']

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


_booleanStates = {'1': True, 'yes': True, 'y': True, 'true': True, 'on': True,
						'0': False, 'no': False, 'n': False, 'false': False, 'off': False}
def getbool (input):
	inp = str(input)
	if inp.lower() not in _booleanStates:
		raise ValueError, 'Not a boolean: %s' % inp
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
		getItem() which searches recursively in self.data for rightmost key value.
	"""
	
	_booleanStates = _booleanStates
	supportedTypes = supportedTypes
	
	def __init__(self):
		self.data = {}
		
	def getItem(self, keys):
		"""Search recursively for item by given keys
			Input: (str) keys Example: t.getItem('key1', 'key2', 'key3')
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
		return getstr(self.getItem(keys))
	
	def getstring (self, *keys):
		return getstring(self.getItem(keys))
	
	def getint (self, *keys):
		return getint(self.getItem(keys))
	
	def gethex (self, *keys):
		return gethex(self.getItem(keys))
	
	def getoct (self, *keys):
		return getoct(self.getItem(keys))
	
	def getdec (self, *keys):
		return getdec(self.getItem(keys))
	
	def getbool (self, *keys):
		return getbool(self.getItem(keys))
	
	def getTemplate (self, *keys):
		return getTemplate(self.getItem(keys))
