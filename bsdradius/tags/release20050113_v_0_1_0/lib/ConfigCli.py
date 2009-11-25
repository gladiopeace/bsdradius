"""
This module contains class for reading configuration
parameters from command line
"""


from UserDict import UserDict
from logging import *
from optparse import OptionParser
from configDefaults import defaultOptions
import Config



class ConfigCli(UserDict):
	"""Class for reading configuration data from command line
	"""
	
	def __init__(self, version = ''):
		"""Constructor
			Input: none
			Output: (ConfigCli) class instance
		"""
		UserDict.__init__(self)
		
		defaults = {}
#		defaults['PATHS'] = {}
#		defaults['SERVER'] = {}
		defaults['config_file'] = defaultOptions['PATHS']['config_file']
		defaults['foreground'] = defaultOptions['SERVER']['foreground']
		defaults['no_threads'] = defaultOptions['SERVER']['no_threads']
		defaults['log_to_screen'] = defaultOptions['SERVER']['log_to_screen']
		defaults['debug_mode'] = defaultOptions['SERVER']['debug_mode']
		defaults['log_client'] = defaultOptions['SERVER']['log_client']
		self._defaults = defaults
		
		usage = "usage: %prog [options]"
		parser = OptionParser(usage=usage)
		parser.version = version
		parser.set_defaults(**defaults)
		
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
		self._parser = parser
		
		# read arguments
		self.read()



	def read(self):
		"""Read and store options.
			Input: (none)
			Output: (none)
		"""
		(options, args) = self._parser.parse_args()
		# store parsed options
		for section, tokens in defaultOptions.items():
			for key, defaultValue in tokens.items():
				if hasattr(options, key):
					newValue = str(getattr(options, key))
					if newValue != defaultValue:
						if section not in self:
							self[section] = {}
						self[section][key] = newValue
		
		
		
	def applyOptions(self):
		"""Apply local options to main configuration
			Input: none
			Output: none
		"""
		for section, tokens in self.items():
			for key, value in tokens.items():
				Config.main_config[section][key] = value
		if Config.main_config['SERVER']['log_to_screen']:
			Config.main_config['SERVER']['log_to_file'] = False
	


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
