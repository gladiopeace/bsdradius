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
This module holds useful functions for operation with internal
BSD Radius server modules.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_7/bsdradius/modules.py $
# Author:		$Author: valts $
# File version:	$Revision: 256 $
# Last changes:	$Date: 2006-08-18 12:22:04 +0300 (Pk, 18 Aug 2006) $


# import modules
#import sys, traceback
import sys
import imp

from bsdradius.Config import Config, main_config
from bsdradius.logger import *
from bsdradius.BsdRadiusModule import BsdRadiusModule
from bsdradius import misc
from bsdradius.configDefaults import moduleConfigDefaults
from types import *


# global variable which should contain BSD Radius modules configuration data
modulesConfig = Config()

# contains all loaded modules
# key - module name, value - BsdRadiusModule class instance
loadedModules = {}

# defines order of modules for authorization phase
authzModules = []
# defines order of modules for accounting phase
acctModules = []
# ties auth type with corresponding module togeather
authcModules = {}


# module status values
MODULE_OK = 1
MODULE_REJECTED = 2
MODULE_FAILED = 3


def getModuleStatusName(status):
	"""get module status name by value
		Input: (int) module status value
		Output: (str) status name
	"""
	ret = ''
	if status == MODULE_OK:
		ret = 'OK'
	elif status == MODULE_REJECTED:
		ret = 'REJECTED'
	elif status == MODULE_FAILED:
		ret = 'FAILED'
	else:
		ret = 'UNDEFINED'
	return ret



def readConfig(filePath):
	"""Read module configuration data from filePath
		Input: (string) path to file
		Output: none
	"""
	global modulesConfig
	readFiles = modulesConfig.readFiles(filePath)
	# set up defaults and reread configuration if there was something read at all
	if len(readFiles) > 0:
		# set up defaults
		for moduleName in modulesConfig.keys():
			for key, value in moduleConfigDefaults.items():
				modulesConfig[moduleName][key] = value
		# overwrite defaults by rereading config file
		readFiles = modulesConfig.readFiles(filePath)



def readModCustomConfig(filePath):
	"""Read configuration files which are individual for particular modules.
		Use configfile setting in user_modules.conf and modules.conf to enable
		reading of custom configuration files for selected modules.
		Input: (string) path to config file
		Output: (Config) Config class instance or None
	"""
	if not filePath:
		return None
	# Append configuration directory path to config file path if
	# config file path is not absolute.
	if filePath[0] != '/':
		filePath =  '%s/%s' % (main_config['PATHS']['conf_dir'], filePath)
	# read file
	modconf = Config()
	readFiles = modconf.readFiles(filePath)
	if len(readFiles) > 0:
		return modconf
	else:
		return None
	
	

def importModule(moduleName, path = None):
	"""Import module in current namespace.
		Input: (string) module name, (string) path to module dir
		Output: (module) imported module
	"""
	mod = None
	try:
		# import server module
		servMod = __import__('bsdradius.serverModules', globals(), locals(), [moduleName])
		if hasattr(servMod, moduleName):
			mod = getattr(servMod, moduleName)
	except:
		misc.printException()
		raise ImportError, 'Can not load system module: %s' % moduleName
	# import user module
	if not mod:
		if path == None:
			raise ImportError, "Can load module %s. Module not found between system \
			modules but user module search path not supplied" % moduleName
		try:
			fp, pathname, description = imp.find_module(moduleName, [path])
			mod = imp.load_module(moduleName, fp, pathname, description)
		except:
			misc.printException()
			raise ImportError, "Can not load user module: %s" % moduleName
	return mod
	
	
	
