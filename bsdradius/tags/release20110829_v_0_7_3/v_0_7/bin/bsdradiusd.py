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
BSD Radius
Data Tech Labs radius server.
Made specially for VoIP needs.
"""


# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_7/bin/bsdradiusd.py $
# Author:		$Author: valts $
# File version:	$Revision: 333 $
# Last changes:	$Date: 2007-08-17 02:38:15 +0300 (Pk, 17 Aug 2007) $

__software__ = 'Bsdradius'
mayRunInBackground = False

# import modules
import sys, signal
import os
import time

# This MUST be the first import in order to use wbstuff.logger
# instead of bsdradius.logger. To understand the magic take a look at
# bsdradius/logger.py
from bsdradius import logger
# Other imports may continue as previously
from bsdradius import BsdRadiusServer
from bsdradius import DatabaseConnection
from bsdradius import misc
from bsdradius import modules
from bsdradius import Config
from bsdradius.pyrad import dictionary
from bsdradius.ConfigDb import ConfigDb
from bsdradius.configDefaults import defaultOptions, defaultTypes
from bsdradius.logger import *


# set logging defaults
logger.showDebug = True
logger.showErrors = True
logger.showWarning = True
logger.showInfo = True
logger.logToScreen = False
logger.createOutputHandlers()



def main():
	"""Prepare and execute server
	"""
	# make sure that keyboard interrupt stops our server
	# and clean up before exiting
	signal.signal(signal.SIGINT, misc.killSignalHandler)
	signal.signal(signal.SIGTERM, misc.killSignalHandler)
	
#	try:
#		import psyco
#		psyco.full()
#		print ('--- Running psyco ---')
#	except:
#		print('Using psyco failed')
	
	# read main configuration data
	Config.readMainConf()
	main_config = Config.main_config
	debug (main_config)
	
	# fork and run as daemon
	if mayRunInBackground and not main_config['SERVER']['foreground']:
		info ('Daemonizing...')
		childProcId = os.fork()
		if childProcId != 0:
			sys.exit(0)
	
	# store pid in file
	user = main_config['SERVER']['user']
	group = main_config['SERVER']['group']
	runDirPath = main_config['PATHS']['run_dir']
	if not misc.checkDir(runDirPath, user = user, group = group):
		misc.quit("Checking %s directory failed" % runDirPath, 1)
	misc.makePidfile()
	
	# check and/or create log directory
	logDirPath = main_config['PATHS']['log_dir']
	if not misc.checkDir(logDirPath, user = user, group = group):
		misc.quit("Checking %s directory failed" % logDirPath, 1)
	
	# open log file
	logFilePath = main_config['PATHS']['server_log_file']
	if logFilePath and main_config['SERVER']['log_to_file']:
		info ('--- Opening log file ---')
		# open file
		try:
			logger.logFile = open(logFilePath, 'a+')
#			misc.setOwner(logFilePath, user, group)
		except:
			misc.printExceptionError()
			quit('Can not open logfile')
	
	# parse dictionaries
	info ('--- Parsing dictionary files ---')
	radiusDict = dictionary.Dictionary(main_config['PATHS']['dictionary_file'])
	
	# connect to database
	if main_config['DATABASE']['enable']:
		info ('--- Connecting to database ---')
		# set driver name
		dbType = main_config['DATABASE']['type']
		if dbType == 'postgresql':
			DatabaseConnection.dbadapterName = 'psycopg'
		elif dbType == 'mysql':
			DatabaseConnection.dbadapterName = 'MySQLdb'
		elif dbType == 'sqlite':
			DatabaseConnection.dbadapterName = 'pysqlite2.dbapi2'
		else:
			error ("Invalid database type: " + dbType)
			misc.quit()
			
		# connect to host and store connection globally available
		try:
			dbh1 = DatabaseConnection.DatabaseConnection.getHandler('bsdradius dbh1')
			dbh1.connect (
				host = main_config['DATABASE']['host'],
				user = main_config['DATABASE']['user'],
				password = main_config['DATABASE']['pass'],
				dbname = main_config['DATABASE']['name'] )
		except:
			misc.printExceptionError()
			misc.quit("Error connecting to database. Check DATABASE section in config file.", 1)
	
	# start server itself
	authport = main_config["SERVER"]["auth_port"]
	acctport = main_config["SERVER"]["acct_port"]
	srv = BsdRadiusServer.BsdRadiusServer(dict = radiusDict, authport = authport, \
		acctport = acctport)
	
	# add valid server client hosts from file
	if main_config['PATHS']['clients_file']:
		info ('--- Reading server clients from file ---')
		clientsConf = Config.Config()
		clientsConf.readFiles([main_config['PATHS']['clients_file']])
		srv.addClientHosts(clientsConf)
	# add valid server client hosts from DB
	# overwrite hosts from file
	if main_config['DATABASE']['enable']:
		info ('--- Reading server clients from DB ---')
		confDb = ConfigDb(dbh1)
		confDb.ReadClients()
		srv.addClientHosts(confDb['CLIENTS'])
				
	debug ('--- Clients: ---')
	for addr in srv.hosts:
		debug ('%s: %s' % (addr, srv.hosts[addr].name))
		
	# bind to IP address (default: all)
	srv.BindToAddress(main_config['SERVER']['home'])
	
	# switch to nonprivileged user
	misc.switchUid(user, group)
	
	# Load BSD Radius server modules.
	# Do it just before starting the server to provide modules with maximum info.
	info ('--- Reading module configuration ---')
	modules.readConfig([main_config['PATHS']['modules_file'], main_config['PATHS']['user_modules_file']])
	debug ('Module configuration:')
	debug (modules.modulesConfig)
	info ('--- Loading modules ---')
	modules.loadModules()
	info ('--- Executing startup modules ---')
	modules.execStartupModules()
	
	# run server
	info ("--- Starting server ---")
	srv.Run()
	
	# do some maintenace tasks
	everythingOk = True
	dbEnable = main_config['DATABASE']['enable']
	dbRefreshCounter = 0
	dbRefreshRate = main_config['DATABASE']['refresh_rate']
	while everythingOk:
		time.sleep(1)
		
		# refresh radius server clients from DB
		if dbEnable:
			dbRefreshCounter += 1
			if dbRefreshCounter >= dbRefreshRate:
				#info ('Refreshing config from DB')
				#debug ('I was waiting for it %s seconds :)' % dbRefreshCounter)
				dbRefreshCounter = 0
				confDb.ReadClients()
				srv.addClientHosts(confDb['CLIENTS'])
				# print only changed clients
	
	
	# exit program
	misc.quit()



if __name__ == '__main__':
	# program should be allowed to run in background only when it is executed itself
	# instead of importing in other modules. It makes debugging and profiling much easier.
	mayRunInBackground = True
	main()
