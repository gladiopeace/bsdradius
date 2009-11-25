"""
This module holds useful functions for operation with internal
BSD Radius server modules.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/tags/release20050113_v_0_1_0/lib/modules.py $
# Author:		$Author: valts $
# File version:	$Revision: 120 $
# Last changes:	$Date: 2006-01-12 15:06:28 +0200 (Ce, 12 Jan 2006) $


# import modules
#import sys, traceback
import types

from Config import Config, main_config
from logging import *
from BsdRadiusModule import BsdRadiusModule
import misc
from configDefaults import moduleConfigDefaults



# global variable which should contain BSD Radius modules configuration data
modulesConfig = Config()

# contains all loaded modules
# key - module name, value - BsdRadiusModule class instance
loadedModules = {}

# defines order of modules for authorization phase
authModules = []
# defines order of modules for accounting phase
acctModules = []



def readConfig(filePath):
	"""Read module configuration data from filePath
		Input: (string) path to file
		Output: none
	"""
	global modulesConfig
	readFiles = modulesConfig.read(filePath)
	# set up defaults and reread configuration if there was something read at all
	if len(readFiles) > 0:
		# set up defaults
		for moduleName in modulesConfig.keys():
			for key, value in moduleConfigDefaults.items():
				modulesConfig[moduleName][key] = value
		# overwrite defaults by rereading config file
		readFiles = modulesConfig.read(filePath)
	
	
	
def loadModules():
	"""Load all configured modules. Shutdown server if loading unsuccessful.
		Input: none
		Output: none
	"""
	global loadedModules
	global authModules
	global acctModules
	if not modulesConfig:
		return
	
	# try to import modules
	for moduleName, tokens in modulesConfig.items():
		debug ('Loading module: ', moduleName)
		mod = BsdRadiusModule(moduleName)
		try:
			if (tokens['startup_module']):
				mod['startup_module'] = __import__(tokens['startup_module'])
				mod['startup_funct'] = loadFunction(mod['startup_module'], tokens['startup_function'])
				mod.startupCapable = True
			if (tokens['authorization_module']):
				mod['authz_module'] = __import__(tokens['authorization_module'])
				mod['authz_funct'] = loadFunction(mod['authz_module'], tokens['authorization_function'])
				mod.authorizationCapable = True
			if (tokens['authentication_module']):
				mod['authc_module'] = __import__(tokens['authentication_module'])
				mod['authc_funct'] = loadFunction(mod['authc_module'], tokens['authentication_function'])
				mod.authenticationCapable = True
			if (tokens['accounting_module']):
				mod['acct_module'] = __import__(tokens['accounting_module'])
				mod['acct_funct'] = loadFunction(mod['acct_module'], tokens['accounting_function'])
				mod.accountingCapable = True
			if (tokens['shutdown_module']):
				mod['shutdown_module'] = __import__(tokens['shutdown_module'])
				mod['shutdown_funct'] = loadFunction(mod['shutdown_module'], tokens['shutdown_function'])
				mod.shutdownCapable = True
		# catch all exceptions, report them to user and shutdown server
		except:
			misc.printException()
			misc.quit('Can not load BSD Radius server modules', 1)
		else:
			loadedModules[moduleName] = mod
			debug (mod)
	
	info ('Setting order of authorization modules')
	# set module executing order in authorization and accounting phases
	authModuleOrder = main_config['AUTHORIZATION']['modules'].split(',')
	for moduleName in authModuleOrder:
		moduleName = moduleName.strip()
		if moduleName not in loadedModules:
			misc.quit('Module "%s" not loaded' % moduleName, 1)
		# make list of authorization module references
		if not loadedModules[moduleName].authorizationCapable:
			misc.quit('Module "%s" not authorization capable' % moduleName, 1)
		authModules.append(loadedModules[moduleName])
	info ('Setting order of accounting modules')
	acctModuleOrder = main_config['ACCOUNTING']['modules'].split(',')
	for moduleName in acctModuleOrder:
		moduleName = moduleName.strip()
		if moduleName not in loadedModules:
			misc.quit('Module "%s" not loaded' % moduleName, 1)
		if not loadedModules[moduleName].accountingCapable:
			misc.quit('Module "%s" not accounting capable' % moduleName, 1)
		acctModules.append(loadedModules[moduleName])



def loadFunction(module, functionName):
	"""Load and check function that belongs to given module
		Input: (module) reference to module which should countain loadable function;
			(string) function name
		Output: (function) reference to function
	"""
	if hasattr(module, functionName):
		function_ref = getattr(module, functionName)
	else:
		raise ValueError, 'Function "%s" in module "%s" doesn\'t exist' % (functionName, module.__name__)
	if callable(function_ref):
		return function_ref
	else:
		raise TypeError, '%s.%s must be function' % (module.__name__, functionName)



def execStartupModules():
	"""Execute all startup-capable modules
		Input: none
		Output: none
	"""
	for moduleName, module in loadedModules.items():
		if module.startupCapable:
			try:
				module['startup_funct']()
			# catch all exceptions, report them to user and shutdown server
			except:
				misc.printException()
				misc.quit('Can not execute startup function in module "%s"' % moduleName, 1)


def execShutdownModules():
	"""Execute all shutdown-capable modules
		Input: none
		Output: none
	"""
	for moduleName, module in loadedModules.items():
		if module.shutdownCapable:
			try:
				module['shutdown_funct']()
			# catch all exceptions, report them to user and shutdown server
			except:
				misc.printException()
				misc.quit('Can not execute shutdown function in module "%s"' % moduleName, 1)



def execAuthorizationModules(received, check, reply):
	"""Execute all authorization modules in preconfigured order
		Input:
			(dict) data received from client;
			(dict) internal parameters; 
			(dict) reply items;
		Output: (bool) True - success; False - failure
	"""
	modulesOk = True
	for module in authModules:
		if modulesOk and module.authorizationCapable:
			modstr = '### Authorization module "%s" ###' % module.name
			#info ()
			info ('#' * len(modstr))
			info (modstr)
			info ('#' * len(modstr))
			modulesOk = execFunction(module['authz_funct'], received, check, reply)
			debug ('--- Module %s results ---' % module.name)
			debug ('Check: ', check)
			debug ('Reply:', reply)
			debug ('Return value: ', modulesOk)
		# exit cycle if any module failed
		else:
			break
			
	# return module execution result
	return modulesOk
	
	
	
def execAuthenticationModules(received, check, reply):
	"""Execute authentication module corresponding to auth-type
		Input:
			(dict) data received from client;
			(dict) internal parameters; 
			(dict) reply items;
		Output: (bool) True - success; False - failure
	"""
	modulesOk = False
	moduleName = ''
	
	# find module name
	if 'Auth-Type' in check and check['Auth-Type']:
		authType = check['Auth-Type']
		if authType in main_config['AUTH_TYPES']:
			moduleName = main_config['AUTH_TYPES'][authType]
		else:
			error ('Unsupported Auth-Type: %s' % authType)
			return False
	else:
		moduleName = main_config['AUTH_TYPES']['default']
	# check module
	if not moduleName in loadedModules:
		error('Module "%s" not loaded' % moduleName)
		return False
	module = loadedModules[moduleName]
	if not module.authenticationCapable:
		error ('Module "%s" not authentication capable' % module.name)
		return False
	
	# execute function
	modstr = '### Authentication module "%s" ###' % module.name
	info ('#' * len(modstr))
	info (modstr)
	info ('#' * len(modstr))
	ret = execFunction(module['authc_funct'], received, check, reply)
	debug ('--- Module %s results ---' % module.name)
	debug ('Check: ', check)
	debug ('Reply:', reply)
	debug ('Return value: ', ret)
	return ret
	
	
	
	
def execAccountingModules(received):
	"""Execute all accounting modules in [reconfigured order
		Input:
			(dict) data received from client;
			(dict) internal parameters; 
			(dict) reply items;
		Output: (bool) True - success; False - failure
	"""
	modulesOk = True
	for module in acctModules:
		if modulesOk and module.accountingCapable:
			modstr = '### Accounting module "%s" ###' % module.name
			info ('#' * len(modstr))
			info (modstr)
			info ('#' * len(modstr))
			try:
				# protect received data dictionary
				locReceived = received.copy()
				# execute acct function
				module['acct_funct'](locReceived)
			except:
				misc.printException()
				modulesOk = False
			else:
				# if everything was ok
				# assign probably changed attribute dictionaries to original ones
				misc.rewriteDict(received, locReceived)
		# exit cycle if any module failed
		else:
			break
			
	# return module execution result
	return modulesOk
	


def execFunction(function, received = None, check = None, reply = None):
	"""Execute preloaded function
		Input: (function ref) reference to function,
			(dict) data received from client;
			(dict) internal parameters; 
			(dict) reply items;
		Output: (mixed) function result
	"""
	ret = None
	try:
		# protect attribute dictionaries in case of failure
		locReceived = received.copy()
		locCheck = check.copy()
		locReply = reply.copy()
		ret = function(locReceived, locCheck, locReply)
	except:
		misc.printException()
		ret = None
	else:
		# if everything was ok
		# assign probably changed attribute dictionaries to original ones
		misc.rewriteDict(received, locReceived)
		misc.rewriteDict(check, locCheck)
		misc.rewriteDict(reply, locReply)
	return ret
