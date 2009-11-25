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
misc module.
Contains various functions that are not any other module specific.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_4/bsdradius/misc.py $
# Author:		$Author: valts $
# File version:	$Revision: 201 $
# Last changes:	$Date: 2006-04-04 17:22:11 +0300 (Ot, 04 Apr 2006) $


# system modules
import os
import sys, traceback
import pwd, grp
import threading, thread
from types import *

# DTL modules
from bsdradius.logger import * 
from bsdradius.Config import main_config



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
	
	
	
def printExceptionError(prefix=''):
	"""Print only error string from exception info
		Input: none
		Output: none
	"""
	exc_type = sys.exc_info()[0]
	exc_value = sys.exc_info()[1]
	error ("%s%s: %s" % (prefix, exc_type, exc_value))
	
	
	
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
		from bsdradius import modules
		modules.execShutdownModules()

	info ("--- Bsdradiusd exiting ---")
	
	# disconnect from DB
	from bsdradius import DatabaseConnection
	if 'bsdradius dbh1' in DatabaseConnection.DatabaseConnection.handlers:
		dbh1 = DatabaseConnection.DatabaseConnection.getHandler('bsdradius dbh1')
		if dbh1.isConnected():
			info ('Closing DB connections')
			dbh1.disconnect()
			
	info ('--- Closing threads ---')
	threads = threading.enumerate()
	tCurrent = threading.currentThread()
	for th in threads:
		if th != tCurrent:
			th.exit()
			th.join()
	
	# close log file
	from bsdradius import logger
	if logger.logFile:
		if not logger.logFile.closed:
			info ('--- Closing logfile ---')
			logger.logFile.close()
			logger.logFile = None
	
	# remove pidfile
	pidFilePath = main_config['PATHS']['pid_file']
	if os.path.exists(pidFilePath):
		info ('--- Removing pidfile ---')
		os.remove(pidFilePath)
	else:
		error ('Cannot remove pid file: ', pidFilePath)
	
	# exit without raising exception
	#os._exit(exitCode)
	sys.exit(exitCode)
	
	
	
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



def rewriteDict(target, source):
	target.clear()
	for key, value in source.iteritems():
		target[key] = value



def copyDictWithListValues(source):
	"""Make full copy of dictionary with values as lists.
		It is necessary only when you want to protect
		also each item in list not only the dictionary.
	"""
	ret = {}
	for key, value in source.iteritems():
		if isinstance(value, ListType):
			ret[key] = value[:]
		else:
			ret[key] = [value]
	return ret



def packetToStr(pkt):
	"""Converts packet in dict format to printable string
		Input: (dict(list)) packet
		Output: (string) printable string
	"""
	if not isinstance(pkt, DictType):
		pkt = dict(pkt)
	output = ""
	for key, values in pkt.iteritems():
		for val in values:
			output += ("%r: %r\n" % (key, val))
	return output


	
def authPacketToStr(pkt):
	"""Converts auth packet in dict format to printable string
		Input: (dict(list)) packet
		Output: (string) printable string
	"""
	pktStr = "--AuthPacket--------------------------------------------------\n"
	pktStr += packetToStr(pkt)
	return pktStr
	
	
	
def acctPacketToStr(pkt):
	"""Converts acct packet in dict format to printable string
		Input: (dict(list)) packet
		Output: (string) printable string
	"""
	pktStr = "--AcctPacket--------------------------------------------------\n"
	pktStr += packetToStr(pkt)
	return pktStr