def loadModules():
	"""Load all configured modules. Shutdown server if loading unsuccessful.
		Input: none
		Output: none
	"""
	global loadedModules
	global authzModules
	global acctModules
	global authcModules
	if not modulesConfig:
		return
	
	disabledModules = [] # list of modules disabled by user
	userModDir = main_config['PATHS']['user_module_dir']
	# try to import modules
	for moduleName, tokens in modulesConfig.items():
		# check if module is enabled
		if not modulesConfig.getbool(moduleName, 'enable'):
			disabledModules.append(moduleName)
			debug ('WARNING: Module "%s" disabled by user. Skipping.' % moduleName)
			continue
		
		debug ('Loading module: ', moduleName)
		mod = BsdRadiusModule(moduleName)
		try:
			# read custom config file
			if tokens['configfile']:
				mod.radParsedConfig = readModCustomConfig(tokens['configfile'])
			# set up additional path for python modules and packages
			# it must be done before actually importing modules
			if tokens['pythonpath']:
				for pth in tokens['pythonpath'].split(':'):
					if pth not in sys.path:
						sys.path.insert(0, pth)
						debug ('Added additional pythonpath: %s' % pth)
			# load python modules and functions for BSDRadius module
			if (tokens['startup_module']):
				mod.startup_module = importModule(tokens['startup_module'], userModDir)
				mod.startup_funct = loadFunction(mod.startup_module, tokens['startup_function'])
				mod.startupCapable = True
				mod.startup_module.radParsedConfig = mod.radParsedConfig
			if (tokens['authorization_module']):
				mod.authz_module = importModule(tokens['authorization_module'], userModDir)
				mod.authz_funct = loadFunction(mod.authz_module, tokens['authorization_function'])
				mod.authorizationCapable = True
				mod.authz_module.radParsedConfig = mod.radParsedConfig
			if (tokens['authentication_module']):
				mod.authc_module = importModule(tokens['authentication_module'], userModDir)
				mod.authc_funct = loadFunction(mod.authc_module, tokens['authentication_function'])
				mod.authenticationCapable = True
				mod.authc_module.radParsedConfig = mod.radParsedConfig
			if (tokens['accounting_module']):
				mod.acct_module = importModule(tokens['accounting_module'], userModDir)
				mod.acct_funct = loadFunction(mod.acct_module, tokens['accounting_function'])
				mod.accountingCapable = True
				mod.acct_module.radParsedConfig = mod.radParsedConfig
			if (tokens['shutdown_module']):
				mod.shutdown_module = importModule(tokens['shutdown_module'], userModDir)
				mod.shutdown_funct = loadFunction(mod.shutdown_module, tokens['shutdown_function'])
				mod.shutdownCapable = True
				mod.shutdown_module.radParsedConfig = mod.radParsedConfig
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
		if moduleName in disabledModules:
			continue
		if moduleName not in loadedModules:
			misc.quit('Module "%s" not loaded' % moduleName, 1)
		# make list of authorization module references
		if not loadedModules[moduleName].authorizationCapable:
			misc.quit('Module "%s" not authorization capable' % moduleName, 1)
		authzModules.append(loadedModules[moduleName])
	info ('Mapping auth types with modules')
	authTypes = main_config['AUTH_TYPES']
	for authType, moduleName in authTypes.items():
		authType = authType.strip()
		moduleName = moduleName.strip()
		if moduleName in disabledModules:
			continue
		if moduleName not in loadedModules:
			misc.quit('Module "%s" not loaded' % moduleName, 1)
		if not loadedModules[moduleName].authenticationCapable:
			misc.quit('Module "%s" not authentication capable' % moduleName, 1)
		authcModules[authType] = loadedModules[moduleName]
	info ('Setting order of accounting modules')
	acctModuleOrder = main_config['ACCOUNTING']['modules'].split(',')
	for moduleName in acctModuleOrder:
		moduleName = moduleName.strip()
		if moduleName in disabledModules:
			continue
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
	for moduleName, module in loadedModules.iteritems():
		if module.startupCapable:
			# prepare and print log message
			modstr = '### Startup module "%s" ###' % module.name
			framestr = ('#' * len(modstr))
			info ('%s\n%s\n%s' % (framestr, modstr, framestr))
			try:
				module.startup_funct()
			# catch all exceptions, report them to user and shutdown server
			except:
				misc.printException()
				misc.quit('Can not execute startup function in module "%s"' % moduleName, 1)


