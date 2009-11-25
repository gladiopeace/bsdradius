"""
Common webserver interface
"""

# HeadURL		$HeadURL: svn://alpha:33033/megabox/trunk/web_modules/calls.py $
# Author:		$Author: valts $
# File version:	$Revision: 1831 $
# Last changes:	$Date: 2006-05-17 16:46:35 +0300 (Wed, 17 May 2006) $


import cgi, time, Cookie
from webstuff.ThreadStore import ThreadStore

# thread specific storage
storage = ThreadStore()

def response(code, descr):
	"""Set HTTP response."""

	storage["response"] = (code, descr)

def header(key, value):
	"""Append html header."""

	storage["headers"].append((key, value))

def output(data):
	"""Output page content."""

	storage["content"] += str(data)

def getvar_get(name, default = None):
	"""Get the value of a GET variable."""

	getvars = storage["getvars"]
	if getvars.has_key(name):
		return getvars[name][0]
	return default

def getvar_post(name, default = None):
	"""Get the value of a POST variable."""

	postvars = storage["postvars"]
	if postvars.has_key(name):
		return postvars[name][0]
	return default

def getvar_cookie(name, default = None):
	"""Get cookie value."""

	cookies = storage["cookies"]
	return cookies.get(name, default)

def getvar_env(name, default = None):
	"""Get environment variable."""

	env = storage["env"]
	return env.get(name, default)

def setcookie(name, value, expire = None, path = '/', domain = None):
	"""Send a Set-Cookie header."""

	if value == None:
		value = ""

	cookie = Cookie.SimpleCookie()
	cookie[name] = value

	if expire != None:
		expire = time.gmtime(expire)
		expdate = time.strftime("%A, %d-%b-%Y %H-%M-%S GMT", expire)
		cookie[name]["expires"] = expdate
		
	if domain != None:
		cookie[name]["domain"] = domain

	cookie[name]["path"] = path

	header("Set-Cookie", cookie[name].OutputString())

def delcookie(name, expire = None, path = '/', domain = None):
	"""Remove cookie."""
	
	setcookie(name, None, expire, path, domain)

def getvar(name, default = None):
	"""Get variable from GET, POST or environment."""
	
	value = getvar_get(name, default)
	if value != default:
		return value

	value = getvar_post(name, default)
	if value != default:
		return value

	value = getvar_cookie(name, default)
	if value != default:
		return value

	return getvar_env(name, default)

def redirect(location):
	"""HTTP Redirect."""

	servname = getvar_env("SERVER_NAME")
	response(302, "Redirect")
	header("Location", "http://" + servname + location)
	
def setDefaultHeaders(force = False):
	"""Set default HTTP headers if neccessary
		Input: (bool) set to true to overwrite existing headers
		Output: none
	"""
	# assign defaults if force enabled
	defaults = [
		("Content-Type", "text/html"),
	]
	if force:
		storage["headers"] = defaults
		return
	
	# scan for missing headers and add them if not found
	contentTypeFound = False
	for key, value in storage["headers"]:
		if key.lower() == "content-type":
			contentTypeFound = True
	# add missing headers
	if not contentTypeFound:
		header("Content-Type", "text/html")
		
def rmHeaders():
	"""Clear all headers that user has set
		Input: none
		Output: none
	"""
	storage["headers"] = []
	
def rmOutput():
	"""Clear all output.
		Input: none
		Output: none
	"""
	storage["content"] = ""
	
# display various errors to user
def notfoundError():
	response(404, "Not Found")
	header("Content-Type", "text/html")
	output('<h1>404 - Not Found</h1>')

def internalError():
	response(500, "Internal Server Error")
	header("Content-Type", "text/html")
	output("<h1>500 - Internal Server Error</h1>")
