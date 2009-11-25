"""
Defines standalone webserver
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/webstuff/tags/release20061229_v_1_0_0/webstuff/server/standalone_if.py $
# Author:		$Author: valdiic $
# File version:	$Revision: 270 $
# Last changes:	$Date: 2006-10-19 16:57:26 +0300 (Ce, 19 Okt 2006) $


from common_if import *
import SocketServer
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

# server instance
serverInstance = None

class MyHandler(BaseHTTPRequestHandler):
	def proc(self):
		storage.add_thread()
		try:
			# setup thread storage
			storage["headers"] = []
			storage["response"] = (200, "OK")
			storage["content"] = ""

			# get query string
			query_string = ""
			pos = self.path.find('?')
			if pos != -1:
				query_string = self.path[pos+1:]
			
			# store GET variables
			storage["getvars"] = cgi.parse_qs(query_string, True)
			
			# set up environment
			env = {}
			env["REQUEST_METHOD"] = self.command
			env["REQUEST_URI"] = self.path
			env["PATH_INFO"] = self.path
			env["SCRIPT_NAME"] = ''
			env["QUERY_STRING"] = ""
			env["CONTENT_TYPE"] = self.headers.get("Content-Type", "")
			env["CONTENT_LENGTH"] = self.headers.get("Content-Length", "")
			env["HTTP_COOKIE"] = self.headers.get("Cookie", "")
			env["REMOTE_ADDR"] = self.client_address[0]
			env["SERVER_ADDR"] = self.server.server_address[0]
			env["SERVER_PORT"] = str(self.server.server_address[1])
			env["SERVER_PROTOCOL"] = self.request_version
			env["SERVER_SOFTWARE"] = "BaseHTTPServer"
			env["USER_AGENT"] = self.headers.get("User-Agent", "")
			env["ACCEPT"] = self.headers.get("Accept", "")
			env["ACCEPT_LANGUAGE"] = self.headers.get("Accept-Language", "")
			env["ACCEPT_CHARSET"] = self.headers.get("Accept-Charset", "")
			env["ACCEPT_ENCODING"] = self.headers.get("Accept-Encoding", "")
			env["REFERER"] = self.headers.get("Referer", "")

			addr = env["SERVER_ADDR"]
			port = str(env["SERVER_PORT"])
			host_header = self.headers.get("Host", "")
			if host_header != "":
				env["SERVER_NAME"] = host_header
			else:
				env["SERVER_NAME"] = addr + ":" + port

			# store POST
			storage["postvars"] = cgi.parse(self.rfile, env, 1)

			# store cookies
			cookie_obj = Cookie.SimpleCookie()
			cookie_obj.load(env["HTTP_COOKIE"])
			cookies = {}
			for key, morsel in cookie_obj.iteritems():
				cookies[key] = morsel.value
			storage["cookies"] = cookies

			# store environment
			env["QUERY_STRING"] = query_string
			storage["env"] = env
			
			# execute user function
			self.server.user_func()
			
			# write response, headers, a blank line and the output
			code, descr = storage["response"]
			self.send_response(code, descr)

			header("Content-Length", len(storage["content"]))
			for key, value in storage["headers"]:
				self.send_header(key, value)
			self.wfile.write("\r\n")

			self.wfile.write(storage["content"])
		finally:
			# clean thread storage
			storage.remove_thread()
	
	def do_GET(self):
		self.proc()

	def do_POST(self):
		self.proc()

class MyServer(SocketServer.ThreadingMixIn, HTTPServer):
	def __init__(self, addr, user_func):
		HTTPServer.__init__(self, addr, MyHandler)
		self.user_func = user_func

#
# Below are functions callable by user
#

def init(user_func, ip = "127.0.0.1", port = 8000):
	"""Initialize standalone HTTP server."""
	
	addr = (ip, port)
	global serverInstance
	serverInstance = MyServer(addr, user_func)
	
def run():
	"""Listen to requests"""
	return serverInstance.serve_forever()
