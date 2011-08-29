# dictionary.py
#
# Copyright 2002 Wichert Akkerman <wichert@wiggy.net>

"""RADIUS dictionary

RADIUS uses dictionaries to define the attributes that can
be used in packets. The Dictionary class stores the attribute
definitions from one or more dictionary files.

Dictionary files are textfiles with one command per line.
Comments are specified by starting with a # character, and empty
lines are ignored.

The commands supported are::

  ATTRIBUTE <attribute> <code> <type> [<vendor>]
  specify an attribute and its type

  VALUE <attribute> <valuename> <value>
  specify a value attribute

  VENDOR <name> <id>
  specify a vendor ID

  BEGIN-VENDOR <vendorname>
  begin definition of vendor attributes

  END-VENDOR <vendorname>
  end definition of vendor attributes


The datatypes currently supported are::

  string   - ASCII string
  ipaddr   - IPv4 address
  integer  - 32 bits signed number
  date     - 32 bits UNIX timestamp
  octets   - arbitrary binary data
  abinary  - ASCII encoded binary data
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_6/bsdradius/pyrad/dictionary.py $
# Author:		$Author: valts $
# File version:	$Revision: 230 $
# Last changes:	$Date: 2006-06-08 17:17:21 +0300 (Ce, 08 Jūn 2006) $


__docformat__	= "epytext en"

import os.path
import sys
from exceptions import Exception
import re

import bidict, tools




class ParseError(Exception):
	"""Dictionary parser exceptions.
	"""



class Attribute:
	def __init__(self, name, code, datatype, vendor = "", values = {}, encryptMethod = 0):
		assert datatype in ("string", "ipaddr", "integer", "date",
					"octets", "abinary", "ipv6addr", "ifid")
		self.name = name
		self.code = code
		self.type = datatype
		self.vendor = vendor
		self.encryptMethod = encryptMethod
		self.values = bidict.BiDict()
		for (key,value) in values.items():
			self.values.Add(key, value)
			
	def __str__(self):
		ret =  "  name: " + str(self.name) + "\n"
		ret += "  code: " + str(self.code) + "\n"
		ret += "  type: " + str(self.type) + "\n"
		ret += "  encrypt: " + str(self.encryptMethod) + "\n"
		ret += "  vendor: " + str(self.vendor) + "\n"
		ret += "  values: " + str(self.values)
		return ret



class Dictionary:
	"""RADIUS dictionary class

	This class stores all information about vendors, attributes and their
	values as defined in RADIUS dictionary files.

	@ivar vendors:    bidict mapping vendor name to vendor code
	@type vendors:    bidict
	@ivar attrindex:  bidict mapping 
	@type attrindex:  bidict
	@ivar attributes: bidict mapping attribute name to attribute class
	@type attributes: bidict
	"""
	
	# this regexp matches encrypt method flag of attribute
	encryptMethodRegexp = re.compile(r'^.*?encrypt=(\d+).*$')
	
	# supported datatypes
	datatypes = ["string", "ipaddr", "integer", "date",
			"octets", "abinary", "ipv6addr", "ifid"]



	def __init__(self, dict = None, *dicts):
		"""
		@param dict:  dictionary file to read
		@type dict:   string
		@param dicts: list of dictionary files to read
		@type dicts:  sequence of strings
		"""
		self.vendors = bidict.BiDict()
		self.vendors.Add("", 0)
		self.attrindex = bidict.BiDict()
		self.attributes = {}

		if dict:
			self.ReadDictionary(dict)
			#for key, value in self attributes.items():
			#	print ""
			self.ReadDictionary(dict, True, True)

		for i in dicts:
			self.ReadDictionary(i)
			self.ReadDictionary(i, True, True)



	def __getitem__(self, key):
		return self.attributes[key]



	def has_key(self, key):
		return self.attributes.has_key(key)


	
	def items(self):
		return self.attributes.items()



	def __ParseAttribute(self, state, tokens):
		if not len(tokens) in [4,5]:
			raise ParseError, "Incorrect number of tokens for attribute definition"
		
		# get vendor name and detect if attribute has to be encrypted
		vendor = state["vendor"]
		encryptMethod = 0
		if len(tokens) >= 5:
			# look for 'encrypt=xx'
			encryptMethodMatched = self.encryptMethodRegexp.match(tokens[4])
			if encryptMethodMatched:
				encryptMethod = int(encryptMethodMatched.group(1))
			# look for vendor
			else:
				vendor = tokens[4]
				if not self.vendors.HasForward(vendor):
					raise ParseError, "Unknown vendor: " + vendor

		(attribute,code,datatype) = tokens[1:4]
		
		# convert code to integer
		# code may be either in base 10 or base 16
		try:
			code = int(code, 10)
		except:
			try:
				code = int(code, 16)
			except:
				raise
		
		if not datatype in self.datatypes:
			raise ParseError, "Illegal type: %s" % datatype

		if vendor:
			key = (self.vendors.GetForward(vendor),code)
		else:
			key = code

		self.attrindex.Add(attribute, key)
		self.attributes[attribute] = Attribute(attribute, code, datatype, vendor, encryptMethod = encryptMethod)



	def __ParseValue(self, state, tokens):
		if len(tokens) != 4:
			raise ParseError, "Incorrect number of tokens for attribute definition"

		(attr, key, value) = tokens[1:]

		try:
			adef = self.attributes[attr]
		except KeyError:
			raise ParseError, "Value defined for unknown attribute " + attr

		if adef.type == "integer":
			value = int(value)
		value = tools.EncodeAttr(adef.type, value)
		self.attributes[attr].values.Add(key, value)



	def __ParseVendor(self, state, tokens):
		if len(tokens) != 3:
			raise ParseError, "Incorrect number of tokens for vendor definition"

		(vendorname,vendor) = tokens[1:]
		self.vendors.Add(vendorname, int(vendor))
	


	def __ParseBeginVendor(self, state, tokens):
		if len(tokens) != 2:
			raise ParseError, "Incorrect number of tokens for begin-vendor statement"

		vendor = tokens[1]

		if not self.vendors.HasForward(vendor):
			raise ParseError, "Unknown vendor %s in begin-vendor statement" % vendor

		state["vendor"] = vendor



	def __ParseEndVendor(self, state, tokens):
		if len(tokens) != 2:
			raise ParseError, "Incorrect number of tokens for end-vendor statement"

		vendor = tokens[1]

		if state["vendor"] != vendor:
			raise ParseError, "Ending non-open vendor" + vendor

		state["vendor"] = ""



	def __ParseInclude(self, state, tokens, file, parseValues):
		if len(tokens) != 2:
			raise ParseError, "Incorrect number of tokens for $INCLUDE statement"
		
		# get dictionary file name
		dictFile = tokens[1]
		
		# if dictionary file name doesn't begin with '/',
		# consider it relative to current dictionary's directory
		if dictFile[0] != '/':
			fileDir = os.path.dirname(file)
			dictFile = fileDir + '/' + dictFile
		
		self.ReadDictionary(dictFile, parseValues, parseInclude = False)



	def ReadDictionary(self, file, parseValues = False, parseInclude = True):
		"""Parse a dictionary file

		Reads a RADIUS dictionary file and merges its contents into the
		class instance.

		@param file: Name of dictionary file to parse
		@type file:  string
		@param parseValues: set to true to parse values
		@type parseValues:  bool
		"""
		fd = open(file, "rt")
		state = {}
		state["vendor"] = ""

		for line in fd:
			line = line.split("#", 1)[0].strip()

			tokens = line.split()
			if not tokens:
				continue

			if tokens[0] == "ATTRIBUTE":
				self.__ParseAttribute(state, tokens)
			elif tokens[0] == "VALUE" and parseValues:
				self.__ParseValue(state, tokens)
			elif tokens[0] == "VENDOR":
				self.__ParseVendor(state, tokens)
			elif tokens[0] == "BEGIN-VENDOR":
				self.__ParseBeginVendor(state, tokens)
			elif tokens[0] == "END-VENDOR":
				self.__ParseEndVendor(state, tokens)
			elif tokens[0] == "$INCLUDE" and parseInclude:
				self.__ParseInclude(state, tokens, file, parseValues)
				
		fd.close()
		
		
		
	def __str__(self):
		"""Print human readable dictionary contents
			Input: none
			Output: (string) formatted contents
		"""
		ret = ''
		for key, attr in self.attributes.items():
			ret += """%s:\n%s\n""" % (key, attr)
		
		return ret
