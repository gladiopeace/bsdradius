"""
Webstuff database module. It imports all functions, classes and variables from
sqlalchemy so you are able to use them directly from db module.
NOTE: plase don't use filename ":memory:" for sqlite. It is not supported in 
multithreaded environment.
"""

# HeadURL		$HeadURL: svn://alpha:33033/megabox/trunk/web_modules/calls.py $
# Author:		$Author: valts $
# File version:	$Revision: 1831 $
# Last changes:	$Date: 2006-05-17 16:46:35 +0300 (Wed, 17 May 2006) $


from ThreadStore import ThreadStore
from logger import *
import thread
import webstuff


# Indicates if tables are prefixed by default or not.
hasPrefixDefault = False


try:
	import sqlalchemy.engine
	original_SQLEngine = sqlalchemy.engine.SQLEngine
	hasDbaccess = True
except:
	original_SQLEngine = object
	hasDbaccess = False
	warning ("Could not import sqlalchemy. Database support disabled.")
	

class WebstuffSqlEngine(original_SQLEngine):
	"""Wrapper to sqlalchemy's SQLEngine class.
		WebstuffSqlEngine adds getTable method for easier operations when using
		EnginePool.
	"""
	def __init__(self, *params, **kwords):
		if not hasDbaccess:
			return
		original_SQLEngine.__init__(self, *params, **kwords)
		self.loadedTables = {}
	
	
	def getTable(self, name, tableName = None, hasPrefix = None):
		"""Get a Table object from database engine.
			Input: (string) table name;
				(string) table name in DB;
				(bool) True table name has prefix, False - table name has no prefix.
			Output: (sqlalchemy.Table) table instance
		"""
		if not hasDbaccess:
			return
		
		# set sql table name to local table name if SQL table name not given
		if tableName == None:
			tableName = name
		
		# get prefix and adjust SQL table name if needed
		if hasPrefix is None:
			hasPrefix = hasPrefixDefault
		prefix = None
		if hasPrefix == True:
			prefix = getTablePrefix()
			tableName = prefix + tableName
		
		try:
			# return prefixed table
			return self.loadedTables[prefix][name]
		except:
			# create new table instance
			table = Table(tableName, self, autoload = True)
			if prefix not in self.loadedTables:
				self.loadedTables[prefix] = {}
			self.loadedTables[prefix][name] = table
			return table


# HACK!!! HACK!!! HACK!!!
# replace original base class for all SQL engines with WebstuffSqlEngine
if hasDbaccess:
	sqlalchemy.engine.SQLEngine = WebstuffSqlEngine


# import all stuff from sqlalchemy in local namespace
try:
	from sqlalchemy import *
	import sqlalchemy.pool as pool
	hasDbaccess = True
except:
	hasDbaccess = False
	warning ("Could not import sqlalchemy. Database support disabled.")


# database engine types
T_POSTGRESQL = 'postgres'
T_MYSQL = 'mysql'
T_ORACLE = 'oracle'
T_SQLITE = 'sqlite'

# thread specific storage (currently only for prefixes)
storage = ThreadStore()
storage.add_thread() # add main thread by default

# sqlalchemy database engines
# Format: {'name': engine}
engines = {}

# pools of sqlalchemy database engines
# format: {'name': pool_instance}
enginePools = {}

# sqlalchemy tables
# Format: {'name': Table}
tables = {}


# exception classes
class SqliteError(Exception):
	pass
class PostgresError(Exception):
	pass
class MysqlError(Exception):
	pass
class OracleError(Exception):
	pass


# default parameters for new connections
connDefaults = {
	'host' : 'localhost', # postgresql, mysql, oracle
	'user' : 'root', # postgresql, mysql, oracle
	'password' : '', # postgresql, mysql, oracle
	'dbname' : 'webstuff', # postgresql, mysql, oracle
	'dsn' : '', # postgresql, oracle
	'filename' : 'webstuff_sqlite.db', # sqlite
	'autocommit' : True, # sqlite, postgresql
}



