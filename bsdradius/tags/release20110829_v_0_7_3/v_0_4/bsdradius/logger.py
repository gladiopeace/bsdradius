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

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_4/bsdradius/logger.py $
# Author:		$Author: valts $
# File version:	$Revision: 201 $
# Last changes:	$Date: 2006-04-04 17:22:11 +0300 (Ot, 04 Apr 2006) $

### System modules ###
import time
from threading import currentThread


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
	global logFile
	if not logFile:
		return
	# prepare current time
	timeNow = time.strftime('%Y-%m-%d %H:%M:%S')
	
	# prepare log string
	logstr = '[%s] ' % timeNow
	for arg in arguments:
		logstr += str(arg)
	logstr += "\n"

	if isUnrestrictedThread():
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
