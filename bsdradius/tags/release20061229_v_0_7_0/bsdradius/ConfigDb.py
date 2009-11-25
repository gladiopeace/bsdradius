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
This module contains class for reading configuration
data from database
"""


from UserDict import UserDict
from bsdradius.logger import *
from bsdradius.Config import main_config



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
		# check if connection to db is still up and running
		if not self._dbh.checkConnection(verbose):
			try:
				self._dbh.reconnect()
			except:
				error ('Could not reconnect to database')
				return
		
		query = main_config['DATABASE']['clients_query']
		result = self._dbh.execGetRows(query, verbose)
		if result:
			for row in result:
				self['CLIENTS'][row[0]] = {'name': row[1], 'secret': row[2]}
