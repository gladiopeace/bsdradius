"""
Defines CGI interface.
I don't suggest to realy on this module because it has never
been actually tested or used.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/webstuff/tags/release20061229_v_1_0_0/webstuff/server/cgi_if.py $
# Author:		$Author: atis $
# File version:	$Revision: 59 $
# Last changes:	$Date: 2006-07-17 16:44:00 +0300 (Pr, 17 Jūl 2006) $


from common_if import *
import os, cgi, sys

user_func = None

def init(_user_func, ip = '', port = 0):
	"""Store user function.
		Ip and port attributes are just for compatibility with
		other server interface modules. They are not really
		used anywhere.
	"""
	# store user function
	global user_func
	user_func = _user_func
	
def run():
	storage.add_thread()

	try:
		storage["headers"] = []
		storage["response"] = (200, "OK")
		storage["content"] = ""
		
		# retrieve GET variables
		getvars = {}
		if os.environ.has_key("QUERY_STRING"):
			getvars = cgi.parse_qs(os.environ["QUERY_STRING"], True)
		storage["getvars"] = getvars

		# retrieve POST variables
		storage["postvars"] = cgi.FieldStorage()

		# store cookies
		cookie_obj = Cookie.SimpleCookie()
		cookie_obj.load(os.environ.get("HTTP_COOKIE", ""))
		cookies = {}
		for key, morsel in cookie_obj.iteritems():
			cookies[key] = morsel.value
		storage["cookies"] = cookies
		
		# execute user function
		user_func()

		# send status header
		response = storage["response"]
		print "Status: %s %s" % response
	
		# print headers
		header("Content-Length", len(storage["content"]))
		for key, value in storage["headers"]:
			print "%s: %s" % (key, value)
		print "\n",
		print storage["content"]
		return None
	finally:
		storage.remove_thread()