def execShutdownModules():
	"""Execute all shutdown-capable modules
		Input: none
		Output: none
	"""
	for moduleName, module in loadedModules.iteritems():
		if module.shutdownCapable:
			# prepare and print log message
			modstr = '### Shutdown module "%s" ###' % module.name
			framestr = ('#' * len(modstr))
			info ('%s\n%s\n%s' % (framestr, modstr, framestr))
			try:
				module.shutdown_funct()
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
	moduleStatus = MODULE_OK
	result = None # value returned by module
	
	# Execute all authorization capable modules until
	# one of them fails or rejects or until all modules
	# executed.
	for i in xrange(len(authzModules)):
		module = authzModules[i]
		if moduleStatus == MODULE_OK and module.authorizationCapable:
			# prepare and print log message
			modstr = '### Authorization module "%s" ###' % module.name
			framestr = ('#' * len(modstr))
			info ('%s\n%s\n%s' % (framestr, modstr, framestr))
			# execute module and detect it's status
			try:
				dictItemsToLists(received)
				dictItemsToLists(check)
				dictItemsToLists(reply)
				result = module.authz_funct(received, check, reply)
				if result:
					moduleStatus = MODULE_OK
				else:
					moduleStatus = MODULE_REJECTED
			except:
				misc.printException()
				moduleStatus = MODULE_FAILED
			debug ('--- Module %s results ---' % module.name)
			debug ('Status: ', getModuleStatusName(moduleStatus))
			debug ('Check: ', check)
			debug ('Reply: ', reply)
			debug ('Return value: ', result)
			
		# exit cycle if any module failed
		else:
			break
			
	# return module execution result
	return moduleStatus
	
	
	
def execAuthenticationModules(received, check, reply):
	"""Execute authentication module corresponding to auth-type
		Input:
			(dict) data received from client;
			(dict) internal parameters; 
			(dict) reply items;
		Output: (bool) True - success; False - failure
	"""
	moduleName = ''
	
	# get auth type value
	authType = check.get('Auth-Type', None)
	if isinstance(authType, ListType):
		authType = authType[0]
	if not authType:
		authType = 'default'
	
	# find module
	module = authcModules.get(authType, None)
	if not module:
		error ('Unsupported Auth-Type: %s' % authType)
		return MODULE_FAILED
	
	# prepare and print log message
	modstr = '### Authentication module "%s" ###' % module.name
	framestr = ('#' * len(modstr))
	info ('%s\n%s\n%s' % (framestr, modstr, framestr))
	
	# execute function
	moduleStatus = MODULE_OK
	result = None
	try:
		dictItemsToLists(received)
		dictItemsToLists(check)
		dictItemsToLists(reply)
		result = module.authc_funct(received, check, reply)
		if result:
			moduleStatus = MODULE_OK
		else:
			moduleStatus = MODULE_REJECTED
	except:
		misc.printException()
		moduleStatus = MODULE_FAILED
		
	debug ('--- Module %s results ---' % module.name)
	debug ('Status: ', getModuleStatusName(moduleStatus))
	debug ('Check: ', check)
	debug ('Reply: ', reply)
	debug ('Return value: ', result)
	return moduleStatus
	
	
	
	
def execAccountingModules(received):
	"""Execute all accounting modules in [reconfigured order
		Input:
			(dict) data received from client;
			(dict) internal parameters; 
			(dict) reply items;
		Output: (bool) True - success; False - failure
	"""
	moduleStatus = MODULE_OK
	for i in xrange(len(acctModules)):
		module = acctModules[i]
		if moduleStatus == MODULE_OK and module.accountingCapable:
			# prepare and print log message
			modstr = '### Accounting module "%s" ###' % module.name
			framestr = ('#' * len(modstr))
			info ('%s\n%s\n%s' % (framestr, modstr, framestr))
			# execute accounting function.
			# consider that function failed only if it raised an exception
			try:
				dictItemsToLists(received)
				module.acct_funct(received)
			except:
				misc.printException()
				moduleStatus = MODULE_FAILED
		# exit cycle if any module failed
		else:
			break
	debug ('--- Module %s results ---' % module.name)
	debug ('Status: ', getModuleStatusName(moduleStatus))		
	# return module execution result
	return moduleStatus
	
	
	
def dictItemsToLists(dictn):
	"""Check dictionary items and convert them to lists if neccessary
		Input: (dict) unchecked dictionary
		Output: (dict) checked dictionary
	"""
	assert isinstance(dictn, DictionaryType)
	for key, val in dictn.iteritems():
		if not isinstance(val, ListType):
			dictn[key] = [val]
