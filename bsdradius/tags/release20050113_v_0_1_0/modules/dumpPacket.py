"""
BSD Radius server packet dump module.
It contains functions neccessary for dumping received packet
data into logfile.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/tags/release20050113_v_0_1_0/modules/dumpPacket.py $
# Author:		$Author: valts $
# File version:	$Revision: 122 $
# Last changes:	$Date: 2006-01-13 19:46:51 +0200 (Pk, 13 Jan 2006) $


import time
from os.path import dirname
import misc
from logging import *


PACKET_TYPE_AUTH = 1
PACKET_TYPE_ACCT = 2



def getFileName():
	"""Get file name depending on current date
		Input: none
		Output: (string) 
	"""
	return time.strftime('bsdradius.packet.%Y%m%d.dump', time.localtime())


def getLogDir():
	from Config import main_config
	return main_config['PATHS']['log_dir']

	
	
def packetToStr(dictionary):
	output = ""
	for attr in dictionary.keys():
		for val in dictionary[attr]:
			output += ("%s: %s\n" % (attr, val))
	return output


def acctPacketToStr(dictionary):
	output = "--AcctPacket--------------------------------------------------\n"
	output += packetToStr(dictionary)
	output += '-' * 52
	output += '\n\n'
	return output
	
	
def authPacketToStr(dictionary):
	output = "--AuthPacket--------------------------------------------------\n"
	output += packetToStr(dictionary)
	output += '-' * 52
	output += '\n\n'
	return output


	
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
			pktStr = acctPacketToStr(pkt)
		elif pktType == PACKET_TYPE_AUTH:
			pktStr = authPacketToStr(pkt)
		else:
			pktStr = packetToStr(pkt)
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
