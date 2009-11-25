"""
Module that brings all parts of the framework together.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/webstuff/tags/release20061229_v_1_0_0/webstuff/framework.py $
# Author:		$Author: valdiic $
# File version:	$Revision: 260 $
# Last changes:	$Date: 2006-10-04 15:03:10 +0300 (Tr, 04 Okt 2006) $


import sys, re, signal, compiler, thread, os

from optparse import OptionParser
from tools import *
from ThreadStore import ThreadStore
import logger
from logger import *
from Config import Config
import sessions, static, db

import webform
from webform import WebForm

# defaults
# web server module
web = None

# thread safe storage
# you can use it in your modules
#storage = ThreadStore()

# another thread safe storage
# used internally in framework
fw_storage = ThreadStore()

# regexp => function mapping
# list of tuples: (compiled regexp, module name, function reference)
urlmap = []

# direcotry where user stores his own modules & templates
userModDir = ''
userTemplateDir = ''
baseTplPath = 'base'
compiledTplPath = 'compiled'
langfileDirPath = 'langfiles'
staticFileRoot = 'static'

# default site language
defaultLanguage = 'en'
# maps language shortname with it's configuration data
languages = {}

# template classes
templates = {}

# turn debugging off by default
debugOn = False

# configure logger to log errors and warnings only
logger.logToScreen = True
logger.showErrors = True
logger.showDebug = False
logger.showInfo = False
logger.showWarning = True

# counts processed requests
requestCounter = 0

# regular expression which matches static files
staticFileRegexp = re.compile(r'/static/(.+)')

# log message prefixes
logger.errorPrefix = "ERROR: "
logger.debugPrefix = "DEBUG: "
logger.infoPrefix = "INFO:  "
logger.warningPrefix = "WARNING: "
logger.createOutputHandlers()

# configuration defaults
configDefaults = {
	'SERVER' : {
		'server_type' : 'standalone',
		'interface' : 'localhost',
		'port' : 8000,
		'foreground' : False,
		'debug' : False,
		'pid_file' : '/usr/local/var/run/webstuff/webstuffd.pid',
		'user' : '',
		'group' : '',
		'user_module_dir' : './modules',
		'template_dir' : './templates',
		'static_file_dir' : './static',
	},
}
# types for configuration items
configTypes = {
	'SERVER' : {
		'port' : 'int',
		'foreground' : 'bool',
		'debug' : 'bool',
	},
}
# stores server configuration options
conf = Config(defaults = configDefaults, types = configTypes)

# look for Cheetah template engine
try:
	from Cheetah.Compiler import Compiler
	from Cheetah.Template import Template
	hasTemplating = True
except:
	warning ('Could not import Cheetah. Template support disabled.')
	hasTemplating = False



def assignWebserver(name):
	"""Ge2t web server module instance and make
		it available as global variable
		Input: (string) protocol name, currently supported:
			fcgi (fast cgi),
			cgi (scgi, simple cgi),
			standalone (uses BaseHTTPServer)
		Output: none
	"""
	debug ('--- Assigning server type: %s ---' % name)
	global web
	name = name.lower()
	if name == 'fcgi':
		import server.fastcgi_if as web
	elif name == 'cgi':
		import server.cgi_if as web
	elif name == 'standalone':
		import server.standalone_if as web
	else:
		raise NotImplementedError, 'Server type %s not implemented' % name
	
	webform.web = web
	sessions.web = web



def getCliconfig():
	"""Get some configuration attributes from CLI (comand line interface)
		Input: none
		Output: (dict) cli config
	"""
	usage = """usage: %prog [options]

