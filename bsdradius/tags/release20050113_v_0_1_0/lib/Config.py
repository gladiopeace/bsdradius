"""
Data Tech Labs configuration file module
Used to extarct and store data from configuration file
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/tags/release20050113_v_0_1_0/lib/Config.py $
# Author:		$Author: valts $
# File version:	$Revision: 118 $
# Last changes:	$Date: 2006-01-12 13:31:41 +0200 (Ce, 12 Jan 2006) $



# modules
from logging import *
from Typecast import Typecast
from configDefaults import *

# standard modules
from UserDict import UserDict
from ConfigParser import SafeConfigParser
import re



class Config(UserDict, Typecast, SafeConfigParser):
	"""Class for configuration file handling
		Class instances may be used as dictionary objects to gain access
		to attributes. All parsed attributes are stored in attribute "data".
		Since UserDict is first class in inheritance instances of this class will
		act more like dictionaries then SafeConfigParser instances.
		Methods overriden by UserDict: items, get
	"""

	def __init__(self, defaults = {}, types = {}):
		"""Constructor.
			If any filenames given tries to parse them
			Input: (string) filename. You can pass pultiple file names
				(dict) defaults: {'section': {'attrib': 'value'}},
				(dict) types: {'section': {'attrib': 'type'}}; types supported are:
					int, str, string, float, bool; default: string
			Output: (Config) class instance
		"""
		# call base class constructors
		SafeConfigParser.__init__(self)
		#UserDict.__init__(self)
		
		### IMPORTANT!!! Link self.data to self._sections to provide connectivity between UserDict and SafeConfigParser
		self.data = self._sections
		self._types = types
		self._defaultOptions = defaults
		self._rawData = {}
		
		for (section, attributes) in defaults.items():
			section = str(section)
			if not self.has_section(section):
				self.add_section(section)
			for (key, value) in attributes.items():
				key = self.optionxform(str(key))
				self.set(section, key, value)
	
	
	
	def add_section(self, section):
		"""Adds new section and inserts section name in it's hidden
			attribute: __name__
			Input: (string) section name
			Output: none
		"""
		SafeConfigParser.add_section(self, section)
		self[section]['__name__'] = section
	
	
	
	def read(self, filenames = None):
		"""Parse config file and store result
			Overrides read method in SafeConfigParser. Adds additional typecasting support
			Input: (string or list) filename(s)
			Output: (list) list of parsed configuration files
		"""
		# read something only when asked for
		# to just parse defaults use this method passing no filenames
		readFiles = []
		# Because of a little bit stupid ConfigParser who thinks that all config data
		# must be stored as strings let it be so.
		for section, tokens in self.items():
			for key, value in tokens.items():
				self[section][key] = str(value)
			
		if filenames:
			# read file and return False if failed
			debug ('Reading config files: ', filenames)
			readFiles = SafeConfigParser.read(self, filenames)
			if not readFiles:
				error ('No config files (%s) read ' % str(filenames))
			else:
				debug ('Files read successfully: ', readFiles)
			
		# Store fully parsed and raw values seperately.
		# Actually I don't know where raw values would be usable. :)
		tmp = {}
		for section in self.keys():
			tmp[section] = {}
			for key, value in self.configItems(section): # use parsed values
				tmp[section][key] = value
			self._rawData[section] = {}
			for key, value in self[section].items(): # use raw values
				self._rawData[section][key] = value
		self._sections = tmp
		self.data = self._sections
		
		# try to typecast attributes
		sections = self.sections()
		castMethods = Typecast.__dict__ # get names of all objects in Typecast module
		for section in self._types:
			for option, type in self._types[section].items():
				if type in Typecast.supportedTypes:
					castMethod = castMethods['get'+type] # get reference to casting method
					self[section][option] = castMethod(self, section, option)
				else:
					raise NotImplementedError, "Typecast to %s not implemented" % type
		
		return readFiles
				
				
				
	def configItems(self, section):
		"""Workaround to provide access to SafeConfigParser.items()
			Input: (str) section name
			Output: (list) tuples of option, value pairs
		"""
		return SafeConfigParser.items(self, section)
		


	def __str__(self):
		"""Print configuration parameters nicely in maximum readable way
			If you need it unreadable but easier for parsing use __repr__ instead.
			Input: none
			Output: (string) formatted contents of configuration data
		"""
		ret = ""
		for section in self.keys():
			ret += "%s:\n" % section
			for option, value in self[section].items():
				if option != '__name__':
					ret += "  %s: %s\n" % (option, value)
		return ret



# contains main configuration data
main_config = Config(defaultOptions, defaultTypes)
# successfully read configuration files
readFiles = []
# parse defaults. It is neccessary to get default config file path
readFiles = main_config.read('')
debug ('Default Config:')
debug(main_config)
# Path to config file
configFiles = [main_config['PATHS']['config_file']]
