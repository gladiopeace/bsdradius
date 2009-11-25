"""
Defines FCGI server
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/webstuff/tags/release20061229_v_1_0_0/webstuff/server/fastcgi_if.py $
# Author:		$Author: atis $
# File version:	$Revision: 59 $
# Last changes:	$Date: 2006-07-17 16:44:00 +0300 (Pr, 17 Jūl 2006) $


from common_if import *
import flup.server.fcgi as fcgi

# user main function
user_func = None

# server instance
serverInstance = None

def _main(environ, start_response):
	"""Wraps user function to work with flup FastCGI."""

	storage.add_thread()

	try:
		# setup thread storage
		storage["headers"] = []
		storage["response"] = (200, "OK")
		storage["content"] = ""

		# get and parse query string
		query_string = environ.get("QUERY_STRING", "")
		storage["getvars"] = cgi.parse_qs(query_string, True)

		# store POST
		input_file = environ["wsgi.input"]
		environ["QUERY_STRING"] = ""
		storage["postvars"] = cgi.parse(input_file, environ, 1)

		# store cookies
		cookie_obj = Cookie.SimpleCookie()
		cookie_obj.load(environ.get("HTTP_COOKIE", ""))
		cookies = {}
		for key, morsel in cookie_obj.iteritems():
			cookies[key] = morsel.value
		storage["cookies"] = cookies

		# store environment
		environ["QUERY_STRING"] = query_string
		storage["env"] = environ

		# execute user function
		user_func()

		# output response and headers
		code, descr = storage["response"]
		header("Content-Length", str(len(storage["content"])))
		start_response(str(code) + ' ' + descr, storage["headers"])

		# get content
		content = storage["content"]
	finally:
		# clean thread storage
		storage.remove_thread()

	return [content]

#
# Below are functions callable by user
#

def init(_user_func, ip = "127.0.0.1", port = 9777):
	"""Initialize web module."""

	global user_func

	user_func = _user_func
	addr = (ip, port)
	global serverInstance
	serverInstance = fcgi.WSGIServer(_main, bindAddress = addr)
	
def run():
	"""Listen to requests"""
	return serverInstance.run()
