#!/usr/bin/env python

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
RADIUS client
"""


# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_7/tools/bsdradclient.py $
# Author:		$Author: valts $
# File version:	$Revision: 257 $
# Last changes:	$Date: 2006-08-18 17:33:54 +0300 (Pk, 18 Aug 2006) $

import sys, socket, random
sys.path.insert(0, '../')

from optparse import OptionParser
from bsdradius.pyrad import packet
from bsdradius.pyrad import dictionary
from bsdradius.pyrad.client import Client, Timeout


C_AUTH = 1
C_ACCT = 2
C_BOTH = 3
commands = {
	'auth' : C_AUTH,
	'acct' : C_ACCT,
	'both' : C_BOTH,
}
hexSymbols = '0123456789abcdef'


def getAuthPacket(srv, attributes = {}):
	req=srv.CreateAuthPacket(code = packet.AccessRequest, **attributes)
	if 'User-Password' in attributes:
		req["User-Password"] = req.PwCrypt(attributes['User-Password'][0])
	return req



def getAcctPacket(srv, attributes = {}):
	req=srv.CreateAcctPacket(code = packet.AccountingRequest, **attributes)
	if not req.has_key("Acct-Input-Octets"):
		req["Acct-Input-Octets"] = random.randrange(2**10, 2**30)
	if not req.has_key("Acct-Output-Octets"):
		req["Acct-Output-Octets"] = random.randrange(2**10, 2**30)
	if not req.has_key("Acct-Session-Time"):
		req["Acct-Session-Time"] = random.randrange(10, 3600)
	if not req.has_key("Acct-Terminate-Cause"):
		req["Acct-Terminate-Cause"] = random.choice(["User-Request", "Idle-Timeout"])
	return req



def sendPacket(srv, req):
	try:
		reply = srv.SendPacket(req)
		return reply
	except Timeout:
		print "RADIUS server does not reply"
		sys.exit(1)
	except socket.error, error:
		print "Network error: " + error[1]
		sys.exit(1)



def genAcctSessionId(length = 16, symbols = hexSymbols):
	"""Generate random string for Acct-Session-Id
	"""
	sesid = ''
	for i in range(16):
		sesid += random.choice(symbols)
	return sesid



def genH323ConfId():
	"""Generate random h323 conference id
	"""
	sesid = ''
	for i in range(4):
		for j in range(8):
			sesid += random.choice(hexSymbols)
		sesid += ' '
	sesid = sesid.rstrip(' ')
	return sesid



############
### MAIN ###
############

# read cmd line config
usage = "%prog [options] auth|acct|both"
cliParser = OptionParser(usage = usage)
cliParser.add_option("-a", "--server-address",
	action="store", dest="serverHost",
	help="IP address of RADIUS server, default: 127.0.0.1", metavar="ADDRESS",
	type="string", default='127.0.0.1')
cliParser.add_option("-t", "--auth-port",
	action="store", dest="authport", metavar="PORT", type="int",
	help="Server UDP port for authorization messages, default: 1812", default=1812)
cliParser.add_option("-c", "--acct-port",
	action="store", dest="acctport", metavar="PORT", type="int",
	help="Server UDP port for accounting messages, default: 1813", default=1813)
cliParser.add_option("-s", "--secret",
	action="store", dest="secret", metavar="SECRET",
	help="Shared secret between server and client, default: testing123", default="testing123")
cliParser.add_option("-d", "--dictionary",
	action="store", dest="dictFile", metavar="FILE",
	help="path to dictionary file, default: /usr/local/share/bsdradius/dictionaries/dictionary",
	default="/usr/local/share/bsdradius/dictionaries/dictionary")
cliParser.add_option("-r", "--attributes",
	action="store", dest="attrFile", metavar="FILE",
	help="path to file holding attributes which client has to send to server, default: ./bsdradclient.conf",
	default="./bsdradclient.conf")
cliParser.add_option("-g", "--dont-gen-ids",
	action="store_false", dest="genIds", metavar="FILE",
	help="don't generate random Acct-Session-Id and h323-conf-id, default: false",
	default = True)


(cliOptions, args) = cliParser.parse_args()
cmd = C_BOTH
if len(args) == 1 and args[0] in commands:
	cmd = commands[args[0]]
	

# parse dictionaries
print '--- Parsing dictionary files ---'
dict = dictionary.Dictionary(cliOptions.dictFile)
# start server itself
authport = cliOptions.authport
acctport = cliOptions.acctport
srv = Client(server = cliOptions.serverHost, secret = cliOptions.secret,
	dict = dict, authport=authport, acctport=acctport)

print "--- Reading config file ---"
attributes = {}
try:
	fh = open(cliOptions.attrFile)
except:
	pass
else:
	for line in fh:
		# get rid of comments
		line = line.strip()
		if line.startswith('#'):
			line = line.split('#', 1)[0]
		line = line.strip()
		if not line:
			continue
		
		# get attr, value pairs
		tokens = line.split('=', 1)
		if len(tokens) <= 0:
			continue
		elif len(tokens) == 1:
			attr = tokens[0]
			value = ''
		else:
			attr = tokens[0]
			value = tokens[1]
		
		# strip whitespace
		attr = attr.strip()
		value = value.strip()
		
		if attr not in attributes:
			attributes[attr] = []
		
		# convert attribute to corresponding datatype according to dictionary records
		# for now it is neccessary for integers only
		try:
			dictAttr = dict[attr]
			if dictAttr.type == "integer" or dictAttr.type == "date":
				value = int(value)
		except KeyError:
			print 'Attribute "%s" not in dictionary. Skipping...' % attr
		except ValueError:
			# Don't report about failed convert attempts.
			# There are attributes which string values are mapped with integer ones.
			pass
		
		print "Adding: %s : %r" % (attr, value)
		attributes[attr].append(value)

# generate random unique id's if neccessary
if cliOptions.genIds:
	if 'h323-conf-id' not in attributes:
		confid = genH323ConfId()
		print 'Adding %s: %r' % ('h323-conf-id', confid)
		attributes['h323-conf-id'] = [confid]
	if 'Acct-Session-Id' not in attributes:
		sesid = genAcctSessionId()
		print 'Adding %s: %r' % ('Acct-Session-Id', sesid)
		attributes['Acct-Session-Id'] = [sesid]

print "--- preparing packet ---"
req = []
if cmd == C_AUTH:
	print "Preparing authorization request"
	req.append(getAuthPacket(srv, attributes))
elif cmd == C_ACCT:
	print "Preparing accounting request"
	req.append(getAcctPacket(srv, attributes))
elif cmd == C_BOTH:	
	print "Preparing authorization request"
	req.append(getAuthPacket(srv, attributes))
	print "Preparing accounting request"
	req.append(getAcctPacket(srv, attributes))

print "--- Sending requests ---"
for i in range(len(req)):
	print "Sending request %s" % i
	reply = sendPacket(srv, req[i])
	print "Return code: %s" % reply.code
	print "Received answer:"
	print reply
