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
Data Tech Labs database connection module.
Works as abstraction layer between database driver
and application. Database driver must be Python
DBAPI-2.0 capable.

Global configuration variables with defaults:

# database adapter name (name of db driver module)
dbadapterName = None

# define global accessible database handlers
# example: 
import DatabaseConnection
DatabaseConnection.dbadapterName = 'psycopg'
dbh1 = DatabaseConnection.DatabaseConnection.getHandler('dbh1')
dbh1.connect('localhost', 'root', '', '')
dbh2 = DatabaseConnection.DatabaseConnection.getHandler('dbh2')
dbh2.connect('')
	
# later in code, in other modules:
from DatabaseConnection import DatabaseConnection
dbh1 = DatabaseConnection.getHandler('dbh1')
dbh1.displayHandlerName()

"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_4/bsdradius/DatabaseConnection.py $
# Author:		$Author: valts $
# File version:	$Revision: 201 $
# Last changes:	$Date: 2006-04-04 17:22:11 +0300 (Ot, 04 Apr 2006) $


# Import database adapter(module that interfaces specific db engine)
#   Import all db adapter module namespace in current namespace
#   use dbadapterName as constant which contains db adapter name

# dbadapterName = 'MySQLdb' # mysql
# dbadapterName = 'psycopg' # postgresql (http://initd.org/software/psycopg)
dbadapterName = None


# DTL modules
from bsdradius.logger import *
from bsdradius import misc
# standard modules
import re
import types
import sys, traceback



