"""
Session stuff

create()
find()
getData()
renew()
delete()
deleteOld()
storeInMemory()
storeInFile()
storeInDb()
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/webstuff/tags/release20061229_v_1_0_0/webstuff/sessions.py $
# Author:		$Author: atis $
# File version:	$Revision: 45 $
# Last changes:	$Date: 2006-06-05 13:54:09 +0300 (Pr, 05 Jūn 2006) $


import time, exceptions
import shelve
import tools, db
# get pickle
try:
	import cPickle as pickle
except:
	import pickle


# storage engine types
STORE_MEMORY = 1
STORE_FILE = 2
STORE_DATABASE = 3

# session storage engine by default is RAM
storageEngine = STORE_MEMORY

# session in-memory storage
# stores: sessionId : (clientIP, expireTime)
memoryStorage = {}

# session file storage.
# this is dictionary like object which behaves very like memoryStorage
fileStorage = None

# sqlalchemy.Table class instance for connection to database
# all session data should be stored in this table
dbStorage = None

# table field mapping
fieldMap = {}
# prepared sql queries
query = {}
# prepared table column instances
columns = {}

# Set to False to disable using precompiled select queries. Changing this option
# has no effect on other types of SQL queries. This option is neccessary because
# pysqlite is dumb enough that it doesn't support executemany() on select statements.
optimizeSelectQueries = True

# web module instance
# neccessary for getting access to request data
web = None

# session cookie name
cookieName = 'WEBSTUFF_SESSION_ID'

# default data structure for session metadata
# data structure: user id, user IP address, expiry timestamp, session timeout, additional attributes
defaultData = [None, None, 0, 0, None]

# default (name => column name) table field mapping for session storage in db
defaultFieldMapping = {
	'session_id' : 'session_id',
	'user_id' : 'user_id',
	'user_ip_address' : 'user_ip_address',
	'exp_timestamp' : 'exp_timestamp',
	'timeout' : 'timeout',
	'additional_data' : 'additional_data',
}

# exception class for handling "no db access" error
class StorageEngineError(Exception):
	pass



def create(userId = None, length = 50, timeout = 3600, additionalData = None,
		setCookie = True, cookiePath = '/'):
	"""Create new session
		Input:(mixed) something that identifies user;
			(int) session id length,
			(int) user session timeout in sseconds
		Output: (string) session id
	"""
	sessionId = tools.randString(length)
	expTimestamp = time.time() + timeout
	userIpAddress = web.getvar_env('REMOTE_ADDR')
	#userXForwardedIp = web.getvar_env('XFORWARDED_CLIENT_IP')
	sessionData = [userId, userIpAddress, expTimestamp, timeout, additionalData]
	
	# delete expired sessions
	deleteOld()
	
	# store session data in memory
	if storageEngine == STORE_MEMORY and sessionId not in memoryStorage:
		memoryStorage[sessionId] = sessionData
	# store session data in file
	elif storageEngine == STORE_FILE and sessionId not in fileStorage:
		fileStorage[sessionId] = sessionData
	# store session in database
	elif storageEngine == STORE_DATABASE:
		values = {
			fieldMap['session_id']: sessionId,
			fieldMap['user_ip_address']: userIpAddress,
			fieldMap['exp_timestamp']: expTimestamp,
			fieldMap['timeout']: timeout
		}
		if userId != None:
			values[fieldMap['user_id']] = userId
		if additionalData != None:
			values[fieldMap['additional_data']] = pickle.dumps(additionalData)
			
		dbStorage.engine.begin()
		query['new'].execute(values)
		dbStorage.engine.commit()
	
	# store session id in cookie
	if setCookie:
		web.setcookie(name = cookieName, value = sessionId, path = cookiePath)
	
	return sessionId


	
def find(sessionId = None):
	"""Perform lookup in session database and returns session id if found.
		If given session id in parameters is None then look for session id
		in cookies.
		Input: (string) session id, pass None to look for session id in cookie
		Output: (string) session id or None if not found
	"""
	if sessionId == None:
		# get session id from cookie
		sessionId = web.getvar_cookie(cookieName, None)
		if sessionId == None:
			return None
		
	# look for session in storage, get expiry timestamp
	expTimestamp = 0
	clientIP = None
	if storageEngine == STORE_MEMORY and sessionId in memoryStorage:
		clientIP, expTimestamp = memoryStorage[sessionId][1:3]
	elif storageEngine == STORE_FILE and sessionId in fileStorage:
		clientIP, expTimestamp = fileStorage[sessionId][1:3]
	elif storageEngine == STORE_DATABASE:
		if optimizeSelectQueries:
			row = query['find'].execute({'sesid': sessionId}).fetchone()
		else:
			row = dbStorage.select(columns['session_id'] == sessionId).execute().fetchone()
		if not row:
			return None
		clientIP = row[fieldMap['user_ip_address']]
		expTimestamp = row[fieldMap['exp_timestamp']]
	else:
		return None
	
	# check if session expired
	if time.time() > expTimestamp:
		return None
		
	# check if user ip address is still the same
	if clientIP != web.getvar_env('REMOTE_ADDR') or clientIP == None:
		return None
	
	# return session ID if everything was ok
	return sessionId


def getData(sessionId = None):
	"""Perform lookup in session database searching by session id
		Input: (string) session id. If None, we'll look for WEBSTUFF_SESSION_ID
			in cookie
		Output: (tuple) session data, empty if session not found
	"""
	# clarify if session id is in storage and session is not expired
	sessionId = find(sessionId)
	if sessionId == None:
		return defaultData
	
	# look for session data in storage
	if storageEngine == STORE_MEMORY:
		return memoryStorage.get(sessionId, defaultData)
	elif storageEngine == STORE_FILE:
		return fileStorage.get(sessionId, defaultData)
	elif storageEngine == STORE_DATABASE:
		if optimizeSelectQueries:
			row = query['find'].execute({'sesid': sessionId}).fetchone()
		else:
			row = dbStorage.select(columns['session_id'] == sessionId).execute().fetchone()
		if not row:
			return defaultData
		# convert sql query results to list
		# we need to use fieldMap to provide compatibility with user defined tables
		sesData = []
		sesData.append(row[fieldMap['user_id']])
		sesData.append(row[fieldMap['user_ip_address']])
		sesData.append(row[fieldMap['exp_timestamp']])
		sesData.append(row[fieldMap['timeout']])

		data = row[fieldMap['additional_data']]
		if data != None:
			sesData.append(pickle.loads(str(data))) # unpickle additional session data
		return sesData # return everything except session id itself
	else:
		return defaultData


def renew(sessionId = None):
	"""Reset session exp time making it valid for longer time
		Input: (string) session id, pass None to look for session id in cookie
	"""
	sessionId = find(sessionId)
	if sessionId == None:
		return

	# renew session resetting it's expiry time to current time + timeout
	if storageEngine == STORE_MEMORY:
		timestamp = memoryStorage[sessionId][3]
		memoryStorage[sessionId][2] = time.time() + timestamp
	elif storageEngine == STORE_FILE:
		# since file storage contains pickle objects it is not possible to
		# directly change contents of deeper object structures. So we have
		# to rewrite whole session data list
		sessionData = fileStorage[sessionId]
		timestamp = sessionData[3]
		sessionData[2] = time.time() + timestamp
		fileStorage[sessionId] = sessionData
	elif storageEngine == STORE_DATABASE:
		query['renew'].execute({'sesid': sessionId, 'tm': time.time()})
		

def delete(sessionId = None):
	"""Delete session from storage
		Input: (string) session id, pass None to look for session id in cookie
		Output: none
	"""
	# Try to get sessions id from request data variables if not
	# passed to function
	if sessionId == None:
		sessionId = web.getvar('WEBSTUFF_SESSION_ID')
		if sessionId == None:
			return
	
	# delete from memory storage
	if storageEngine == STORE_MEMORY and sessionId in memoryStorage:
		del memoryStorage[sessionId]
	elif storageEngine == STORE_FILE and sessionId in fileStorage:
		del fileStorage[sessionId]
	elif storageEngine == STORE_DATABASE:
		query['delete'].execute({'sesid': sessionId})


def deleteOld():
	"""Delete expired sessions
		Input: none
		Output: none
	"""
	if storageEngine == STORE_MEMORY:
		for sessionId, tokens in memoryStorage.iteritems():
			if tokens[2] < time.time():
				del memoryStorage[sessionId]
	elif storageEngine == STORE_FILE:
		for sessionId, tokens in fileStorage.iteritems():
			if tokens[2] < time.time():
				del fileStorage[sessionId]
	elif storageEngine == STORE_DATABASE:
		query['delete_old'].execute({'exp_ts' : time.time()})


def storeInMemory():
	"""Store session data in memory
		Input: none
		Output: none
	"""
	global storageEngine
	storageEngine = STORE_MEMORY

	
def storeInFile(filename = "webstuff_sessions.dat"):
	"""Store session data in file
		Input: (string) filename, default: webstuff_sessions.dat
		Output: none
	"""
	global storageEngine
	storageEngine = STORE_FILE
	global fileStorage
	fileStorage = shelve.open(filename)
	

def storeInDb(table, fieldMapping = defaultFieldMapping):
	"""Store session data in SQL database
		Input: (sqlalchemy.Table) table instance;
			(dict) field name mapping, see defaultFieldMapping to get clue
		Output: none
	"""
	if not db.hasDbaccess:
		raise StorageEngineError, "Database access not supported. You can not store sessions in database."
	
	global storageEngine, dbStorage, fieldMap
	storageEngine = STORE_DATABASE
	dbStorage = table
	fieldMap = fieldMapping
	
	# prepare column instances
	for name, colName in fieldMap.iteritems():
		columns[name] = dbStorage.columns[colName]
		
	# prepare queries
	if dbStorage.engine.name == db.T_SQLITE:
		global optimizeSelectQueries
		optimizeSelectQueries = False
	else:
		query['find'] = dbStorage.select(columns['session_id'] == db.bindparam('sesid'))
	
	query['new'] = dbStorage.insert()
	query['renew'] = dbStorage.update(columns['session_id'] == db.bindparam('sesid'),
		values = {columns['exp_timestamp']: columns['exp_timestamp'] + db.bindparam('tm')})
	query['delete'] = dbStorage.delete(columns['session_id'] == db.bindparam('sesid'))
	query['delete_old'] = dbStorage.delete(columns['exp_timestamp'] < db.bindparam('exp_ts'))
