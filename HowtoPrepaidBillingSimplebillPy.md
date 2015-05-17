
```
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
Simple billing module for BSD Radius 
This module conatins trivial example of how to build your own prepaid billing
using BSD Radius server.

Received, check and reply packets should be (or behive like) dictionaries. 
Format: {'key1': ['value1', 'value2', ...], 'key2': [...]}

Use exceptions in case of failure.
Use return values in authorization and authentication functions
to tell the server if user is ok or not.

"""

import exceptions
from string import Template
import re, datetime
from types import *
# you can use functions defined in logger module to use BSD Radius's
# logger system.
from bsdradius.logger import *
from bsdradius.DatabaseConnection import DatabaseConnection
from bsdradius.misc import parseDatetime

#
# startup function opens connection to SQL database 
#
def simplebill_funct_startup():
	"""Open sql connection
		Input: none
		Output: none
	"""
	info ('Opening database connections')
	# he we pars modules own config file, which, in our example is 
	# etc/bsdradius/simplebill.conf
	if radParsedConfig == None:
		error ('No configuration data was parsed')
	else:
		debug ("Parsed configuration: ", radParsedConfig)
	
	sqlAccess = radParsedConfig['DATABASE']
	
	# detect database driver name and open connection
	# mysql is used in example, though there should not be problem to use Postgres
	if sqlAccess['type'] == 'postgresql':
		dbadapterName = 'psycopg'
	else:
		dbadapterName = 'MySQLdb'
	dbh = DatabaseConnection.getHandler('simplebill', dbadapterName)
	dbh.connect(host = sqlAccess['host'], user = sqlAccess['user'],
		password = sqlAccess['pass'], dbname = sqlAccess['name'])

#
# authorization function
#
def simplebill_funct_authz(received, check, reply):
	"""Find user in database
		Input: (dict) received data, (dict) check data, (dict) reply data
		Output: (bool) True - success, False - failure
	"""	
	debug ("Received packet:")
	debug (received)
	# Select account data.
	# we have to tell get_account function should it look for password or no
	# cases where no password should be looked are:
	#  1) Auth-Type is already set by some module 
	#  2) function called from accounting module (see below in accounting function)
	authType = check.get('Auth-Type', [None])[0]
	if not authType:
		check_password = True
	else:
		check_password = False
	account = simplebill_get_account(received, check_password)
	debug ("Account")
	debug (account)
	# see if account was found
	if account:
		debug ('Account found')
	        if account['balance'] <= 0:
	                debug ('Account balance below zero')
                        reply['h323-return-code'] = "h323-return-code=2"
                        reply['h323-credit-amount'] = "h323-credit-amount=0.00"
                        return False  

		authType = check.get('Auth-Type', [None])[0]
		if not authType:
			# just set the auth type to "simplebill" if no previous modules have touched it.
			check['Auth-Type'] = ['simplebill']
		elif len(acctData) >= 2:
			# pass username and password to module which has set up it's auth type.
			check['User-Name'] = account['User-Name']
			check['User-Password'] = account['User-Password']
		# now lets see if it call admission message based on presence of called number
		if 'Called-Station-Id' in received:
			# Call admission stage - we should check for entry in rate table
			debug ('This is Call Admission Message')
			rate = simplebill_get_rate(account, received)
			if rate:
				debug ("Rate Query Returned Result")
				# we should perform remaining seconds calculation now
				remainingSecs = (account['balance'] - rate['ratePerCall']) * 60 / rate['ratePerMinute']
				remainingSecs -= remainingSecs % int(rate['increment'])
				debug ("Remaining secs")
				debug (remainingSecs)
				# allow to call this destination 
				reply['h323-return-code'] = "h323-return-code=0"
				reply['h323-credit-time'] = "h323-credit-time=%d" % (remainingSecs)
				reply['Session-Timeout'] = "%d" % remainingSecs
				return True
			else:
				# return 0 remaining seconds time to prevent to call this destination 
				debug ("Rate Query Returned No Result")
				reply['h323-return-code'] = "h323-return-code=2"
				reply['h323-credit-time'] = "h323-credit-time=0"
				reply['Session-Timeout'] = 0
				return False
		else: 
			# registration stage 
			debug ("This is Registration Request Message")
			# prepare reply message
			# confirm registration with remaining balance message 
			reply['h323-return-code'] = "h323-return-code=0"
			reply['h323-credit-amount'] = "h323-credit-amount=%.2f" % (account['balance']) # balance column
			reply['h323-billing-model'] = "h323-billing-model=1"
			return True
	else:
		debug ('Account not found')
		# Return 0 remaining credit and invalid account code
		# if user was not found
		reply['h323-return-code'] = "h323-return-code=2"
		reply['h323-credit-amount'] = "h323-credit-amount=0.00"
		return False

#
# authentication function 
#
def simplebill_funct_authc(received, check, reply):
	"""Do some authentication tasks here. Check username and
		password against chap, md5, digest or something like that
		Input: (dict) received data, (dict) check data, (dict) reply data
		Output: (bool) True - success, False - failure
		NOTE: since all function attributes in python are passed by reference
			it is possible to modify 'received', 'check' and attributes.
	"""
	authType = check.get('Auth-Type', [None])[0]
	if authType == 'simplebill':
		return True
	else:
		return False

#
# accounting function
#
def simplebill_funct_acct(received):
	"""Do some accounting tasks here. Log received accounting stop message,
		reduce user's balance.
		Input: (dict) received
		Output: none
	"""
	debug ("Received packet:")
	debug (received)
	# we should process only stop messages 
	if received['Acct-Status-Type'] == ['Stop']:
		debug ('Accounting Stop Message Received')
		# Select account data. No password is present in accounting message 
		check_password = False
		account = simplebill_get_account(received, check_password)
		debug ("Account")
		debug (account)
		if account:
			debug ('Account found')
			# now lets see if it call admission message 
			if received['Acct-Status-Type'] == ['Stop']:
				# Call admission stage - we should check for entry in rate table
				debug ('Accounting Stop Message Received')
				rate = simplebill_get_rate(account, received)
				debug ("Rate")
				debug (rate)
				# set up defaults
				if not 'h323-connect-time' in received:
					received['h323-connect-time'] = received['h323-setup-time']
				tmp = {} # use temporary storage to avoid messing up received attributes
				tmp['h323-setup-time'] = parseDatetime(received.get('h323-setup-time', [''])[0])
				tmp['h323-connect-time'] = parseDatetime(received.get('h323-connect-time', [''])[0])
				tmp['h323-disconnect-time'] = parseDatetime(received.get('h323-disconnect-time', [''])[0])
				for key, value in tmp.iteritems():
					if value != None:
						received[key] = str(value)
				# detect calling IP properly
				if 'Framed-IP-Address' in received:
				    calling_ip = received['Framed-IP-Address'][0]
				elif 'h323-gw-id' in received:
				    calling_ip = received['h323-gw-id'][0]
				else:
				    calling_ip = '0.0.0.0'
				# insert call into cdr table
				query = """
INSERT INTO cdr 
 (userId, setupTime, startTime, endTime, callingNum, calledNum, h323confid, duration, callingIp, calledIp)
 VALUES
 (%(userId)s, '%(setupTime)s', '%(startTime)s', '%(endTime)s', '%(callingNum)s', 
 '%(calledNum)s', '%(h323ConfId)s', %(duration)s, '%(callingIp)s', '%(calledIp)s')
""" % {
					'userId': account['userId'], 
					'setupTime': received['h323-setup-time'], 
					'startTime': received['h323-connect-time'], 
					'endTime': received['h323-disconnect-time'], 
					'callingNum': received['Calling-Station-Id'][0], 
					'calledNum': received['Called-Station-Id'][0], 
					'h323ConfId': received['h323-conf-id'][0], 
					'duration': received['Acct-Session-Time'][0], 
					'callingIp': calling_ip, 
					'calledIp': received['h323-remote-address'][0]}
				dbh = DatabaseConnection.getHandler('simplebill')
				insertCdr = dbh.execute(query)
				# update balance after call
				# if duration is less than grace, do not charge the call
				if received['Acct-Session-Time'][0] <= rate['grace']:
					amount = 0
					bill_dur = 0
				else:
					if received['Acct-Session-Time'][0] < rate['minDur']: # roundup to minDur
						bill_dur = rate['minDur']
					if received['Acct-Session-Time'][0] < rate['increment']: # should not be shorter than increment
						bill_dur = rate['increment']
					bill_dur = received['Acct-Session-Time'][0]
					#set to correct value because of call increment
					amount = 0
					iii = bill_dur % rate['increment']
					jjj = 0
					if iii > 0:
						jjj = rate['increment'] - iii
					bill_dur += jjj
					#calculate billed amount:
					amount += bill_dur * rate['ratePerMinute']
					amount /= 60 #call charging per minute not per second
					amount += rate['ratePerCall'] #charge call with rate per call
					# update account balance
					query = """
UPDATE users SET balance = balance - %s WHERE userId = %s
""" % (amount, account['userId'])
					updateAcct = dbh.execute(query)
				return True
		else: 
			debug ('Account not found')
			# Return false if account not found. This will allow dump_packet module
			# to log failed accounting packets for later investigation 
			return False
	else:
		debug ('This is not Accounting Stop Message, do nothing')
		return True
#
# shutdown function - closes db connections
#
def simplebill_funct_shutdown():
	"""Close database connections
		Input: none
		Output: none
	"""
	info ("Shutting down database connections")
	dbh = DatabaseConnection.getHandler('simplebill')
	dbh.disconnect()

#
# function to find account based on received radius packet
# 
def simplebill_get_account(received, check_password):
	# if authType is not set we need to check password field as well
	if check_password:
		passwd_check = " AND password= '%s' "  % received['User-Password'][0]
	else:
		passwd_check = ""
	query = """
SELECT name, password, status, rateTableId, balance , userId
 FROM users 
 WHERE name= '%s' 
  %s
  AND status = 1 
""" % (received['User-Name'][0],passwd_check)
	dbh = DatabaseConnection.getHandler('simplebill')
	acctData = dbh.execGetRowsOne(query)
	if acctData:
		account = {
			'User-Name': acctData[0], 
			'User-Password': acctData[1],
			'rateTableId': acctData[3],
			'balance': acctData[4], 
			'userId': acctData[5]}
	else:
		account = []
	return account

#
# function to find rate
#
def simplebill_get_rate(account, received):
	dbh = DatabaseConnection.getHandler('simplebill')
	query = """
SELECT ratePerMinute, ratePerCall, increment, grace, minDur,
 userId, s1.rateTableId, s3.destCode
 FROM users s1 
 LEFT JOIN rateItems s2 ON s1.rateTableId = s2.rateTableId 
 LEFT JOIN destCodes s3 ON s3.destinationId=s2.destinationId 
 WHERE s1.userId = %s 
  AND s1.rateTableId = %s 
  AND s2.status = 1 
  AND s3.destCode = left('%s',length(s3.destCode)) 
 ORDER BY length(s3.destCode) DESC LIMIT 1 
""" % (account['userId'], account['rateTableId'], received['Called-Station-Id'][0])
	rateData = dbh.execGetRowsOne(query)
	if rateData:
		rate = {
			'ratePerMinute': rateData[0],
			'ratePerCall': rateData[1],
			'increment': rateData[2],
			'grace': rateData[3],
			'minDur': rateData[4]}
	else:
		rate = []
	return rate
```