class getSqliteConnection:
	"""Class for getting connection to sqlite database.
		It stores sqlite.connect() parameters as local attributes.
	"""
	def __init__(self, filename = connDefaults['filename'], autocommit = connDefaults['autocommit']):
		"""Get class/function for opening connection to sqlite database.
			pysqlite2 module must be present
			Input: (dict) sqlite.dbapi2.connect() parameters
			Output: (getSqliteConnection) class instance. Use it as function
		"""
		debug ('Making sqlite')
		# Import sqlite module locally.
		# Tell the user that sqlite is not supported if import is unsuccessful.
		try:
			from pysqlite2 import dbapi2 as dbdriver
		except ImportError:
			raise SqliteError, 'Sqlite not supported. Try to install pysqlite2 Python module.'
		self.dbdriver = dbdriver
		
		# :memory: is not supported. sqlalchemy.pool.SingletonThreadPool
		# creates new connection for each thread resulting in seperate in-memory
		# databases per thread.
		if filename == ':memory:':
			raise SqliteError, 'Filename "%s" not supported in multithreaded environment' % filename
		self.filename = filename
		self.autocommit = autocommit			


	def __call__(self):
		"""Get connection to sqlite database
			Input: none
			Output: none
		"""
		debug ('Creating new SQLite connection with filename: %s' % self.filename)
		conn = self.dbdriver.connect(self.filename)
		if self.autocommit:
			conn.isolation_level = None
		return conn



class getPostgresConnection:
	"""Class for getting connection to postgresql database.
		It stores psycopg.connect() parameters as local attributes.
	"""
	def __init__(self, host = connDefaults['host'], user = connDefaults['user'],
			password = connDefaults['password'], dbname = connDefaults['dbname'],
			dsn = connDefaults['dsn'], autocommit = connDefaults['autocommit']):
		"""Get class/function for opening connection to postgresql database.
			psycopg or psycopg2 module must be installed.
			Input: (string) host, (string) username, (string) password,
				(string) database name, (string) dsn string,
				(bool) autocommit (True - enable, False - disable).
			Output: (getPostgresConnection) class instance. Use it as function
			NOTE: when dsn string given then host, username, password and database name
				parameters are totally ignored.
		"""
		# Import psycopg module locally.
		# Tell the user that postgres is not supported if import is unsuccessful.
		try:
			import psycopg2 as dbdriver
		except ImportError:
			try:
				import psycopg as dbdriver
			except ImportError:
				raise PostgresError, 'Postgresql not supported. Try to install psycopg2 or psycopg Python module.'
		self.dbdriver = dbdriver
		self.host = host
		self.user = user
		self.password = password
		self.dbname = dbname
		self.autocommit = autocommit
		
		# prepare dsn string if dsn not given already
		if not dsn:
			dsn = "host=%s user=%s password=%s dbname=%s" % (host, user, password, dbname)
		self.dsn = dsn


	def __call__(self):
		# turn on debug in logger.py to see these messages
		if self.password:
			usesPassword = 'YES'
		else:
			usesPassword = 'NO'
		debug ("Creating new PostgreSQL connection")
		debug ("  Host: %s, username: %s, database: %s" % (self.host, self.user, self.dbname))
		debug ("  Using password: %s" % usesPassword)
		
		conn = self.dbdriver.connect(self.dsn)
		if self.autocommit:
			conn.autocommit(1)
		else:
			conn.autocommit(0)
		return conn



class getMysqlConnection:
	"""Class for getting connection to mysql database.
		It stores mysqldb.connect() parameters as local attributes.
	"""
	def __init__(self, host = connDefaults['host'], user = connDefaults['user'],
			password = connDefaults['password'], dbname = connDefaults['dbname']):
		"""Get class/function for opening connection to mysql database.
			mysqldb module must be installed.
			Input: (string) host, (string) username, (string) password,
				(string) database name
			Output: (getMysqlConnection) class instance. Use it as function
		"""
		# Import mysqldb module locally.
		# Tell the user that mysql is not supported if import is unsuccessful.
		try:
			import MySQLdb as dbdriver
		except ImportError:
			raise MysqlError, 'Mysql not supported. Try to install MySQLdb Python module.'
		self.dbdriver = dbdriver
		self.host = host
		self.user = user
		self.password = password
		self.dbname = dbname


	def __call__(self):
		# turn on debug in logger.py to see these messages
		if self.password:
			usesPassword = 'YES'
		else:
			usesPassword = 'NO'
		debug ("Creating new MySQL connection")
		debug ("  Host: %s, username: %s, database: %s" % (self.host, self.user, self.dbname))
		debug ("  Using password: %s" % usesPassword)
		
		return self.dbdriver.connect(self.host, self.user, self.password, self.dbname)



