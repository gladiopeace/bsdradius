#!/usr/bin/env python
"""
BSD Radius installation script
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/trunk/setup.py $
# Author:		$Author: valts $
# File version:	$Revision: 303 $
# Last changes:	$Date: 2006-12-29 11:35:07 +0200 (Pk, 29 Dec 2006) $

import os, sys, os.path, shutil
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



def listdir(path, suffix = None):
	"""List directory without .svn in results and put
		path as prefix for each result
		Input: (string) directory path;
			(string) if present only files with such suffix will be included
				in the results.
		Output: (list) directory contents.
	"""
	ret = []
	if not path:
		return ret

	for name in os.listdir(path):
		if name == '.svn':
			continue
		if suffix is not None and not name.endswith(suffix):
			continue
		name = '%s/%s' % (path, name)
		# exclude directories
		if os.path.isdir(name):
			continue
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
	(etcDir, listdir('etc', suffix = ".sample")),
	('%s/sql' % shareDir, listdir('sql')),
	('%s/tools' % shareDir, listdir('tools')),
	('%s/user_modules' % etcDir, listdir('user_modules')),
]

# call setup
dist = distutils.core.setup(
	name = 'bsdradius',
	version = '0.8.0',
	author = 'DataTechLabs',
	author_email = 'info@datatechlabs.com',
	url = 'http://www.datatechlabs.com',
	description = 'BSD Radius server',
	packages = ['bsdradius', 'bsdradius.pyrad', 'bsdradius.serverModules',
		'bsdradius.webstuff'],
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
	
	# copy sample config file to usual ones if they do not exist yet
	debug ("Creating configuration files which don't exist yet")
	cfgFiles = listdir(os.path.join(prefix, "etc/bsdradius"))
	for filename in cfgFiles:
		# look for ".sample" at the ned of file
		idx = filename.rfind('.sample')
		if idx > 0:
			# cut ".sample" postfix
			shortname = filename[:idx]
			if not os.path.exists(shortname):
				debug ("  Creating configuration file: %s" % shortname)
				try:
					shutil.copyfile(filename, shortname)
				except:
					error ("Can not create configuration file: %s" % shortname)
	
	# set search string
	searchString = r"^prefix\s*=.*$"
	
	debug ("Changing installation prefix in main config file")
	try:
		confFilePath = os.path.join(prefix, 'etc/bsdradius/bsdradiusd.conf')
		replaceStuffInFile(confFilePath, searchString, "prefix = %s" % prefix, dryRun)
	except:
		 error ("Can not set installation prefix in file %s" % confFilePath)
	
	debug ("Changing installation prefix in default config library")
	try:
		configDefaultsPath = os.path.join(libPath, 'bsdradius/configDefaults.py')
		replaceStuffInFile(configDefaultsPath, searchString, "prefix = '%s'" % prefix, dryRun)
	except:
		error ("Can not set installation prefix in file %s" % configDefaultsPath)
	
	# Create symlink to main executable file.
	# This should not work on windows.
	try:
		bindir = os.path.join(prefix, 'bin')
		daemonScriptPath = os.path.join(bindir, 'bsdradiusd')
		replaceStuffInFile(daemonScriptPath, r'^PYTHONPATH=.*$', "PYTHONPATH=%s" % libPath, dryRun)
		replaceStuffInFile(daemonScriptPath, r'^exec.*$', "exec %s%s $@" % (daemonScriptPath, '.py'), dryRun)
	except:
		error ("Can not set PYTHONPATH in file %s" % daemonScriptPath)
