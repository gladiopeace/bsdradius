"""
Functions and methods for casting types from string to
other types.
Contains functions and class for inheritance in other classes.
Supported types: 'str', 'string', 'int', 'hex', 'oct', 'dec', 'bool', 'Template'
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/webstuff/tags/release20061229_v_1_0_0/webstuff/Typecast.py $
# Author:		$Author: valdiic $
# File version:	$Revision: 259 $
# Last changes:	$Date: 2006-10-04 14:55:12 +0300 (Tr, 04 Okt 2006) $


# for typecasting to Template
from string import Template
from decimal import Decimal
import os.path

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

def getfloat (input):
	return float(input)

def getTemplate (input):
	return Template(str(input))
	
def getUnicode (input):
	return unicode(input)
	
def getDecimal (input):
	return Decimal(str(input))

def getPath (input):
	input = os.path.expandvars(input)
	return os.path.abspath(input)



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
		# this is for compatibility of UserDict derived classes
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
			# get item of first level
			if tmp is None:
				try:
					# for classes derived from dict
					tmp = self[key]
				except:
					try:
						# for classes derived from UserDict
						tmp = self.data[key]
					except:
						err = 'Could not find item "%s". ' % key
						err += 'Please use class instance derived from dict or UserDict classes'
						raise TypeError(err)
					
			# get item of further dictionary cascade levels
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
	
	def getUnicode (self, *keys):
		return getUnicode(self._getItem(keys))
		
	def getDecimal (self, *keys):
		return getDecimal(self._getItem(keys))
	
	def getPath (self, *keys):
		return getPath(self._getItem(keys))

		
# holds references to all supported typecast methods
typecastMethods = {
	'str' : getstr,
	'string' : getstring,
	'int' : getint,
	'hex' : gethex,
	'oct' : getoct,
	'dec' : getdec,
	'bool' : getbool,
	'float' : getfloat,
	'Template' : getTemplate,
	'unicode' : getUnicode,
	'decimal' : getDecimal,
	'path' : getPath,
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
	'unicode' : Typecast.getUnicode,
	'decimal' : Typecast.getDecimal,
	'path' : Typecast.getPath,
}