class getOracleConnection:
	"""Class for getting connection to Oracle(tm) database.
		It stores connect() parameters as local attributes.
	"""
	def __init__(self, host = connDefaults['host'], user = connDefaults['user'],
			password = connDefaults['password'], dbname = connDefaults['dbname'],
			dsn = connDefaults['dsn']):
		"""Get class/function for opening connection to mysql database.
			mysqldb module must be installed.
			Input: (dict) cx_Oracle.connect() or DCOracle2.connect() parameters
			Output: (getOracleConnection) class instance. Use it as function
		"""
		# Import oracle module locally.
		# Tell the user that oracle is not supported if import is unsuccessful.
		try:
			import cx_Oracle as dbdriver
		except ImportError:
			try:
				import DCOracle2 as dbdriver
			except ImportError:
				raise OracleError, 'Oracle(tm) not supported. Try to install cx_Oracle or DCOracle2 Python module.'
		self.dbdriver = dbdriver
		self.host = host
		self.user = user
		self.password = password
		self.dbname = dbname
		self.dsn = dsn


	def __call__(self):
		# turn on debug in logger.py to see these messages
		if self.password:
			usesPassword = 'YES'
		else:
			usesPassword = 'NO'
		debug ("Creating new Oracle(tm) connection")
		debug ("  Host: %s, username: %s, database: %s" % (self.host, self.user, self.dbname))
		debug ("  Using password: %s" % usesPassword)
		raise NotImplementedError, "Oracle support not implemented yet"



class EnginePoolError(Exception):
	pass


class EnginePool(object):
	"""Pool of engines to different databases with the same content.
		One of databases is master which accepts inserts, others are slaves
		for reading only.
		Use round robin mechanism with no priorities for selecting the right engine.
	"""
	def __init__(self, masterEngine = None, slaveEngines = []):
		"""
		"""
		self._master = masterEngine
		self._slaves = slaveEngines
		self._lastSlaveId = -1
		self._lastSlaveIdLock = thread.allocate_lock()
		self._masterLock = thread.allocate_lock()
		self._slaveLock = thread.allocate_lock()
	
	
	def setMaster(self, master):
		"""Assign master engine.
			Input: (sqlalchemy.SQLEngine) sqlalchemy engine instance
			Output: None
		"""
		self._masterLock.acquire()
		self._master = master
		self._masterLock.release()
	
	
	def addSlave(self, slave):
		"""Add new slave engine instance.
			Input: (sqlalchemy.SQLEngine) sqlalchemy engine instance
			Output: None
		"""
		self._slaveLock.acquire()
		self._slaves.append(slave)
		self._slaveLock.release()
	
	
	def getMaster(self):
		"""Get master engine if it is set. If master engine is not set up
			properly (is None) then raises an exception
			Input: None
			Output: (sqlalchemy.SQLEngine) sqlalchemy engine instance
		"""
		self._masterLock.acquire()
		if self._master is not None:
			ret = self._master
			self._masterLock.release()
			return ret
		else:
			self._masterLock.release()
			raise EnginePoolError('Master database engine not set')
	
	
	def getSlave(self, id = None):
		"""Get slave engine if any are set up. If list of slave engines is empty
			then raises an exception.
			Input: (int) engine id (optional)
			Output: (sqlalchemy.SQLEngine) sqlalchemy engine instance
		"""
		self._slaveLock.acquire()
		# raise exception if slave list is empty
		if not self._slaves:
			self._slaveLock.release()
			raise EnginePoolError('Slave database engines not set')
		# try to return specified engine
		if id is not None:
			try:
				ret = self._slaves[id]
				self._slaveLock.release()
				return ret
			except IndexError:
				self._slaveLock.release()
				raise EnginePoolError('Slave connection with id: %s doesn\'t exist')
			except:
				self._slaveLock.release()
				raise
		
		# get slave engine id for round robin
		self._lastSlaveIdLock.acquire()
		if self._lastSlaveId >= len(self._slaves) - 1:
			self._lastSlaveId = 0
		else:
			self._lastSlaveId += 1
		id = self._lastSlaveId
		self._lastSlaveIdLock.release()
		
		# return engine instance using round robin 
		try:
			ret = self._slaves[id]
			self._slaveLock.release()
			return ret
		except:
			self._slaveLock.release()
			raise



