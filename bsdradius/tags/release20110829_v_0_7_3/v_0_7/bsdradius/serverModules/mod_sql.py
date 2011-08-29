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
BSDRadius module for user database access
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_7/bsdradius/serverModules/mod_sql.py $
# Author:		$Author: valts $
# File version:	$Revision: 219 $
# Last changes:	$Date: 2006-05-19 14:43:46 +0300 (Pk, 19 Mai 2006) $


import exceptions
from string import Template
import re, datetime
from types import *
# you can use functions defined in logger module to use BSD Radius's
# logger system.
from bsdradius.logger import *
from bsdradius.DatabaseConnection import DatabaseConnection
from bsdradius.misc import parseDatetime


class ModsqlError(exceptions.Exception):
	pass



def startup():
	"""Open sql connection
		Input: none
		Output: none
	"""
	info ('Opening database connections')
	sqlAccess = radParsedConfig['ACCESS']
	
	# detect database driver name and open connection
	if sqlAccess['type'] == 'postgresql':
		dbadapterName = 'psycopg'
	else:
		dbadapterName = 'MySQLdb'
	dbh = DatabaseConnection.getHandler('mod_sql_1', dbadapterName)
	dbh.connect(host = sqlAccess['host'], user = sqlAccess['user'],
		password = sqlAccess['pass'], dbname = sqlAccess['name'])
	
	

def authorization(received, check, reply):
	"""Find user in database
		Input: (dict) received data, (dict) check data, (dict) reply data
		Output: (bool) True - success, False - failure
	"""	
	# translate "-" to "_" in request attributes
	attrs = translateAttrs(received)
	
	queryTpl = radParsedConfig['AUTHORIZATION'].get('authz_query', None)
	if queryTpl == None:
		return
	
	# Select account data.
	# It is advisable to select username and password as 1st two attributes
	# for modules which require them in authentication (chap, digest)
	dbh = DatabaseConnection.getHandler('mod_sql_1')
	query = Template(queryTpl).substitute(attrs) # use request items for keyword replacement
	acctData = dbh.execGetRowsOne(query)
	if acctData:
		debug ('Account found')
		authType = check.get('Auth-Type', [None])[0]		
		if not authType:
			# just set the auth type to "sql" if no previous modules have touched it.
			check['Auth-Type'] = ['sql']
		elif len(acctData) >= 2:
			# pass username and password to module which has set up it's auth type.
			check['User-Name'] = [acctData[0]]
			check['User-Password'] = [acctData[1]]
	else:
		debug ('Account not found')
	# Return true even if account not found. Leave chance for other modules to
	# find the user.
	return True



def authentication(received, check, reply):
	"""Tell the server that user is ok
		Input: (dict) received data, (dict) check data, (dict) reply data
		Output: (bool) True - success, False - failure
	"""
	authType = check.get('Auth-Type', [None])[0]
	if authType == 'sql':
		return True
	else:
		return False



def accounting(received):
	"""Log data of completed session (call).
		Input: (dict) received data
		Output: none
	"""
	dbh = DatabaseConnection.getHandler('mod_sql_1')
	
	acctType = received.get('Acct-Status-Type', [None])[0]
	if not acctType:
		raise ModsqlError, 'Acct-Status-Type not found in request'
	debug ('Accounting %s message received' % acctType)
	
	supportedAcctTypes = ['Start', 'Alive', 'Stop']
	if acctType not in supportedAcctTypes:
		return
	
	# translate "-" to "_" in request attributes
	attrs = translateAttrs(received)
	# Parse date and time from cisco format to datetime class when using
	# mysql. There are no problems with postgresql however.
	# This should be done for users who want to log call start and end times into
	# database. Since they can wish to log these attributes during any type of
	# request, we should always parse them.
	if radParsedConfig['ACCESS']['type'] != 'postgresql':
		tmp = {} # use temporary storage to avoid messing up received attributes
		tmp['h323_setup_time'] = parseDatetime(attrs.get('h323_setup_time', ''))
		tmp['h323_connect_time'] = parseDatetime(attrs.get('h323_connect_time', ''))
		tmp['h323_disconnect_time'] = parseDatetime(attrs.get('h323_disconnect_time', ''))
		for key, value in tmp.iteritems():
			if value != None:
				attrs[key] = str(value)
	
	# get sql query template based on Acct-Status-Type parameter
	queryTpl = None
	if acctType == 'Start':
		queryTpl = radParsedConfig['ACCOUNTING'].get('acct_start_query', None)
	elif acctType == 'Alive':
		queryTpl = radParsedConfig['ACCOUNTING'].get('acct_update_query', None)
	elif acctType == 'Stop':
		queryTpl = radParsedConfig['ACCOUNTING'].get('acct_stop_query', None)
	
	# check and parse query template
	if queryTpl == None:
		return
	query = Template(queryTpl).substitute(attrs) # use request items for keyword replacement
	
	# execute query
	success = dbh.execute(query)
	if not success:
		raise ModsqlError, "Error executing accounting %s SQL query" % acctType



def shutdown():
	"""Close database connections
		Input: none
		Output: none
	"""
	info ("Shutting down database connections")
	dbh = DatabaseConnection.getHandler('mod_sql_1')
	dbh.disconnect()



def translateAttrs(received):
	"""Tanslate attribute names replacing "-" with "_". It is neccessary
		because we use Template objects for sql queries. Template doesn't
		accept "-" symbols in keyword names.
		Input: (dict) request data
		Output: (dict) request data with translated attribute names.
	"""
	attrs = {}
	for key, value in received.iteritems():
		key = key.replace('-', '_')
		attrs[key] = DatabaseConnection.quote(value[0])
	return attrs
