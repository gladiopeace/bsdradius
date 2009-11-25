"""
misc module.
Contains various functions that are not any other module specific.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/tags/release20050113_v_0_1_0/lib/misc.py $
# Author:		$Author: valts $
# File version:	$Revision: 115 $
# Last changes:	$Date: 2006-01-10 21:25:46 +0200 (Ot, 10 Jan 2006) $


# system modules
import os
import sys, traceback
import pwd, grp

# DTL modules
import DatabaseConnection
import logging
from logging import * 
from Config import main_config
import modules



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
	error ('---[ ERROR: rlm_python ]---')
	error ("Traceback (most recent call last):")
	# print all traceback stack items
	for tracebackItem in extractedTb:
		error("  File ", tracebackItem[0], ", line ", tracebackItem[1], ", in ", tracebackItem[2], "()")
		error("    ", tracebackItem[3])
	error("  ", str(exc_type), ": ", str(exc_value))
	error('---')
	error()



def fprintException():
	"""print exception info to debug file
		Input: none
		Output: none
	"""
	# prepare exception info
	exc_type = sys.exc_info()[0]
	exc_value = sys.exc_info()[1]
	extractedTb = traceback.extract_tb(sys.exc_info()[2])

	# print exception info
	printToFile()
	printToFile ('---[ ERROR: rlm_python ]---')
	printToFile ("Traceback (most recent call last):")
	# print all traceback stack items
	for tracebackItem in extractedTb:
		printToFile("  File ", tracebackItem[0], ", line ", tracebackItem[1], ", in ", tracebackItem[2], "()")
		printToFile("    ", tracebackItem[3])
	printToFile("  ", str(exc_type), ": ", str(exc_value))
	printToFile('---')
	printToFile()
	
	
	
def printExceptionError():
	"""Print only error string from exception info
		Input: none
		Output: none
	"""
	exc_value = sys.exc_info()[1]
	error (exc_value)
	
	
	
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
	
	info ('--- Executing shutdown modules ---')
	if exitCode == 0:
		modules.execShutdownModules()

	info ("--- Bsdradiusd exiting ---")
	
	# disconnect from DB
	if 'dbh1' in dir(DatabaseConnection):
		if DatabaseConnection.dbh1.isConnected():
			info ('Closing DB connections')
			DatabaseConnection.dbh1.disconnect()
	
	# close log file
	if logging.logFile:
		if not logging.logFile.closed:
			info ('Closing logfile')
			logging.logFile.close()
			logging.logFile = None
	
	# remove pidfile
	pidFilePath = main_config['PATHS']['pid_file']
	if os.path.exists(pidFilePath):
		info ('Removing pidfile')
		os.remove(pidFilePath)
	else:
		error ('Cannot remove pid file: ', pidFilePath)
	
	# exit without raising exception
	os._exit(exitCode)
	
	
	
def makePidfile():
	"""Store process id into file
		Input: none
		Output: none
	"""
	# store current proccess id in pid file
	try:
		filePath = main_config['PATHS']['pid_file']
		user = main_config['SERVER']['user']
		group = main_config['SERVER']['group']
		
		myProcId = os.getpid()
		pidfile = file(main_config['PATHS']['pid_file'], 'w')
		pidfile.write(str(myProcId))
		pidfile.close()
		# change owner
		setOwner(filePath, user, group)
	except:
		printExceptionError()
		quit ('Can not make pid file', 1)
		
		
		
def killSignalHandler(signum, frame):
	info ('Killed with signal ', signum)
	quit()
	
	
	
def switchUid(user = '', group = ''):
	"""Switch effective user and group id's
		Usually used for switching to nonprivileged user
		due to security reasons
		Input: (string) usernam, (string) group name
	"""
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
		printExceptionError()
		quit ('Can not switch user and group to %s:%s' % (user, group), 1)
	
	

def setOwner(path, user = '', group = ''):
	"""Change file's or directorie's owner
		Input: (string) file or dir path, (string) owner user name,
			(string) owner group name
		Output: none
	"""
	# check and set owner ang group if neccessary
	if user:
		uid = pwd.getpwnam(user)[2]
		os.chown(path, uid, -1)
	if group:
		gid = grp.getgrnam(group)[2]
		os.chown(path, -1, gid)



def rewriteDict(old, new):
	for key in old.keys():
		del old[key]
	for key, value in new.items():
		old[key] = value
