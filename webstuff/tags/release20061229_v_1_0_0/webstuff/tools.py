"""
tools module.
Contains various functions that are not any other module specific.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/webstuff/tags/release20061229_v_1_0_0/webstuff/tools.py $
# Author:		$Author: valdiic $
# File version:	$Revision: 260 $
# Last changes:	$Date: 2006-10-04 15:03:10 +0300 (Tr, 04 Okt 2006) $


# system modules
import os
import sys, traceback
import platform
import thread
import imp
import random
from types import *
import time, datetime

# DTL modules
from logger import *


# check if we are running on WIndows
# in case of Windows OS pwd and grp modules are not available
sysname = platform.system().lower()
debug("This OS is %s " % sysname)
# hack For Microsoft Server 2003
if sysname == 'microsoft':
	sysname = 'windows'
# import UNIX only modules
if sysname != 'windows':
	import pwd, grp
else:
	warning("pwd and grp modules not available!")


pidFilePath = ''

def printException():
	"""print exception info
		Input: none
		Output: none
	"""
	# prepare exception info
	exc_type = sys.exc_info()[0]
	exc_value = sys.exc_info()[1]
	extractedTb = traceback.extract_tb(sys.exc_info()[2])

	# print exception info
	error()
	error ('---[ PYTHON EXCEPTION ]---')
	error ("Traceback (most recent call last):")
	# print all traceback stack items
	for tracebackItem in extractedTb:
		error("  File ", tracebackItem[0], ", line ", tracebackItem[1], ", in ", tracebackItem[2], "()")
		error("    ", tracebackItem[3])
	error("  ", str(exc_type), ": ", str(exc_value))
	error('---')
	
	
def strException():
	"""prepare user readable exception info
		Input: none
		Output: (string) nice formatted exception info
	"""
	# prepare exception info
	exc_type = sys.exc_info()[0]
	exc_value = sys.exc_info()[1]
	extractedTb = traceback.extract_tb(sys.exc_info()[2])

	# print exception info
	ret = '\n'
	ret += '---[ PYTHON EXCEPTION ]---\n'
	ret += "Traceback (most recent call last):\n"
	# print all traceback stack items
	for tracebackItem in extractedTb:
		ret += "  File %s, line %s, in %s()\n" % (tracebackItem[0], tracebackItem[1], tracebackItem[2])
		ret += "    %s\n" % tracebackItem[3]
	ret += "  %s: %s\n" % (str(exc_type), str(exc_value))
	ret += '---\n'
	return ret



def strExceptionError(prefix=''):
	"""Print only error string from exception info
		Input: none
		Output: none
	"""
	exc_type = sys.exc_info()[0]
	exc_value = sys.exc_info()[1]
	return "%s%s: %s" % (prefix, exc_type, exc_value)



def checkDir(dir, mode = 0755, user = '', group = ''):
	"""Check if given directory exists and try to create it if doesn't exist
		Input: (string) path to directory, (int) file access mode (octal),
			(string) owner's name, (string) owner's group
		Output: (bool) True - ok, False - failure
	"""
	dirPath = str(dir)
	if not dirPath:
		return False

	# create directory if it doesn't exist
	if not os.path.exists(dirPath):
		try:
			os.makedirs(dirPath, mode)
		except:
			printException()
			return False

	# check and set owner ang group if neccessary
	try:
		setOwner(dir, user, group)
	except:
		printException()
		return False

	# check if it is directory
	if os.path.isdir(dirPath):
		return True
	else:
		return False



def quit(message = "", exitCode = 0):
	"""Exit program displaying corresponding text message and
		returning appropiate errorcode. Cleanup before exiting.
		Input: (string) text mesasge, default: ""; (int) exit code,
			default: 0
		Output: none
	"""
	# display info message if exiting normaly
	# otherwise consider it as error message
	if message:
		if exitCode == 0:
			info (message)
		else:
			error (message)

	# remove pidfile
	if os.path.exists(pidFilePath):
		info ('--- Removing pidfile ---')
		os.remove(pidFilePath)
	else:
		error ('Cannot remove pid file: ', pidFilePath)

	sys.exit(exitCode)



def killSignalHandler(signum, frame):
	info ('Killed with signal ', signum)
	quit()



def switchUid(user = '', group = ''):
	"""Switch effective user and group id's
		Usually used for switching to nonprivileged user.
		UNIX only.
		due to security reasons
		Input: (string) usernam, (string) group name
	"""
	if sysname == 'windows':
		warning('switchUid() not available on Windows')
		return
	# change uid and gid
	try:
		# we have to switch group first
		if group:
			gid = grp.getgrnam(group)[2]
			os.setgid(gid)
		if user:
			uid = pwd.getpwnam(user)[2]
			os.setuid(uid)
	except:
		printException()
		quit ('Can not switch user and group to %s:%s' % (user, group), 1)



def makePidfile(filePath, user = '', group = ''):
	"""Store process id into file
		Input: none
		Output: none
	"""
	# store current proccess id in pid file
	if not checkDir(os.path.dirname(filePath), 0755, user, group):
		quit('Pid file directory checking failed', 1)
	try:
		myProcId = os.getpid()
		pidfile = file(filePath, 'w')
		pidfile.write(str(myProcId))
		pidfile.close()
		# change owner
		setOwner(filePath, user, group)
		global pidFilePath
		pidFilePath = filePath
	except:
		printException()
		quit ('Can not make pid file', 1)



def setOwner(path, user = '', group = ''):
	"""Change file's or directorie's owner
		Input: (string) file or dir path, (string) owner user name,
			(string) owner group name
		Output: none
	"""
	if sysname == 'windows':
		warning('setOwner() not available on Windows')
		return
	# check and set owner ang group if neccessary
	if user:
		uid = pwd.getpwnam(user)[2]
		os.chown(path, uid, -1)
	if group:
		gid = grp.getgrnam(group)[2]
		os.chown(path, -1, gid)



def rewriteDict(target, source):
	target.clear()
	for key, value in source.iteritems():
		target[key] = value
		
		

loadedModules = {}
loadedModulesLock = thread.allocate_lock()
def importModule(moduleName, path, alwaysReload = False):
	"""Import module in current namespace.
		Input: (string) module name, (string) path to module dir,
			(bool) True - reload module even if it has been loaded already,
				False - do not reload module if it is already loaded in one
				of previous 
		Output: (module) imported module
	"""
	# make loading modules thread safe
	loadedModulesLock.acquire()
	# Store loaded modules in seperate dictionaries for each module searching path.
	# This is neccessary to avoid module naming conflicts.
	if path not in loadedModules:
		loadedModules[str(path)] = {}
	pathModules = loadedModules[str(path)]
	
	# load module
	mod = None
	# do not reload modules
	if not alwaysReload and moduleName in pathModules:
		mod = pathModules[moduleName]
		loadedModulesLock.release()
		return mod
	# Turn path to list since find_module() accepts list of paths
	if not isinstance(path, ListType):
		path = [path]
	# import module
	try:
		fp, pathname, description = imp.find_module(moduleName, path)
		mod = imp.load_module(moduleName, fp, pathname, description)
		pathModules[moduleName] = mod
		fp.close()
	except:
		printException()
		loadedModulesLock.release()
		raise ImportError, "Can not import module: %s" % moduleName
	else:
		loadedModulesLock.release()
		return mod



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
		raise TypeError, '%s.%s is not callable (probably not function at all)' % (module.__name__, functionName)



def clearImportedModules(path = None):
	"""Clear imported modules which were imported from specific directory path
		or completely remove all imported modules if path not specified.
		Input: (string) directory path
		Output: none
	"""
	# make operations with modules thread safe
	loadedModulesLock.acquire()
	if path != None and str(path) in loadedModules:
		debug ('Clearing modules imported from path: %s' % path)
		loadedModules[str(path)].clear()
	elif path == None:
		debug ('Clearing all imported modules')
		loadedModules.clear()
	loadedModulesLock.release()



def randString(length = 50, allchars = None):
	"""Returns string of random characters. Mostly suitable for generating
		session ids
		Input: (int) length, (string, list, tuple) valid characters
		Output: (string) generated string
	"""
	assert isinstance(length, IntType)
	# set default valid characters
	if allchars == None:
		#allchars = 'abcdefghijklnmopqrstuvwxyzABCDEFGHIJKLNMOPQRSTUVWXYZ0123456789!@#$%^*()~|<>,.;:+-_'
		allchars = 'abcdefghijklnmopqrstuvwxyzABCDEFGHIJKLNMOPQRSTUVWXYZ'
	try:
		k = allchars[0]
	except:
		raise TypeError, "allchars must be instance of sequence type"
		
	ret = ''
	for i in xrange(length):
		ret += random.choice(allchars)
	return ret



def selectList(result_set, key_attr, value_attr):
	"""Prepare a list for use in a web form <select> field."""
	select_list = []
	while True:
		row = result_set.fetchone()
		if row == None:
			break
		pair = (getattr(row, key_attr), getattr(row, value_attr))
		select_list.append(pair)
		
	return select_list



def firstDay():
	"""Return ISO timestamp representation of the first day of the
	current month.
	"""
	return time.strftime("%Y-%m-01")



def lastDay():
	"""Return ISO timestamp representation of the last day of the
	current month.
	"""
	now = time.localtime()
	
	nextmonth = now[1] + 1
	if nextmonth > 12:
		nextmonth = 1
		
	ed = datetime.date(now[0], nextmonth, 1) - datetime.timedelta(1)
	return ed.isoformat()



class TableRowMapper(object):
	"""Class for easier column value mapping to class instance"""
	def mapColumns(self, row):
		"""Maps all columns in row to class instance.
			All column names are in lowercase
			Input: (sqlachemy table row) row
			Output: None
		"""
		for key, value in row.items():
			setattr(self, key, value)



def cutPrefix(source, prefix):
	"""Cut prefix from source string.
		Input: (string) source string; (string) prefix
		Output: (string) source str without prefix
	"""
	source = str(source)
	prefix = str(prefix)
	if source.startswith(prefix):
		return source[len(prefix):]
	else:
		return source
