"""
Data Tech Labs logger module
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
	import logger
	logger.logFile = file('./logfile.log', 'a')
	
	from logger import printToFile, error, debug, info
	error ('This is ', 'error message')
	debug ('This is debug mesasge')
	info ('This is ', 1, '-st info message')
	printToFile('logging something to file')

"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/webstuff/tags/release20061229_v_1_0_0/webstuff/logger.py $
# Author:		$Author: valts $
# File version:	$Revision: 70 $
# Last changes:	$Date: 2006-08-24 21:47:42 +0300 (Ce, 24 Aug 2006) $


### System modules ###
import time, sys
from threading import currentThread


### global variables ###

# logfile handle
logFile = None
# file like objects for logging output to screen
errorOutput = None
debugOutput = None
infoOutput = None
warningOutput = None

# show error messages. True - show, False - don't show
showErrors	= True
# show debug messages. True - show, False - don't show
showDebug	= False
# show informative messages. True - show, False - don't show
showInfo	= False
# show warning messages. True - show, False - don't show
showWarning	= True

# enable or disable logging to screen
logToScreen = True

# error message prefix and postfix
errorPrefix = "ERROR: "
errorPostfix = ""
# debug message prefix and postfix
debugPrefix = ""
debugPostfix = ""
# info message prefix and postfix
infoPrefix = ""
infoPostfix = ""
# warning message prefix and postfix
warningPrefix = "WARNING: "
warningPostfix = ""

# threads which are allowed to log something
restrictThreads = False
unrestrictedThreads = []


### Output handlers ###
class logOutput(object):
	def __init__(self, handler, prefix = '', postfix = '', show = True):
		"""Perform initial setup actions.
			Input: (file) file like object (methods "write" and "writelines" are
					required;
				(string) log line prefix
				(string) log line postfix
				(bool) determines if this object will log something at all
		"""
		self.handler = handler
		self.prefix = prefix
		self.postfix = postfix
		self.show = show
	
	
	def write(self, *arguments):
		"""Write logging string(s) to handler and file
		"""
		if self.show and isUnrestrictedThread():
			# prepare string for logging
			logstr = self.prefix
			for arg in arguments:
				logstr += str(arg)
			logstr += self.postfix
			# write the string
			if logToScreen:
				self.handler.write(logstr + '\n')
			printToFile(logstr)
	
	
	def writelines(self, logstr):
		"""Log multiple lines
		"""
		if self.show and isUnrestrictedThread():
			for line in logstr:
				self.write(line)



### functions ###
def createOutputHandlers():
	"""Set up output handlers togeather with their output prefixes and postfixes
		If you want to completely redirect the output redefine the output
		handlers yourself.
		Input: None
		Output: None
	"""
	global errorOutput
	global debugOutput
	global infoOutput
	global warningOutput
	errorOutput = logOutput(sys.stderr, prefix = errorPrefix, show = showErrors)
	debugOutput = logOutput(sys.stdout, prefix = debugPrefix, show = showDebug)
	infoOutput = logOutput(sys.stdout, prefix = infoPrefix, show = showInfo)
	warningOutput = logOutput(sys.stderr, prefix = warningPrefix, show = showWarning)

# call the function right here to set up defaults
createOutputHandlers()



def printToFile(*arguments):
	"""Prints incoming text to file
		input: accepts multiple arguments
		output: none
	"""
	global logFile
	if logFile is not None and isUnrestrictedThread():
		# prepare current time
		timeNow = time.strftime('%Y-%m-%d %H:%M:%S')
		
		# prepare log string
		logstr = '[%s] ' % timeNow
		for arg in arguments:
			logstr += str(arg)
		logstr += "\n"
	
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
	errorOutput.write(*arguments)



def debug(*arguments):
	"""Print debug message
		input: accepts multiple arguments
		output: none
	"""
	debugOutput.write(*arguments)



def info(*arguments):
	"""Print informative message
		input: accepts multiple arguments
		output: none
	"""
	infoOutput.write(*arguments)



def warning(*arguments):
	"""Print warning message
		input: accepts multiple arguments
		output: none
	"""
	warningOutput.write(*arguments)



def isUnrestrictedThread():
	"""Check if current thread is allowed for logging
		Input: none
		Output: (bool) True - is unrestricted (allowed for logging),
			False - is restricted (not allowed for logging)
	"""
	if restrictThreads:
		if currentThread() in unrestrictedThreads:
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
		th = currentThread()
		if th not in unrestrictedThreads:
			unrestrictedThreads.append(th)



def rmUnrestrictedThread():
	"""Remove current thread from unrestricted thread list
		Input: none
		Output: none
	"""
	global unrestrictedThreads
	if restrictThreads:
		th = currentThread()
		if th in unrestrictedThreads:
			idx = unrestrictedThreads.index(th)
			del unrestrictedThreads[idx]
