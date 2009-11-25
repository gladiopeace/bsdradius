"""
Data Tech Labs configuration file module
Used to extarct and store data from configuration file
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/webstuff/tags/release20061229_v_1_0_0/webstuff/Config.py $
# Author:		$Author: valts $
# File version:	$Revision: 70 $
# Last changes:	$Date: 2006-08-24 21:47:42 +0300 (Ce, 24 Aug 2006) $



# modules
import os, sys
from logger import *
from Typecast import Typecast
#from configDefaults import *
from webstuff_version import fullVersion

# standard modules
from ConfigParser import SafeConfigParser
from optparse import OptionParser
import re
from types import *
from string import Template



class Config(dict, Typecast):
	"""Class for configuration file and CLI configuration data handling.
		Class instances may be used as dictionary objects to gain access
		to attributes. All parsed attributes are stored in attribute "data".
	"""

	def __init__(self, defaults = {}, types = {}, cliDefaults = {},
		usageMessage = "usage: %prog [options]", softVersion = fullVersion,
		softDescription = "", softwareName = os.path.basename(sys.argv[0]), defaultType = 'str'):
		"""Constructor.
			If any filenames given tries to parse them
			Input: (string) filename. You can pass pultiple file names
				(dict) defaults: {'section': {'attrib': 'value'}},
				(dict) types: {'section': {'attrib': 'type'}};
				(dict) cli defaults (the same format as for configfile defaults;
				(string) usage message;
				(string) software version string (default: webstuff lib version);
				(string) software brief description;
				(string) software name (default: executed file name)
				See Typecast.py for supported types.
			Output: (Config) class instance
		"""
		self.cliParser = None # we don't need CLI parser by default
		self.fileParser = SafeConfigParser()
		self._types = types
		self._defaults = defaults
		self._cliDefaults = cliDefaults
		self._usageMessage = usageMessage
		self._softVersion = softVersion
		self._softDescription = softDescription
		self._softwareName = softwareName
		self._defaultType = defaultType
		
		# set default values in config file parser instance
		self.setDefaults(defaults)
		# store parsed default values
		self.storeParsedFileItems()
	
	
	
	def setDefaults(self, defaults):
		"""Set default values in config parser
		"""
		# set defaults in configfile parser
		fileParser = self.fileParser
		for (section, attributes) in defaults.items():
			section = str(section)
			if not fileParser.has_section(section):
				fileParser.add_section(section)
			for (key, value) in attributes.items():
				key = str(key)
				value = str(value)
				key = fileParser.optionxform(key)
				fileParser.set(section, key, value)
	
	
	
	def storeParsedFileItems(self):
		"""Parse values form parser instance and store in this class' instance
			Input: none
			Output: none
		"""
		# store all interpolated attributes in self.data
		parser = self.fileParser
		for section in parser.sections():
			# add missing sections
			if section not in self:
				self[section] = {}
			for tokens in parser.items(section):
				self[section][tokens[0]] = tokens[1]
		
		self.typecastOptions()
	
	
	
	def typecastOptions(self):
		# try to typecast attributes
		castMethods = self.typecastMethods # get names of all objects in Typecast module
		for section, options in self._types.items():
			for option, type in options.items():
				if type in castMethods:
					castMethod = castMethods[type] # get reference to casting method
					self[section][option] = castMethod(self, section, option)
				else:
					raise NotImplementedError, "Typecast to %s not implemented" % type



	def setUpCliParser(self, cliDefaults = None, usageMessage = None,
		softVersion = None, softDescription = None, softwareName = None, force = False):
		"""Prepare CLI parser for operation
			Input: (dict) cli defaults (the same format as for configfile defaults;
				(string) usage message;
				(string) software version string (default: webstuff lib version);
				(string) software brief description;
				(string) software name (default: executed file name)
				(bool) set to True to invoke new parser even when it has been done
					earlier.
				See Typecast.py for supported types.
				NOTICE: these attributes override ones you passed to constructor.
			Output: none
		"""
		# set up CLI parser only once
		if not force and self.cliParser:
			return
			
		# override any previous attributes
		if cliDefaults != None:
			self._cliDefaults = cliDefaults
		if usageMessage != None:
			self._usageMessage = usageMessage
		if softVersion != None:
			self._softVersion = softVersion
		if softDescription != None:
			self._softDescription = softDescription
		if softwareName != None:
			self._softwareName = softwareName
		
		debug ('Preparing CLI parser')
		self.cliParser = OptionParser(
			usage = self._usageMessage,
			version = self._softVersion,
			description = self._softDescription,
			prog = self._softwareName
		)
		parser = self.cliParser
		
		# set defaults in parser instance
		parserDefaults = {}
		for section, options in self._cliDefaults.iteritems():
			for option, value in options.iteritems():
				parserDefaults[option] = value
		parser.set_defaults(**parserDefaults)
		
		return parser
	
	
	
	def readFiles(self, filenames = None):
		"""Parse config file and store result
			Overrides read method in SafeConfigParser. Adds additional typecasting support
			Input: (string or list) filename(s)
			Output: (list) list of parsed configuration files
		"""
		parsedFiles = []
		if not filenames:
			error ('No files to read')
			return parsedFiles
		
		# read files
		debug ('Reading config files: ', filenames)
		parsedFiles = self.fileParser.read(filenames)
		if not parsedFiles:
			error ('No config files (%s) read' % str(filenames))
		else:
			debug ('Files read successfully: ', parsedFiles)
		
		self.storeParsedFileItems()
		return parsedFiles
	
	
	
	def readCli(self):
		"""Parse command line attributes and apply them
			Input: none
			Output: none
		"""
		debug ('Reading command line attributes')
			
		# prepare parser and get attributes from CLI
		self.setUpCliParser()
		(options, args) = self.cliParser.parse_args()
		# store parsed options
		for section, tokens in self._cliDefaults.iteritems():
			for key, defaultValue in tokens.iteritems():
				newValue = str(getattr(options, key))
				if newValue != defaultValue:
					self[section][key] = newValue
		# store typecasted attributes only
		self.typecastOptions()
	
	

	def applyConfig(self):
		"""Apply configuration.
			This is ABSTRACT function. You should define it in derived class to
			change various configuration aoptions depending on others.
		"""
		raise notImplementedError, "you MUST define applyConfig() in derived class to use it"



	def __str__(self):
		"""Print configuration parameters nicely in maximum readable way
			If you need it unreadable but easier for parsing use __repr__ instead.
			Input: none
			Output: (string) formatted contents of configuration data
		"""
		ret = ""
		for section, options in self.iteritems():
			ret += "%r:\n" % section
			for option, value in options.iteritems():
				ret += "  %r: %r\n" % (option, value)
		return ret



class PhpConfigParseError(Exception):
	pass

class PhpConfig(Config):
	"""Class for parsing PHP configuration files
	"""
	def __init__(self, safeInterpolation = False, *t_params, **d_params):
		"""Constructor.
			Input: (bool) set to true to avoid raising exceptions when php
				variable names in attribute values could not be replaced with
				values of already existing attributes
			Output: None
			Pass all other received parameters to constructor of base class.
		"""
		self.safeInterpolation = safeInterpolation
		Config.__init__(self, *t_params, **d_params)
	
	
	def setDefaults(self, defaults):
		"""Override method with the same name in bas class.
			It is not neccessary to touch ini file parser at the moment.
		"""
		self.update(self._defaults)
	
	
	def storeParsedFileItems(self):
		"""Since we don't use external parser there just hop to typecasting
			attributes.
		"""
		self._parsePhpAttributes()
		self.typecastOptions()
	
	
	def readFiles(self, filenames = []):
		"""Parse php file and export it's variables. Raises exception on error
			Input: (list or string) pass string for one file name, pass list for
				multiple files
			Output: (list) list of parsed files
		"""
		parsedFiles = [] # list of successfully parsed files
		# check and convert filenames to something usable
		if not filenames:
			error ('No files to read')
			return parsedFiles
		if isinstance(filenames, StringTypes):
			filenames = [filenames]
		if not isinstance(filenames, ListType):
			filenames = list(filenames)
			
		debug ('Reading config files: ', filenames)
		for file in filenames:
			try:
				fh = open(file, 'r')
			except:
				continue
			self._parsePhpFile(fh)
			fh.close()
			parsedFiles.append(file)
		
		# check parsing results and store parsed items
		if not parsedFiles:
			error ('No config files (%s) read' % str(filenames))
		else:
			debug ('Files read successfully: ', parsedFiles)
		
		self.storeParsedFileItems()
		return parsedFiles



	# represents multiline php comments: /*.....*/
	_multilinePhpCommentRegexp = re.compile(r'/\*(.*?)\*/', re.DOTALL)
	# represents single line php comments: //....
	_singleLinePhpCommentRegexp = re.compile(r'//.*\n')
	# matches whitespace characters at the beginning and end of line in multiline string
	_stripRegexp = re.compile(r'^\s*|\s*\n', re.MULTILINE)
	# matches php statement: $.....;
	_phpStatementRegexp = re.compile(r'\$(.*?);', re.DOTALL)
	# matches one single or double quote at the beginning or end of string
	_quoteStripRegexp = re.compile(r'^\s*[\'"]?|[\'"]?\s*$')
	def _parsePhpFile(self, fh):
		"""Parse config file which actually is simple php file.	Raises
			exception on error.
			Input: (file) file like object
			Output: none
		"""
		# store all parsed attributes in section called "PHPFILE"
		if 'PHPFILE' not in self:
			self['PHPFILE'] = {}
		sect = self['PHPFILE']
		
		# Read all the file into the memory.
		# It is needed to cut out php's bloody multiline comments.
		fileContents = fh.read()
		
		# cut multiline comments
		fileContents = PhpConfig._multilinePhpCommentRegexp.sub('', fileContents)
		fileContents = PhpConfig._singleLinePhpCommentRegexp.sub('', fileContents)
		fileContents = PhpConfig._stripRegexp.sub('', fileContents)
		phpStatements = PhpConfig._phpStatementRegexp.findall(fileContents)
		
		# read line by line
		for statement in phpStatements:
			# split statements by assignment operator
			tokens = statement.split('=', 1)
			if len(tokens) != 2:
				continue
			# get varible name and value without surrounding whitespace and quotes
			var = PhpConfig._quoteStripRegexp.sub('', tokens[0])
			value = PhpConfig._quoteStripRegexp.sub('', tokens[1])
			
			sect[var] = value
	
	
	def _parsePhpAttributes(self):
		"""Parse php config attributes. Parses arrays, dictionaries and
			interpolates php variable names.
			Input: none
			Output: none
		"""
		sect = self['PHPFILE']
		for attr, value in sect.items():
			# interpolate php variables
			# perform recursive operation
			try:
				if self.safeInterpolation:
					value = RecursiveTemplate(value).safe_substitute(sect)
				else:
					value = RecursiveTemplate(value).substitute(sect)
			except RuntimeError, err:
				if str(err) == 'maximum recursion depth exceeded':
					errmsg = 'Could not parse configuration file. '
					errmsg += 'Probably there are recursive attributes in configuration file'
					raise PhpConfigParseError(errmsg)
				else:
					raise
				
			
			# parse lists and dicts
			value = self._parsePhpArray(value)
			value = self._phpArrayToDict(value)
			
			sect[attr] = value
	
	
	# represents syntax of php array definition: array(....)
	_phpArrayRegexp = re.compile(r'^array\s*\(|\)$')
	# matches whitespace characters around commas
	_spaceCommasRegexp = re.compile(r'\s*,\s*')
	@classmethod
	def _parsePhpArray(cls, value):
		"""Parse config sfile strings which are defined as array for php.
			Make them as list for python!
			NOTE: This method is not able to parse multidimensional array definitions
			Input: (string) parameter value from config file
			Output: (mixed) array of values if parsed as an array or the same string if parsing is not neccessary
		"""
		# return unchanged value if it is not possible to parse it
		if not isinstance(value, StringTypes):
			return value
		# convert array into list
		if cls._phpArrayRegexp.match(value):
			value = cls._phpArrayRegexp.sub ('', value) # remove leading "array(" and trailing ")"
			value = cls._spaceCommasRegexp.sub (',', value) # remove whitespace characters around commas
			value = value.split (',')	# split string by commas and put it in list
		return value
	
	
	
	@classmethod
	def _phpArrayToDict(cls, array):
		"""Parse raay elements to dictionary key: value pairs
			Takes each array element and looks for strings like 'key => value'
			If all array elements are in this format then array is converted to 
			dictionary
			Input: (list) array of strings
			Output: (mixed) the same array or already parsed dictionary
		"""
		# return unchanged value if it is not possible to parse it
		if not isinstance(array, ListType):
			return array
		
		ret = {}
		# scan all items in list and build up dictionary
		# return unchanged array if at least one item parsing fails
		for arrayStr in array:
			tokens = arrayStr.split('=>', 1)
			if len(tokens) != 2:
				return array
			else:
				key = cls._quoteStripRegexp.sub('', tokens[0])
				value = cls._quoteStripRegexp.sub('', tokens[1])
				ret[key] = value
		
		# return parsed dictionary
		return ret



class RecursiveTemplate(Template):
	"""This class is for parsing string templates which variables may refer
		to other variables and so on. This is derived class of string.Template
	"""
	def __init__(self, template):
		Template.__init__(self, template)
		
	def substitute(self, *args, **kws):
		# operate with strings only.
		if not isinstance(self.template, StringTypes):
			return self.template
		
		if len(args) > 1:
			raise TypeError('Too many positional arguments')
		if not args:
			mapping = kws
		elif kws:
			mapping = _multimap(kws, args[0])
		else:
			mapping = args[0]
		# Helper function for .sub()
		def convert(mo):
			# Check the most common path first.
			named = mo.group('named') or mo.group('braced')
			if named is not None:
				val = mapping[named]
				# fill template recursively
				# it is needed when one template has other template as mapped value
				matched = self.pattern.match(val)
				if matched and (matched.group('named') or matched.group('braced')):
					val = RecursiveTemplate(val).substitute(mapping)
				# We use this idiom instead of str() because the latter will
				# fail if val is a Unicode containing non-ASCII characters.
				return '%s' % val
			if mo.group('escaped') is not None:
				return self.delimiter
			if mo.group('invalid') is not None:
				self._invalid(mo)
			raise ValueError('Unrecognized named group in pattern',
							 self.pattern)
		return self.pattern.sub(convert, self.template)
		
	def safe_substitute(self, *args, **kws):
		# operate with strings only.
		if not isinstance(self.template, StringTypes):
			return self.template
		
		if len(args) > 1:
			raise TypeError('Too many positional arguments')
		if not args:
			mapping = kws
		elif kws:
			mapping = _multimap(kws, args[0])
		else:
			mapping = args[0]
		# Helper function for .sub()
		def convert(mo):
			named = mo.group('named')
			if named is not None:
				try:
					# fill template recursively
					# it is needed when one template has other template as mapped value
					matched = self.pattern.match(val)
					if matched and matched.group('named'):
						val = RecursiveTemplate(val).substitute(mapping)
					# We use this idiom instead of str() because the latter
					# will fail if val is a Unicode containing non-ASCII
					return '%s' % mapping[named]
				except KeyError:
					return self.delimiter + named
			braced = mo.group('braced')
			if braced is not None:
				try:
					# fill template recursively
					# it is needed when one template has other template as mapped value
					matched = self.pattern.match(val)
					if matched and matched.group('braced'):
						val = RecursiveTemplate(val).substitute(mapping)
					return '%s' % mapping[braced]
				except KeyError:
					return self.delimiter + '{' + braced + '}'
			if mo.group('escaped') is not None:
				return self.delimiter
			if mo.group('invalid') is not None:
				return self.delimiter
			raise ValueError('Unrecognized named group in pattern',
							 self.pattern)
		return self.pattern.sub(convert, self.template)
