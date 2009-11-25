"""
This module contains class for reading configuration
data from database
"""


from UserDict import UserDict
from logging import *



class ConfigDb(UserDict):
	"""Class for readin configuration data from database
	"""
	
	def __init__(self, dbh):
		"""Constructor
			Input: (DatabaseConnectio) database connection handler
			Output: (configDb) class instance
		"""
		UserDict.__init__(self)
		self._dbh = dbh
		self.data['CLIENTS'] = {}



	def ReadClients(self, verbose = False):
		"""Read or refresh radius client data from DB
			Input: (bool) be verbose and print some debugging info
			Output: (none)
		"""
		
		query = 'select address, name, secret from radiusClients'
		result = self._dbh.execGetDict(query, verbose)
		if result:
			for row in result:
				self['CLIENTS'][row['address']] = {'name': row['name'], 'secret': row['secret']}
