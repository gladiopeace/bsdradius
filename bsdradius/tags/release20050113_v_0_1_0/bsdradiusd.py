#!/usr/local/bin/python
"""
VoIP Radius
Data Tech Labs radius server.
Made specially for VoIP needs.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/tags/release20050113_v_0_1_0/bsdradiusd.py $
# Author:		$Author: valts $
# File version:	$Revision: 124 $
# Last changes:	$Date: 2006-01-13 19:50:15 +0200 (Pk, 13 Jan 2006) $

__version__ = 'BSD Radius 1.0.0'


# import modules
import sys, signal
import os
import time

sys.path.insert(0, './lib')
sys.path.insert(0, './modules')
import BsdRadiusServer
import logging
import DatabaseConnection
import misc
import modules
import Config
from pyrad import dictionary
from ConfigDb import ConfigDb
from ConfigCli import ConfigCli
from configDefaults import defaultOptions, defaultTypes
from logging import *


# make sure that keyboard interrupt stops our server
# and clean up before exiting
signal.signal(signal.SIGINT, misc.killSignalHandler)
signal.signal(signal.SIGTERM, misc.killSignalHandler)

# parse command line options
confCli = ConfigCli(__version__)

# set logging attributes
if 'SERVER' in confCli:
	srvConf = confCli['SERVER']
	if 'debug_mode' in srvConf and srvConf['debug_mode']:
		confCli['SERVER']['foreground'] = True
		confCli['SERVER']['no_threads'] = True
		confCli['SERVER']['log_to_screen'] = True
	if 'log_to_screen' in srvConf and srvConf['log_to_screen']:
		# enable logging to screen 
		logging.logToScreen = True
	if 'log_client' in srvConf and srvConf['log_client']:
		# restrict all threads from logging
		info ('--- Enabling threads logging restrictions ---')
		logging.restrictThreads = True
		# add this (main) thread to unrestricted threads to allow print log messages
		misc.addUnrestrictedThread()

info ('--- Reading configuration ---')
# get config file path
if 'PATHS' in confCli and 'config_file' in confCli['PATHS']:
	Config.configFiles[0] = confCli['PATHS']['config_file']
# read config file
Config.readFiles = Config.main_config.read(Config.configFiles)
# check if all neccessary files are read
if Config.configFiles != Config.readFiles:
	misc.quit("Can not read required configuration files", 1)

# overwrite configfile attributes with command line ones
confCli.applyOptions()

# print config
main_config = Config.main_config
debug (main_config)

# fork and run as daemon
if not main_config['SERVER']['foreground']:
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

# open log file
if main_config['PATHS']['server_log_file'] and main_config['SERVER']['log_to_file']:
	logDirPath = main_config['PATHS']['log_dir']
	logFilePath = main_config['PATHS']['server_log_file']
	info ('--- Opening log file ---')
	# check and/or create log directory
	if not misc.checkDir(logDirPath, user = user, group = group):
		misc.quit("Checking %s directory failed" % logDirPath, 1)
	# open file
	try:
		logging.logFile = open(logFilePath, 'a+')
		misc.setOwner(logFilePath, user, group)
	except:
		misc.printExceptionError()
		quit('Can not open logfile')

# parse dictionaries
info ('--- Parsing dictionary files ---')
dict = dictionary.Dictionary('dictionaries/dictionary')

# connect to database
if main_config['DATABASE']['enable']:
	info ('--- Connecting to database ---')
	# set driver name
	if main_config['DATABASE']['type'] == 'postgresql':
		DatabaseConnection.dbadapterName = 'psycopg'
	else:
		DatabaseConnection.dbadapterName = 'MySQLdb'
		
	# connect to host and store connection globally available
	try:
		DatabaseConnection.dbh1 = DatabaseConnection.DatabaseConnection('dbh1')
		DatabaseConnection.dbh1.connect (
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
srv = BsdRadiusServer.BsdRadiusServer(dict = dict, authport = authport, \
	acctport = acctport)

# add valid server client hosts from file
if main_config['PATHS']['clients_file']:
	info ('--- Reading server clients from file ---')
	clientsConf = Config.Config()
	clientsConf.read([main_config['PATHS']['clients_file']])
	srv.addClientHosts(clientsConf)
# add valid server client hosts from DB
# overwrite hosts from file
if main_config['DATABASE']['enable']:
	info ('--- Reading server clients from DB ---')
	confDb = ConfigDb(DatabaseConnection.dbh1)
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
modules.readConfig(main_config['PATHS']['modules_file'])
modules.readConfig(main_config['PATHS']['user_modules_file'])
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
dbRefreshCounter = 0
main_config['DATABASE']['refresh_rate'] = 10
while everythingOk:
	time.sleep(1)
	
	# refresh radius server clients from DB
	if main_config['DATABASE']['enable']:
		dbRefreshCounter += 1
		if dbRefreshCounter >= main_config['DATABASE']['refresh_rate']:
			#info ('Refreshing config from DB')
			#debug ('I was waiting for it %s seconds :)' % dbRefreshCounter)
			dbRefreshCounter = 0
			confDb.ReadClients()
			srv.addClientHosts(confDb['CLIENTS'])
			# print only changed clients


# exit program
misc.quit()
