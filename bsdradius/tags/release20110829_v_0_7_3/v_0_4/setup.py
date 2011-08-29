#!/usr/local/bin/python
"""
BSD Radius installation script
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_4/setup.py $
# Author:		$Author: valts $
# File version:	$Revision: 203 $
# Last changes:	$Date: 2006-04-04 17:34:35 +0300 (Ot, 04 Apr 2006) $

import os, sys
import re
import distutils.core
import distutils.sysconfig
import distutils.util
import distutils.file_util
import distutils.dir_util
from optparse import OptionParser
#import bsdradius.bsdradiusd

# default installation prefix
platform = distutils.util.get_platform()
defaultPrefix = '/usr/local'
verbose = 1



def listdir(path):
	"""List directory without .svn in results and put
		path as prefix for each result
		Input: (string) directory path.
		Output: (list) directory contents.
	"""
	ret = []
	if not path:
		return ret

	for name in os.listdir(path):
		if name == '.svn':
			continue
		name = '%s/%s' % (path, name)
		ret.append(name)

	return ret
	

def replaceStuffInFile(filePath, lineRegexpStr, newPrefixLine, dryRun):
	"""Set prefix in given file changing according lines
		Input: (string) path to file, (string) regexp for searching lines
			for changing, (string) lines for replacement
	"""
	# read file and look for lines that are neccessary to change
	debug ("  editing file:", filePath)
	if dryRun: return

	fh = open(filePath, 'r+')
	lineRegexp = re.compile(lineRegexpStr)
	parsedLines = []
	for line in fh:
		line = line.strip()
		#print line
		matched = lineRegexp.match(line)
		if matched:
			line = newPrefixLine
		parsedLines.append(line + '\n')
	fh.close()
	# save changes
	fh = open(filePath, 'w+')
	fh.writelines(parsedLines)
	
	
	
def debug(*str):
	if verbose:
		for msg in str:
			print msg,
		print
		
def error(*str):
	if verbose:
		debug ('ERROR:', *str)

	

### MAIN ###

# Prepare setup data
shareDir = 'share/bsdradius'
etcDir = 'etc/bsdradius'
dataFiles = [
	('%s/dictionaries' % shareDir, listdir('dictionaries')),
	('%s/doc' % shareDir, listdir('doc')),
	(etcDir, listdir('etc')),
	('%s/sql' % shareDir, listdir('sql')),
	('%s/tools' % shareDir, listdir('tools')),
	('%s/user_modules' % etcDir, listdir('user_modules')),
]

# call setup
dist = distutils.core.setup(
	name = 'bsdradius',
	version = '0.4',
	author = 'Data Tech Labs',
	author_email = 'info@datatechlabs.com',
#	maintainer = 'Valts Mazurs',
#	maintainer_email = 'valts@datatechlabs.com',
	url = 'http://www.datatechlabs.com',
	description = 'BSD Radius server',
	packages = ['bsdradius', 'bsdradius.pyrad', 'bsdradius.serverModules'],
	scripts = ['bin/bsdradiusd.py', 'bin/bsdradiusd'],
	data_files = dataFiles,
#	py_modules = [],
)



# run post install tasks
cmdObj = dist.command_obj
if 'install' in sys.argv and 'install' in cmdObj:
	dryRun = dist.dry_run
	verbose = dist.verbose
	debug ("Running post install tasks"	)
	# get installation prefix
	prefix = cmdObj['install'].config_vars['base']
	debug ('prefix:', prefix)
	# get python library path
	libPath = cmdObj['install_lib'].install_dir
#	libPath = re.sub(defaultPrefix, prefix, libPath)
	# set search string
	searchString = r"^prefix\s*=.*$"
	
	debug ("Changing installation prefix in main config file")
	try:
		confFilePath = '%s/etc/bsdradius/bsdradiusd.conf' % prefix
		replaceStuffInFile(confFilePath, searchString, "prefix = %s" % prefix, dryRun)
	except:
		 error ("Can not set installation prefix in file %s" % confFilePath)
	
	debug ("Changing installation prefix in default config library")
	try:
		configDefaultsPath = '%s/bsdradius/configDefaults.py' % libPath
		replaceStuffInFile(configDefaultsPath, searchString, "prefix = '%s'" % prefix, dryRun)
	except:
		error ("Can not set installation prefix in file %s" % configDefaultsPath)
	
	# create symlink to main executeable file
	try:
		bindir = prefix + '/bin'
		daemonScriptPath = bindir + '/bsdradiusd'
		replaceStuffInFile(daemonScriptPath, r'^PYTHONPATH=.*$', "PYTHONPATH=%s" % libPath, dryRun)
		replaceStuffInFile(daemonScriptPath, r'^exec.*$', "exec %s%s $@" % (daemonScriptPath, '.py'), dryRun)
	except:
		error ("Can not set PYTHONPATH in file %s" % configDefaultsPath)
	
	# create startup script
	#if re.match('freebsd', platform):
		#print "Installing startup script for freebsd"
