"""
Data Tech Labs logging module
contains functions that are needed to log messages
to screen or logfile.


Usable functions:
	printToFile(*arguments)
	error(*arguments)
	debug(*arguments)
	info(*arguments)
	
	
Global configuration variables with defaults:

  # show error messages. True - show, False - don't show
  showErrors	= True
  
  # show debug messages. True - show, False - don't show
  showDebug	= True
  
  # show informative messages. True - show, False - don't show
  showInfo	= True
  
  # enable or disable logging to screen
  logToScreen = True


To enable logging to file please initiate
logfile handle: logFile

Example: 
	import logging
	logging.logFile = file('./logfile.log', 'a')
	
	from logging import printToFile, error, debug, info
	error ('This is ', 'error message')
	debug ('This is debug mesasge')
	info ('This is ', 1, '-st info message')
	printToFile('logging something to file')

"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/tags/release20050113_v_0_1_0/lib/logging.py $
# Author:		$Author: valts $
# File version:	$Revision: 122 $
# Last changes:	$Date: 2006-01-13 19:46:51 +0200 (Pk, 13 Jan 2006) $

### System modules ###
import time
import threading


### global variables ###

# logfile handle
logFile = None

# show error messages. True - show, False - don't show
showErrors	= True
# show debug messages. True - show, False - don't show
showDebug	= True
# show informative messages. True - show, False - don't show
showInfo	= True

# enable or disable logging to screen
logToScreen = False

# threads which are allowed to log something
restrictThreads = False
unrestrictedThreads = []



### funtions ###

def printToFile(*arguments):
	"""Prints incoming text to file
		input: accepts multiple arguments
		output: none
	"""
	
	# prepare current time
	timeNow = time.strftime('%Y-%m-%d %H:%M:%S')
	
	# prepare log string
	logstr = '[%s] ' % timeNow
	for arg in arguments:
		logstr += str(arg)
	logstr += "\n"

	global logFile
	if logFile and isUnrestrictedThread():
		try:
			logFile.write(logstr)
			logFile.flush()
		except:
			logFile = None	# to avoid repeated attemptin to write to log file
			error ('Can not write to logfile')



def error(*arguments):
	"""Print error message
		input: accepts multiple arguments
		output: none
	"""
	if not showErrors:
		return
	logstr = ''
	for arg in arguments:
		logstr += str(arg)
	if logToScreen and isUnrestrictedThread():
		print 'ERROR: ' + logstr
	printToFile('ERROR: ' + logstr)



def debug(*arguments):
	"""Print debug message
		input: accepts multiple arguments
		output: none
	"""
	if not showDebug:
		return
	logstr = ''
	for arg in arguments:
		logstr += str(arg)
	if logToScreen and isUnrestrictedThread():
		print logstr
	printToFile(logstr)



def info(*arguments):
	"""Print informative message
		input: accepts multiple arguments
		output: none
	"""
	if not showInfo:
		return
	logstr = ''
	for arg in arguments:
		logstr += str(arg)
	if logToScreen and isUnrestrictedThread():
		print logstr
	printToFile(logstr)



def isUnrestrictedThread():
	"""Check if current thread is allowed for logging
		Input: none
		Output: (bool) True - is unrestricted (allowed for logging),
			False - is restricted (not allowed for logging)
	"""
	if restrictThreads:
		if threading.currentThread() in unrestrictedThreads:
			return True
		else:
			return False
	else:
		return True



def addUnrestrictedThread():
	"""Add current thread to unrestricted thread list
		Input: none
		Output: none
	"""
	global unrestrictedThreads
	if restrictThreads:
		th = threading.currentThread()
		if th not in unrestrictedThreads:
			unrestrictedThreads.append(th)



def rmUnrestrictedThread():
	"""Remove current thread from unrestricted thread list
		Input: none
		Output: none
	"""
	global unrestrictedThreads
	if restrictThreads:
		th = threading.currentThread()
		if th in unrestrictedThreads:
			idx = unrestrictedThreads.index(th)
			del unrestrictedThreads[idx]