def createEngine(dbtype = T_POSTGRESQL, poolParams = {}, engineParams = {}, **params):
	"""Set up the global database engine object.
		Input: (string) database type,
			(dict) various parameters for sqlalchemy pool class constructors;
			(dict) various parameters for sqlalchemy.create_engine();
			Various parameters for connecting to database:
				(string) db host (postgresql, oracle, mysql);
				(string) db user (postgresql, oracle, mysql);
				(string) db user (postgresql, oracle, mysql);
				(string) db name (postgresql, oracle, mysql);
				(string) dsn name (postgresql, oracle);
				(string) filename (sqlite), ":memory:" not supported
		Output: (sqlalchemy.SQLEngine) sqlalchemy engine instance
	"""
	if not hasDbaccess:
		return
	
	supportedTypes = [T_POSTGRESQL, T_MYSQL, T_ORACLE, T_SQLITE]
	if dbtype not in supportedTypes:
		raise ValueError, 'Database type "%s" not supported' % supportedTypes
	
	# set logging facility to default debug output from webstuff.logger
	if not 'logger' in engineParams:
		engineParams['logger'] = debugOutput

	pl = getPool(dbtype, params, poolParams)
	engine = create_engine(dbtype, params, pool = pl, **engineParams)
	return engine



def getEngine(name = None, **params):
	"""Get database engine by name. If engine with such name doesn't
		exists new instance is created.
		Input: (string) engine name, various parameters for createEngine()
		Output: (sqlalchemy.SQLEngine) sqlalchemy engine instance
	"""
	debug ('Looking for DB engine with name: %s' % name)
	try:
		return engines[name]
	except KeyError:
		engine = createEngine(**params)
		engines[name] = engine
		return engine



def getEnginePool(name = None, engineConfig = [], addSlaveAutomagically = True):
	"""Get database engine pool. Use this pool for advanced scaling needs.
		Input: (string) engine name;
			(list) list of dictionaries wich consist of all neccessary
				parameters for createEngine(). The first element in list is
				always considered as configuration for master database;
			(bool) enable/disable hack for adding slave db config entry
				automatically when there is only master db config available
	"""
	debug ('Looking for DB engine pool with name: %s' % name)
	try:
		return enginePools[name]
	except KeyError:
		# HACK!!! Add entry for slave db config if only master config is given.
		if addSlaveAutomagically and len(engineConfig) == 1:
			engineConfig.append(engineConfig[0])
		# create neccessary engine instances
		engines = []
		for attrs in engineConfig:
			engines.append(createEngine(**attrs))
		masterEngine = engines.pop(0)
		engPool = EnginePool(masterEngine = masterEngine,
			slaveEngines = engines)
		enginePools[name] = engPool
		return engPool



def getPool(dbtype, params, poolParams):
	"""Get connection pool. Defines getConnection method based on db type
		Input: (string) database type, (dict) connect() parameters,
			(dict) pool constructor parameters.
		Output: (class) pool instance
	"""
	if dbtype == T_POSTGRESQL:
		funct = getPostgresConnection(**params)
		return pool.QueuePool(creator = funct, **poolParams)
	elif dbtype == T_MYSQL:
		funct = getMysqlConnection(**params)
		return pool.QueuePool(creator = funct, **poolParams)
	elif dbtype == T_ORACLE:
		funct = getOracleConnection(**params)
		return pool.QueuePool(creator = funct, **poolParams)
	elif dbtype == T_SQLITE:
		funct = getSqliteConnection(**params)
		return pool.SingletonThreadPool(creator = funct, **poolParams)



def setTablePrefix(prefix):
	"""Set table prefix, e.g., 'site01.', 'demo21_'
		Input: (string) prefix
		Output: none
	"""
	storage["prefix"] = prefix



def getTablePrefix():
	"""Get table name prefix.
		Input: none
		Output: (string) prefix
	"""
	return storage.get("prefix", "")



def getTable(name, engineName = None, tableName = None,
	hasPrefix = None, engine = None, useMasterEngine = False):
	"""Get a Table object from database engine.
		Input: (string) table name;
			(string) engine name;
			(string) table name in DB;
			(bool) True table name has prefix, False - table name has no prefix;
			(sqlalchemy.SQLEngine) engine instance;
			(bool) set to true to use master engine from engine pool;
		Output: (sqlalchemy.Table) table instance
	"""
	if not hasDbaccess:
		return
	
	if not engine:
		engine = getEngine(engineName)
		# get engine instance from engine pool
		if isinstance(engine, EnginePool):
			if useMasterEngine:
				engine = engine.getMaster()
			else:
				engine = engine.getSlave()
	table = engine.getTable(name, tableName, hasPrefix)
	return table