class DatabaseConnection:
	"""Derived class for connection to abstract database engine
		Has to be derrived class from one of DB engine
		specific base classes (ex.: PgsqlDatabaseConnection)
	"""

	# when there is no name passed to constructor we shoulduse numeric id instead of name
	# this attribute contains the largest already assigned id
	_handlerTopId = -1
	# must contain all handler instances
	# used for easier DatabaseConnection sharing between modules
	handlers = {}

	### Class methods ###
	def __init__ (self, name = None, _dbadapterName = None):
		"""Constructor which opens connection if neccessary parameters received
			Input: (string) instance name, default: 0,1,2,... ;
				(string) dbadapterName module name, default: module global dbadapterName
			Output: (DatabaseConnection) class instance
		"""
		
		# import db adapter (driver)
		if _dbadapterName:
			self._dbadapterName = _dbadapterName # use local value
		elif dbadapterName:
			self._dbadapterName = dbadapterName # use global value
		else:
			raise ValueError, "Invalid dbadapterName value. Local: %s; global: %s" % (_dbadapterName, dbadapterName)
		self._dbadapter = __import__ (self._dbadapterName)

		# set defaults
		self._conn 		= None	# connection handler
		self._cursor	= None	# db cursor (usable after query execute)
		self._errorStr	= ""	# last error text string
		self._errorCode	= 0		# last error code (0 - no error)
		self._connected	= False
		
		# Set handler's name to given value or choose id next to previous existing one.
		# Avoid using name or id that is already in handlers dictionary. That should make
		# debugging easier.
		if name != None:
			if name in DatabaseConnection.handlers:
				raise ValueError, 'DatabaseConnection instance name "%s" already in use' % name
			self._name	= name # connection handler name for printing in debug messages
		else:
			DatabaseConnection._handlerTopId += 1
			while DatabaseConnection._handlerTopId in DatabaseConnection.handlers:
				DatabaseConnection._handlerTopId += 1
			self._name = DatabaseConnection._handlerTopId



	@classmethod
	def getHandler(cls, name = None, _dbadapterName = None):
		"""Get DatabaseConnection instance by name or id
			Input: (mixed) DatabaseConnection instance name (that one
				which you passed to constructor
			Output: (DatabaseConnection) class instance
		"""
		# prepare name for searching the handler
		searchName = name
		if searchName == None:
			searchName = 0
			
		# create new class instance if neccessary
		# if something goes wrong there should be an exception raised
		if searchName not in cls.handlers:
			handler = cls(name, _dbadapterName)
			cls.handlers[handler._name] = handler
		
		return cls.handlers[searchName]



	def connect(self, host, user, password, dbname, autocommit = True):
		"""Connect to database
			Constructor which opens connection if neccessary parameters received
			Input: (string) host, (string) username, (string) password, (string) database name;
				(bool) autocommit, True- enable, False - disable, default: True
			Output: none
			Prints error and raises an exception again if unsuccessful.
		"""
		info("db>> Connecting to database")
		self.displayHandlerName()
		loginStr = "host=%s user=%s password=%s dbname=%s" % (host, user, password, dbname)
		
		usingPassword = 'yes'
		if not password:
			usingPassword = 'no'
		debug('db>> host: ',host,'; db: ',dbname,'; user: ',user,'; using password: ',usingPassword)
		
		# try to open connection
		try:
			if dbadapterName == 'MySQLdb':
				self._conn = self._dbadapter.connect(host, user, password, dbname)
			else:
				self._conn = self._dbadapter.connect(loginStr)
		# catch all exceptions
		except:
			exc_value = sys.exc_info()[1]
			error('db>> Can not connect to database: %s' % exc_value)
			raise
		else:		
			# continue if connection successful
			self._connected = True
			# create new cursor
			self._cursor = self._conn.cursor()
			# store access details for possible reconnect needs
			self._host		= host
			self._user		= user
			self._password	= password
			self._dbname	= dbname
			# set autocommit
			if autocommit:
				self._conn.autocommit(1)
			else:
				self._conn.autocommit(0)



	def reconnect(self):
		"""reconnect to database in case when connection is lost
			between to requests to radius
		"""
		self.__init__() # set everything to default
		self.disconnect()
		self.connect(self._host, self._user, self._password, self._dbname) # reconnect



	def disconnect(self):
		"""Disconnect from database"
			Input: none
			Output: none
		"""
		
		self.displayHandlerName()
		if (self._connected):
			try:
				self._cursor.close()
			except:
				error('db>> Error closing cursor to DB')
			try:
				self._conn.close()
			except:
				error('db>> Error closing connection to DB')
				misc.printException()
				
			self._errorStr = ''
			self._errorCode = 0
			self._connected = False
		else:
			error('db>> Already disconnected from DB')



	def execute(self, query, verbose = True):
		"""Prepare and execute query
			Input: (string) query, (bool) be verbose and print some useful info
			Output: (bool) True if query execution was succssful, False if not
		"""
		
		ret = False # return value
		if (not query): return ret
		
		if (verbose):
			self.displayHandlerName()
			debug ('db>> QUERY: ', query)
		
		# execute query
		try:
			self._cursor.execute(query)
		except:
			error ('db>>ERROR: Could not execute query: ', query)
			misc.printException()
		else:
			ret = True
		
		return ret
	
	
	
	def execProcedure(self, procName):
		"""Execute stored procedure in DB.
			Input: (string) procedure name
			Output: (bool) True if procedure call was successful, False if not
		"""
		
		ret = False
		if (not procName): return ret
		
		self.displayHandlerName()
		
		# call procedure
		try:
			self._cursor.callproc(procName)
		except:
			error ('db>>Error Could not execute stored procedure: ', procName)
			misc.printException()
		else:
			ret = True
		
		return ret
	
	
	
	def begin(self):
		"""Begin transaction
			Input: none
			Output: none
			Should raise exception if unsuccessful.
		"""
		self.execute('BEGIN')
	
	
	
	def commit(self):
		"""Commit changes to DB
			Input: none
			Output: none
			Should raise exception if unsuccessful.
		"""
		self.displayHandlerName()
		self._conn.commit()
		
		
	def rollback(self):
		"""Rollback any changes to the point of last commit
			Input: none
			Output: none
			Should raise exception if unsuccessful.
		"""
		self.displayHandlerName()
		self._conn.rollback()
	
	
	
	@classmethod
	def quote(cls, dirtyStr):
		"""Quote string with single quotes and escape special characters
			Input: (string) string for quoting
			Output: (string) quoted and escaped string
		"""
		ret = str(dirtyStr)
		ret = re.sub(r'\\', '\\\\', ret) # escape backslashes
		ret = re.sub(r'\'', '\\\'', ret) # escape single quote
		ret = re.sub(r'\000', '\\\000', ret) # escape null character
		ret = re.sub(r'\032', '\\\032', ret) # escape ctrl+z
		return ret
	



	def execGetDict(self, query, printRes = True):
		"""Execute query and fetch all rows from result in list of dictionaries
			Input: (string) query, (int)
			Output: (list(dict)) data or None if failure
		"""
		ret = None
		if (self.execute(query, printRes)):
			ret = self._cursor.dictfetchall()
			if (printRes):
				for row in ret:
					debug ('db>> ', row)
		return ret



	def execGetDictOne(self, query, printRes = True, freeRes = True):
		"""Execute query and fetch one row from result in dictionary
			Input: (string) query
			Output: (dict) data or None if failure
		"""
		ret = None
		if (self.execute(query, printRes)):
			ret = self._cursor.dictfetchone()
			if (freeRes): self.freeResult()
			if (printRes): debug ('db>> ', ret, '\n')
		return ret
	
	
	
	def execGetRows(self, query, printRes = True):
		"""Execute query and fetch all rows from result in 2 dimensional array (list)
			Input: (string) query
			Output: (list) data or None if failure
		"""
		ret = None
		if (self.execute(query, printRes)):
			ret = self._cursor.fetchall()
			if (printRes):
				for row in ret:
					debug ('db>> ', row)
		return ret
	
	
	
	def execGetRowsOne(self, query, printRes = True, freeRes = True):
		"""Execute query and fetch one row from result in 1 dimensional array (list)
			Input: (string) query
			Output: (list) data or None if failure
		"""
		ret = None
		if (self.execute(query, printRes)):
			ret = self._cursor.fetchone()
			if (freeRes): self.freeResult()
			if (printRes): debug ('db>> ', ret, '\n')
		return ret
	
	
	
	def freeResult(self):
		"""Free result data set
			Input: none
			Output: none
		"""
		pass



	def getError(self):
		"""Get Error message
			Input: none
			Output: (string) error message
		"""
		return self._errorStr



	def getErrorCode(self):
		"""Get error code
			Input: none
			Output: (int) error code
		"""
		return self._errorCode
	


	def getAffectedRowCount (self):
		"""Get number of affeced rows during executing last query
			Input: none
			Output: (int) number of rows
		"""
		self.displayHandlerName()
		return self._cursor.rowcount



	def getLastInsertId(self, sequence):
		"""Get lst inserted row id
			Input: none
			Output: (int) row id
		"""
		self.displayHandlerName()
		query = "SELECT currval('%s') AS last" % sequence
		return self.execGetRowsOne(query)[0]



	def isConnected(self):
		"""Clarify if connection is active
			Input: none
			Output: (bool) true - connected, false - disconnected
		"""
		return self._connected



	def checkConnection(self):
		"""Check connection to DB
			Input: none
			Output: (bool) True - ok, False - Failure
		"""
		info ('db>> Checking DB connection')
		if self.execute('select 1'):
			return True
		else:
			return False


	def getHandlerName(self):
		"""Get current handler's name
			Input: none
			Output: (string) name
		"""
		return str(self._name)



	def displayHandlerName(self):	
		"""Display connection handler name
			Input: (none)
			Output: (none)
		"""
		if self._name != None:
			debug ('db>> Using connection handler "%s"' % self.getHandlerName())