To get list of supported options execute %prog with options -h or --help
"""
	cliParser = conf.setUpCliParser(cliDefaults = dict(conf), usageMessage = usage)
	
	# general options
	cliParser.add_option("-t", "--server-type",
		action = "store", dest = "server_type", metavar = "TYPE",
		help = "Server type (FCGI, SCGI, standalone), default: standalone")
	cliParser.add_option("-i", "--interface",
		action = "store", dest = "interface", metavar = "ADDRESS",
		help = "IP interface which server may bind to, default: localhost")
	cliParser.add_option("-o", "--port",
		action = "store", dest = "port", metavar = "NUMBER",
		help = "Port which server may bind to, default: 8000",
		type = "int")
	# debug options
	cliParser.add_option("-f", "--foreground",
		action = "store_true", dest = "foreground",
		help = "Run in foreground")
	cliParser.add_option("-d", "--debug",
		action = "store_true", dest = "debug",
		help = "Print useful text messages (implifies -f)")
	# os related settings
	cliParser.add_option("-p", "--pid-file",
		action = "store", dest = "pid_file", metavar = "PATH",
		help = "Path to pid file")
	cliParser.add_option("-u", "--user",
		action = "store", dest = "user", metavar = "NAME",
		help = "Switch process uid to given user")
	cliParser.add_option("-g", "--group",
		action = "store", dest = "group", metavar = "NAME",
		help = "Switch process gid to given group")
	conf.readCli()



urlmapLock = thread.allocate_lock()
def loadModules(userUrlmap):
	"""Map user url regular expresions with callable
		functions in user modules.
		Input: (list(tuple)) url mapping, (string) user module directory
		Output: none
		NOTE: uses and modifies global variables: urlmap, userModDir
	"""
	info ('--- Loading user modules ---')
	
	# make operations with urlmap thread safe
	urlmapLock.acquire()
	
	global urlmap, userModDir
	debug ('Module search path: %s' % userModDir)
	for urlPattern, modfunc in userUrlmap:
		(moduleName, functName) = modfunc.split('.')
		debug ('Loading moule: %s, function: %s' % (moduleName, functName))
		# we'll need compiled regexps only
		compiledRegexp = re.compile(urlPattern)
		# import module and get function reference
		module = importModule(moduleName, userModDir)
		function = loadFunction(module, functName)
		# store results
		urlmap.append((compiledRegexp, moduleName, function))
	
	# it's safe to relase the lock after all changes to urlmap are done
	urlmapLock.release()
	

	
def reloadModules():
	debug ("--- Reloading user modules ---")
	
	# make operations with urlmap thread safe
	urlmapLock.acquire()
	
	global urlmap
	for i in xrange(len(urlmap)):
		compiledRegexp, moduleName, function = urlmap[i]
		functName = function.__name__
		debug ('Reloading module: %s, function: %s' % (moduleName, functName))
		# import module and get function reference
		module = importModule(moduleName, userModDir, alwaysReload = True)
		function = loadFunction(module, functName)
		# store results
		urlmap[i] = (compiledRegexp, moduleName, function)
	
	# it's safe to relase the lock after all changes to urlmap are done
	urlmapLock.release()



def hupSignalHandler(signum, frame):
	"""Reload user modules when HUP signal received
	"""
	info ('HUP signal received')
	reloadModules()



def handleRequest():
	"""Handles each request loading templates and user modules.
		Input: none
		Output: none
	"""
	global requestCounter

	fw_storage.add_thread()
	db.storage.add_thread()
	
	try:
		requestCounter += 1
		info ('--- Handling request: %d ---' % requestCounter)
		# get request uri and remove query string
		req_uri = web.getvar_env("REQUEST_URI", '')
		pos = req_uri.find('?')
		if pos != -1:
			req_uri = req_uri[:pos]
		debug ('Request uri:', req_uri)
		
		# handle static files seperately
		staticMatch = staticFileRegexp.match(req_uri)
		if staticMatch:
			static.getFile(*staticMatch.groups())
			fw_storage.remove_thread()
			db.storage.remove_thread()
			return

		# find the module.function that matches, if any
		match = None
		subgroups = ()
		for regexp, moduleName, function in urlmap:
			match = regexp.search(req_uri)
			if match == None:
				continue
			subgroups = match.groups()
			break

		# check if we found a matching function
		if match == None:
			web.notfoundError()
			return
		
		# set language
		setLanguage(web.getvar('language', defaultLanguage))

		try:
			# execute module function (user callback)
			debug ('Executing module: %s, function: %s' % (moduleName, function.__name__))
			function(*subgroups)
			web.setDefaultHeaders()
		except:
			webError ('Error in user module %s, function %s' % (moduleName, function.__name__))
	except:
		printException()

	fw_storage.remove_thread()
	db.storage.remove_thread()



def setLanguage(langcode):
	fw_storage["language"] = langcode
	
	
	
def getLanguage():
	"""Get current site language. If language not set returns default language.
		Input: none
		Output: (string) language code (2 letters)
	"""
	lan = fw_storage.get("language", defaultLanguage)
	if lan in languages:
		return lan
	else:
		return defaultLanguage



def loadTemplate(name):
	"""Returns a cheetah template object or None if templating disabled"""
	if not hasTemplating:
		return None
		
	lang = getLanguage()
	fullname = lang + "_" + name
	
	# check if template class is already imported
	if fullname in templates:
		t_class = templates[fullname]
		return t_class()

	# import template module
	t_module = importModule(fullname, compiledTplPath)
	t_class = getattr(t_module, fullname)
	templates[fullname] = t_class
	
	return t_class()


	
def compileTemplate(tpl, cplFileName, moduleName):
	"""Compile one user template to python bytecode
		Input: (string) template file name;
			(string) compiled (target) file name
		Output: none
	"""
	if not hasTemplating:
		return
	
	debug ("Compiling template %s to file: %s" % (moduleName, cplFileName))
	try:
		debug ('  Generating code')
		cpl = Compiler(source = tpl, moduleName = moduleName)
		cpl.compile()
	except:
		printException()
		error('Error compiling template: %s' % moduleName)
		return
	# write compiled template to file
	try:
		debug ('  Writing to file')
		fh = open(cplFileName, 'w')
		fh.write(str(cpl))
		fh.close()
	except:
		printException()
		error('Can not write compiled template to file: %s' % cplFileName)
		return
	# compile generated template to python bytecode
	try:
		debug ('  Compiling to Python bytecode')
		compiler.compileFile(cplFileName)
	except:
		printException()
		error('Can not compile generated template to python bytecode. File: %s' % cplFileName)
		return



templateFileRegexp = re.compile(r'^(.+?)\.tmpl$') # matches .tmpl files
langfileFileRegexp = re.compile(r'^(\w{2})\.conf$') # matches xx.conf files
templatesLock = thread.allocate_lock()
def compileTemplates(clearFirst = True):
	"""Compile user template in all available human languages
		Input: (bool) set to True to clear compiled template directory first
		Output: none
	"""
	if not hasTemplating:
		return
	
	# make operations with templates thread safe
	templatesLock.acquire()
	
	# clear old compiled template files
	if clearFirst:
		clearTemplates(compiledTplPath)
	
	# read language config
	info ('--- Reading language configuration ---')
	global languages
	languages = {} # maps language to Config instance
	for langFileName in os.listdir(langfileDirPath):
		matched = langfileFileRegexp.match(langFileName)
		# we're not very interested in parsing other files than language config ones
		if not matched:
			continue
		# read language config file and store parsed data
		langConf = Config()
		fullname = os.path.join(langfileDirPath, langFileName)
		langConf.readFiles(fullname)
		languages[matched.group(1)] = langConf
	
	# parse templates in default language anyway
	if defaultLanguage not in languages:
		langConf = Config()
		langConf['langConf'] = {'lang_name': 'English'}
		languages[defaultLanguage] = langConf
		
	
	# compile Cheetah templates
	info ('--- Compiling user templates ---')
	for fileName in os.listdir(baseTplPath):
		matched = templateFileRegexp.match(fileName)
		# process .tmpl file only
		if not matched:
			continue
		
		# set file paths and module name
		tplFileName = os.path.join(baseTplPath, fileName)
		moduleName = matched.group(1)
		
		# translate template to each of available languages
		for lang, langConf in languages.iteritems():
			debug ('Translating template %s to language %s' % (tplFileName, lang))
			lngModuleName = lang + "_" + moduleName
			cplFileName = os.path.join(compiledTplPath, lngModuleName + '.py')
			try:
				# load and translate user template
				searchList = [langConf.get(moduleName, {})]
				tpl = Template(file = tplFileName, searchList = searchList)
				# compile parsed template to python code
				compileTemplate(tpl, cplFileName, lngModuleName)
			except:
				printException()
				error('Can not translate template. File: %s; language: %s' % (tplFileName, lang))
				continue
	
	# it is safe to release lock only when all changes to templates dict are finished
	templatesLock.release()
	info ('Finished compiling templates')



compiledFileRegexp = re.compile(r'^.+?\.pyc?$') # matches .py and .pyc files
def clearTemplates(dirPath):
	"""Clear all compiled templates from gived directory
		Input: (string) directory path
		Output: none
	"""
	if not hasTemplating:
		return
	
	info ('--- Clearing compiled user templates ---')
	for fileName in os.listdir(dirPath):
		if compiledFileRegexp.match(fileName):
			fullFileName = os.path.join(compiledTplPath, fileName)
			debug ('Removing: %s' % fullFileName)
			try:
				os.remove(fullFileName)
			except:
				printException()
				error('Can not remove compiled user template: %s' % fullFileName)
	info ('--- Clearing loaded user templates ---')
	templates.clear()
	clearImportedModules(compiledTplPath)
	


def displayTemplate(tpl):
	"""Simple way how to deliver parsed template to user
		Input: (Cheetah.Template) template object
		Output: none
	"""
	if not hasTemplating:
		return
	try:
		web.output(tpl)
	except:
		webError('Error parsing template: %s' % tpl.__module__)
	
	

def webError(msg):
	"""Simple way how to display error message (and exception info) to user.
		Input: none
		Output: none
	"""
	if not debugOn:
		# don't show anything other than error to user
		web.rmHeaders()
		web.rmOutput()
	
	# print error message to user
	web.internalError()
	# print error message to web interface
	if debugOn:
		web.output("<pre>\n")
		web.output(strException())
		web.output(msg)
		web.output('</pre>\n')
	
	# print error and exception info for admin
	printException()	
	error(msg)


	
def pfPrint(msg):
	"""Print preformatted html text. Usable mostly for debugging 
		and testing purposes
	"""
	web.output('<pre>\n%s\n</pre>\n' % msg)



def run(userUrlmap, **confArgs):
	"""Start handling requests. Run script with -h or --help options to
		see the list of possible options.
		Input: (list(tuples)) url mapping, (mixed) various configuration attributes.
			Accepted configuration attributes:
			* server_type - server type, one of "standalone", "fcgi" or "cgi"
			* user_module_dir - path to user module directory
			* template_dir - path to user templates directory
			* static_file_dir - path to directory for static files
			* interface - ip address or hostname which server (standalone or fcgi)
				will use for binding
			* port - port which server will use for binding
			* pid_file - path to server process id file
			* user - server process will belong to this user
			* group - server process will belong to this group
		Output: none
		NOTE: arguments of this function are overriden by command line arguments!
	"""
	# set signal handler
	signal.signal(signal.SIGINT, killSignalHandler)
	signal.signal(signal.SIGTERM, killSignalHandler)
	
	# SIGHUP could not be handled on Windows
	if sysname != 'windows':
		signal.signal(signal.SIGHUP, hupSignalHandler)
	
	
	# fork and run as daemon by default
	runInBackground = True
	
	# fill configuration with data supplied by user
	serverConf = conf['SERVER']
	for name, value in confArgs.items():
		if name not in serverConf:
			raise NameError, 'Attribute "%s" is not supported' % name
		serverConf[name] = value
	
	# get configuration attributes from cli
	# they should overwrite any user supplied configuration parameters
	getCliconfig()
	
	# apply configuration
	if serverConf['foreground']:
		runInBackground = False
	if serverConf['debug']:
		global debugOn
		debugOn = True
		logger.logToScreen = True
		logger.showErrors = True
		logger.showDebug = True
		logger.showInfo = True
		logger.showWarning = True
		logger.createOutputHandlers()
		runInBackground = False
		serverConf['foreground'] = True
	user = serverConf['user']
	group = serverConf['group']
	
	# show parsed configuration data to user
	debug ('Final server configuration:')
	debug (conf)
	
	# fork and run as daemon
	if sysname != 'windows' and runInBackground:
		info ('Daemonizing...')
		childProcId = os.fork()
		if childProcId != 0:
			sys.exit(0)
	
	# store global variables
	global userModDir, userTemplateDir, staticFileRoot
	userModDir = serverConf['user_module_dir']
	userTemplateDir = serverConf['template_dir']
	staticFileRoot = serverConf['static_file_dir']
	
	# set up and check template directories
	global baseTplPath, compiledTplPath, langfileDirPath
	baseTplPath = os.path.join(userTemplateDir, baseTplPath)
	compiledTplPath = os.path.join(userTemplateDir, compiledTplPath)
	langfileDirPath = os.path.join(userTemplateDir, langfileDirPath)
	checkDir(userTemplateDir) # we need read only access
	checkDir(langfileDirPath) # we need read only access
	checkDir(staticFileRoot) # we need read only access
	checkDir(compiledTplPath, user = user, group = group) # rw access needed
	
	# store pid in file
	makePidfile(serverConf['pid_file'], user, group)
	
	# assign webserver before loading any other modules
	assignWebserver(serverConf['server_type'])
	
	# set up webserver and bind it to interface and port 
	web.init(handleRequest, serverConf['interface'], serverConf['port'])
	# switch user and group ids
	switchUid(user, group)
	
	# compile regexps in urlmap and load mapped functions
	loadModules(userUrlmap)
	
	# compile user templates
	compileTemplates()

	# start serving requests at last
	keepRunning = True
	while keepRunning:
		keepRunning = web.run()
		if keepRunning:
			reloadModules()
			compileTemplates()
	
	# Actually we should never get this far
	# but I'll put quit() here just because of being such a paranoic.
	quit('Exiting')
