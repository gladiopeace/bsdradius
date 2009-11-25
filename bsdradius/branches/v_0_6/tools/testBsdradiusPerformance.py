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
Tool for testing BSD Radius performance.
It is suggested to run multiple testing scripts on multiple servers
to achieve the real performance.
"""


# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_6/tools/testBsdradiusPerformance.py $
# Author:		$Author: valts $
# File version:	$Revision: 253 $
# Last changes:	$Date: 2006-07-28 11:36:19 +0300 (Pk, 28 Jūl 2006) $

import time
import socket
import os, sys
import random
from optparse import OptionParser
sys.path.insert(0, '../bsdradius')

import Config
import pyrad.packet
from configDefaults import defaultOptions, defaultTypes
from pyrad.client import Client
from pyrad import dictionary



def getAuthPacket(srv):
	req=srv.CreateAuthPacket(code=pyrad.packet.AccessRequest,
		User_Name="testuser")
	req["NAS-IP-Address"] = "192.168.1.10"
	req["NAS-Port"] = 0
	req["Service-Type"] = "Login-User"
	req["NAS-Identifier"] = "trillian"
	req["Called-Station-Id"] = "00-04-5F-00-0F-D1"
	req["Calling-Station-Id"] = "00-01-24-80-B3-9C"
	req["Framed-IP-Address"] = "10.0.0.100"
	req["User-Password"] = req.PwCrypt('testing123')
	return req


def getAcctPacket(srv):
	req=srv.CreateAcctPacket(code=pyrad.packet.AccountingRequest,
		User_Name="testuser")
	req["NAS-IP-Address"]="192.168.1.10"
	req["NAS-Port"]=0
	req["NAS-Identifier"]="trillian"
	req["Called-Station-Id"]="00-04-5F-00-0F-D1"
	req["Calling-Station-Id"]="00-01-24-80-B3-9C"
	req["Framed-IP-Address"]="10.0.0.100"
	req["Acct-Status-Type"]="Stop"
	req["Acct-Input-Octets"] = random.randrange(2**10, 2**30)
	req["Acct-Output-Octets"] = random.randrange(2**10, 2**30)
	req["Acct-Session-Time"] = random.randrange(120, 3600)
	req["Acct-Terminate-Cause"] = random.choice(["User-Request", "Idle-Timeout"])
	return req


def sendPacket(srv, req):
	try:
		srv.SendPacket(req)
	except pyrad.client.Timeout:
		print "RADIUS server does not reply"
		sys.exit(1)
	except socket.error, error:
		print "Network error: " + error[1]
		sys.exit(1)



############
### MAIN ###
############

### startup ###
print '--- Reading configuration ---'
# read config file
Config.readFiles = Config.main_config.read(Config.configFiles)
# check if all neccessary files are read
if Config.configFiles != Config.readFiles:
	print "Can not read required configuration files"
	sys.exit(1)
main_config = Config.main_config

# read cmd line config
usage = "usage: %prog [options]"
cliParser = OptionParser(usage=usage)
cliParser.add_option("-t", "--test-time",
	action="store", dest="testTime",
	help="Time in sec which will be spent in each test case", metavar="TIME",
	type="int", default=60)
cliParser.add_option("-s", "--server-host",
	action="store", dest="serverHost",
	help="IP address of RADIUS server", metavar="ADDRESS",
	type="string", default='127.0.0.1')
cliParser.add_option("-c", "--no-acct",
	action="store_true", dest="noAcct",
	help="Send accounting messages", default=False)
cliParser.add_option("-z", "--no-auth",
	action="store_true", dest="noAuth",
	help="Send authorization messages", default=False)
cliParser.add_option("-x", "--no-mixed",
	action="store_true", dest="noMixed",
	help="Send mixed (acct and auth) messages", default=False)
(cliOptions, args) = cliParser.parse_args()

# get options
testTime	= cliOptions.testTime
testAuth	= not cliOptions.noAuth
testAcct	= not cliOptions.noAcct
testMixed	= not cliOptions.noMixed
host		= cliOptions.serverHost


# parse dictionaries
print '--- Parsing dictionary files ---'
dict = dictionary.Dictionary(main_config['PATHS']['dictionary_file'])
# start server itself
authport = main_config["SERVER"]["auth_port"]
acctport = main_config["SERVER"]["acct_port"]
srv=Client(server=host, secret="testing123", dict=dict)

### run tests ###
totalAuthRequests = 0
totalAcctRequests = 0
totalMixedRequests = 0

if testAuth:
	startTime = time.time()
	endTime = startTime + testTime
	while (time.time() < endTime):
		req = getAuthPacket(srv)
		sendPacket(srv, req)
		totalAuthRequests += 1

if testAcct:
	startTime = time.time()
	endTime = startTime + testTime
	while (time.time() < endTime):
		req = getAcctPacket(srv)
		sendPacket(srv, req)
		totalAcctRequests += 1

if testMixed:
	startTime = time.time()
	endTime = startTime + testTime
	while (time.time() < endTime):
		# in real life radius server gets slightly more auth requests than acct requests
		choice = random.choice([1, 1, 1, 2, 2])
		if choice == 1:
			req = getAuthPacket(srv)
		else:
			req = getAcctPacket(srv)
		sendPacket(srv, req)
		totalMixedRequests += 1


### print results ###
print "I ran each test %s seconds" % testTime
print "Auth requests:", totalAuthRequests
print "Acct requests:", totalAcctRequests
print "Mixed requests:", totalMixedRequests
