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
BSD Radius server packet dump module.
It contains functions neccessary for dumping received packet
data into logfile.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_4/bsdradius/serverModules/dumpPacket.py $
# Author:		$Author: valts $
# File version:	$Revision: 201 $
# Last changes:	$Date: 2006-04-04 17:22:11 +0300 (Ot, 04 Apr 2006) $


import time
from os.path import dirname
from bsdradius import misc
from bsdradius.logger import *


PACKET_TYPE_AUTH = 1
PACKET_TYPE_ACCT = 2


logDir = None


def getFileName():
	"""Get file name depending on current date
		Input: none
		Output: (string) 
	"""
	return time.strftime('bsdradius.packet.%Y%m%d.dump', time.localtime())


def getLogDir():
	global logDir
	if logDir == None:
		from bsdradius.Config import main_config
		logDir = main_config['PATHS']['log_dir']
	return logDir
	
	

def dumpPacket(pkt, filePath, pktType = None):
	"""Dump packet into file
		Input: (packet or dict) packet, must contain __str__ method
			(string) path to file
		Output: none
	"""
	# check directory
	dirPath = dirname(filePath)
	if not misc.checkDir(dirPath):
		error('Directory %s not available for logging' % dirPath)
		return
		
	# dump packet to file
	try:
		debug ('Dumping packet to file:\n', filePath)
		file = open(filePath, 'a+')
		if pktType == PACKET_TYPE_ACCT:
			pktStr = misc.acctPacketToStr(pkt)
		elif pktType == PACKET_TYPE_AUTH:
			pktStr = misc.authPacketToStr(pkt)
		else:
			pktStr = misc.packetToStr(pkt)
		file.write(pktStr)
		file.close()
	except:
		error('Can not dump packet to file "%s"' % filePath)
		misc.printExceptionError()



def dumpAcctPacket(received):
	"""Dump accounting packet
		Input: (packet) accounting packet, must contain __str__ method
		Output: none
	"""
	filePath = "%s/%s/acct/%s" % (getLogDir(), received['Client-IP-Address'][0], getFileName())
	dumpPacket(received, filePath, PACKET_TYPE_ACCT)

	
	
def dumpFailedAcctPacket(received):
	"""Dump accounting packet which failed in some way.
		'Failed' means that there was error in processing packet
		in any of accounting modules.
		Input: (packet) accounting packet
		Output: none
	"""
	filePath = "%s/%s/acct_failed/%s" % (getLogDir(), received['Client-IP-Address'][0], getFileName())
	dumpPacket(received, filePath, PACKET_TYPE_ACCT)



def dumpUnhandledAcctPacket(received):
	"""Dump unhandled accounting packet	. Unhandled accounting
		packet is that one which was not passed to packet processing
		(working) threads because acct packet queue was full.
		Input: (packet) accounting packet
		Output: none
	"""
	filePath = "%s/%s/acct_unhandled/%s" % (getLogDir(), received['Client-IP-Address'][0], getFileName())
	dumpPacket(received, filePath, PACKET_TYPE_ACCT)

	
	
def dumpAuthPacket(received, check, reply):
	"""Dump authorization packet
		Input: (packet) authorization packet
		Output: (bool) True - success, False - failure
	"""
	filePath = "%s/%s/auth/%s" % (getLogDir(), received['Client-IP-Address'][0], getFileName())
	dumpPacket(received, filePath, PACKET_TYPE_AUTH)
	return True
	
	
	
def dumpFailedAuthPacket(received):
	"""Dump authorization packet which failed in some way.
		'Failed' means that there was error in processing packet
		in any of authorization or authentication modules.
		Input: (packet) authorization packet
		Output: none
	"""
	filePath = "%s/%s/auth_failed/%s" % (getLogDir(), received['Client-IP-Address'][0], getFileName())
	dumpPacket(received, filePath, PACKET_TYPE_AUTH)
	
	
	
def dumpUnhandledAuthPacket(received):
	"""Dump unhandled authorization packet	. Unhandled authorization
		packet is that one which was not passed to packet processing
		(working) threads because acct packet queue was full.
		Input: (packet) authorization packet
		Output: none
	"""
	filePath = "%s/%s/auth_unhandled/%s" % (getLogDir(), received['Client-IP-Address'][0], getFileName())
	dumpPacket(received, filePath, PACKET_TYPE_AUTH)
