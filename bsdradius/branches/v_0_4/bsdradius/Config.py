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
Data Tech Labs configuration file module
Used to extarct and store data from configuration file
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_4/bsdradius/Config.py $
# Author:		$Author: valts $
# File version:	$Revision: 201 $
# Last changes:	$Date: 2006-04-04 17:22:11 +0300 (Ot, 04 Apr 2006) $



# modules
from bsdradius import logger
from bsdradius.logger import *
from bsdradius.Typecast import Typecast
from bsdradius.configDefaults import *
from bsdradius import version

# standard modules
from UserDict import UserDict
from ConfigParser import SafeConfigParser
from optparse import OptionParser
import re



class Config(UserDict, Typecast):
	"""Class for configuration file and CLI configuration data handling.
		Class instances may be used as dictionary objects to gain access
		to attributes. All parsed attributes are stored in attribute "data".
	"""

	def __init__(self, defaults = {}, types = {}):
		"""Constructor.
			If any filenames given tries to parse them
			Input: (string) filename. You can pass pultiple file names
				(dict) defaults: {'section': {'attrib': 'value'}},
				(dict) types: {'section': {'attrib': 'type'}};
				See Typecast.py for supported types.
			Output: (Config) class instance
		"""
		UserDict.__init__(self) # create self.data
		self.cliParser = None # we don't need CLI parser by default
		self.fileParser = SafeConfigParser()
		self._types = types
		self._defaults = defaults
		
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
		
		# store parsed default values
		self.storeParsedFileItems()
	
	
	
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



	def setUpCliParser(self):
		"""Prepare CLI parser for operation
			Input: none
			Output: none
		"""
		# set up CLI parser only once
		if self.cliParser:
			return
		
		debug ('Preparing CLI parser')
		cliDefaults = {}
		cliDefaults['PATHS'] = {}
		cliDefaults['SERVER'] = {}
		cliDefaults['PATHS']['config_file'] = self._defaults['PATHS']['config_file']
		cliDefaults['SERVER']['foreground'] = self._defaults['SERVER']['foreground']
		cliDefaults['SERVER']['no_threads'] = self._defaults['SERVER']['no_threads']
		cliDefaults['SERVER']['log_to_screen'] = self._defaults['SERVER']['log_to_screen']
		cliDefaults['SERVER']['debug_mode'] = self._defaults['SERVER']['debug_mode']
		cliDefaults['SERVER']['log_client'] = self._defaults['SERVER']['log_client']
		self._cliDefaults = cliDefaults
		
		usage = "usage: %prog [options]"
		self.cliParser = OptionParser(usage=usage)
		parser = self.cliParser
		parser.version = version
		
		# set defaults in parser instance
		parserDefaults = {}
		for section, options in cliDefaults.iteritems():
			for option, value in options.iteritems():
				parserDefaults[option] = value
		parser.set_defaults(**parserDefaults)
		
		# set up available options
		parser.add_option("-v", "--version", action="version",
			help = "Print version info")
		parser.add_option("-c", "--configuration-file",
			action="store", dest="config_file",
			help="Path to configuration file", metavar="FILE")
		parser.add_option("-f", "--foreground",
			action="store_true", dest="foreground",
			help="Run server in foreground")
		parser.add_option("-n", "--no-threads",
			action="store_true", dest="no_threads",
			help="Run server with only one packet processing thread")
		parser.add_option("-s", "--log-to-screen",
			action="store_true", dest="log_to_screen",
			help="Print all log messages to screen (stdout) only")
		parser.add_option("-d", "--debug",
			action="store_true", dest="debug_mode",
			help="Run server in debugging mode. Implifies: -f -n -s")
		parser.add_option("-l", "--log-client",
			action="store", dest="log_client",
			help="Print log messages regarding only one server client.",
			metavar="ADDRESS")
	
	
	
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
		self.setUpCliParser()
		
		(options, args) = self.cliParser.parse_args()
		# store parsed options
		for section, tokens in self._cliDefaults.iteritems():
			for key, defaultValue in tokens.iteritems():
				newValue = str(getattr(options, key))
				if newValue != defaultValue:
					self[section][key] = newValue
		
		self.typecastOptions()
	
	

	def applyConfig(self):
		"""Apply configuration 
		"""
		# apply options
		if self['SERVER']['debug_mode']:
			self['SERVER']['foreground'] = True
			self['SERVER']['no_threads'] = True
			self['SERVER']['log_to_screen'] = True
		if self['SERVER']['log_to_screen']:
			self['SERVER']['log_to_file'] = False
			logger.logToScreen = True
		if self['SERVER']['log_client']:
			# restrict all threads from logger
			info ('--- Enabling threads logging restrictions ---')
			logger.restrictThreads = True
			# add this (main) thread to unrestricted threads to allow print log messages
			logger.addUnrestrictedThread()



	def __str__(self):
		"""Print configuration parameters nicely in maximum readable way
			If you need it unreadable but easier for parsing use __repr__ instead.
			Input: none
			Output: (string) formatted contents of configuration data
		"""
		ret = ""
		for section, options in self.iteritems():
			ret += "%s:\n" % section
			for option, value in options.iteritems():
				ret += "  %s: %s\n" % (option, value)
		return ret



# contains main configuration data
main_config = Config(defaultOptions, defaultTypes)
# successfully read configuration files
parsedFiles = []
def readMainConf():
	"""Read main configuration data
		Input: none
		Output: none
	"""
	global main_config
	# read path to config file from CLI
	main_config.readCli()
	# apply config to enable/disable logging
	main_config.applyConfig()
	
	# read config file
	info ('--- Reading configuration ---')
	confFilePath = main_config['PATHS']['config_file']
	parsedFiles = main_config.readFiles(confFilePath)
	# check if all neccessary files are read
	if confFilePath not in parsedFiles:
		from bsdradius import misc
		misc.quit("Can not read required configuration files", 1)
	
	# read CLI again to overwrite options from file
	main_config.readCli()
	# apply config to avoid overwritten values from config file
	main_config.applyConfig()
