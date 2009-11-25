#!/usr/local/bin/python

"""
Main example script
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/webstuff/tags/release20061229_v_1_0_0/examples/main.py $
# Author:		$Author: atis $
# File version:	$Revision: 47 $
# Last changes:	$Date: 2006-06-13 18:25:48 +0300 (Ot, 13 Jūn 2006) $


# we want to get access to webstuff module.
import sys
sys.path.insert(0, '../')

import webstuff.framework as fw
from webstuff import sessions, db
from webstuff.logger import *
import re, traceback

# map url regexps to module.function
# 1 -st element: url regexp
# 2-nd element: module name
# 3-rd element: function (or any other callable object) name
urlmap = [
	("/overview",  "various.overview"),
	("/accounts/list/(\w+)", "accounts.list"),
	("/accounts/edit/(\d+)", "accounts.edit"),
	("/login", "various.login"),
	("/logout", "various.logout"),
]

# prepare config file defaults
confFilePath = './example.conf'
configDefaults = {
	'PATHS' : {
		'prefix' : '.',
		'module_dir' : '%(prefix)s/modules',
		'template_dir' : '%(prefix)s/templates',
		'config_file' : '%(prefix)s/example.conf',
	},
	'SERVER' : {
		'server_type' : 'standalone',
	},
}

# read configuration data
conf = fw.Config(defaults = configDefaults)
readFiles = conf.readFiles(conf['PATHS']['config_file'])
if not readFiles:
	fw.quit('Error reading config file', 1)

# user module dir
moduleDir = conf['PATHS']['module_dir']
# compiled Cheetah template dir
templateDir = conf['PATHS']['template_dir']
serverType = conf['SERVER']['server_type']

# prepare database for storing sessions
sqliteFile = './sqlite.db'
#sqliteFile = ':memory:'
#dbengine = db.getEngine(name = 'webstuff', dbtype = db.T_SQLITE, engineParams = {'echo' : True},
#	filename = sqliteFile)
#dbengine = db.getEngine(name = 'webstuff', dbtype = db.T_MYSQL, engineParams = {'echo' : True},
#	host = 'alpha', user = 'valts', password='ultrascreen', dbname='test')
dbengine = db.getEngine(name = 'webstuff', dbtype = db.T_POSTGRESQL, engineParams = {'echo' : True},
	host = 'alpha', user = 'valts', password='ultrascreen', dbname='test')

sessionTable = db.Table('sessions', dbengine,
	db.Column('session_id', db.String(50), primary_key=True),
	db.Column('username', db.String(50)),
	db.Column('user_ip_address', db.String(15)),
	db.Column('exp_timestamp', db.Float),
	db.Column('timeout', db.Integer),
	db.Column('additional_data', db.PickleType)
)
fieldMapping = {
	'session_id' : 'session_id',
	'user_id' : 'username',
	'user_ip_address' : 'user_ip_address',
	'exp_timestamp' : 'exp_timestamp',
	'timeout' : 'timeout',
	'additional_data' : 'additional_data',
}

# create table if it already doesn't exist
try:
	sessionTable.create()
except:
	fw.printException()
	pass

sesTable = db.getTable('ses', engineName = 'webstuff', tableName = 'sessions')

# set up session storage engine
sessions.storeInDb(sessionTable, fieldMapping = fieldMapping)

# start serving pages
if __name__ == '__main__':
	fw.run(urlmap, server_type = serverType, user_module_dir = moduleDir, template_dir = templateDir)
