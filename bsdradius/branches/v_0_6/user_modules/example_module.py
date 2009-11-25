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
BSD Radius server example module
This module conatins trivial examples how to create modules for using
them into BSD Radius server.

Received, check and reply packets should be (or behive like) dictionaries. 
Format: {'key1': ['value1', 'value2', ...], 'key2': [...]}

Use exceptions in case of failure.
Use return values in authorization and authentication functions
to tell the server if user is ok or not.

"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_6/user_modules/example_module.py $
# Author:		$Author: valts $
# File version:	$Revision: 201 $
# Last changes:	$Date: 2006-04-04 17:22:11 +0300 (Ot, 04 Apr 2006) $


# you can use functions defined in logger module to use BSD RAdius's
# logger system.
from bsdradius.logger import *
import types


def example_funct_startup():
	"""Function which is meant to be called during server
		Startup. You should do some initializing work. For ex.,
		open files, connect to database etc.
		Input: none
		Output: none
	"""
	info ("Doing some file opening and stuff like that")
	
	

def example_funct_authz(received, check, reply):
	"""Do some authorization tasks here. Get username, 
		password from file or database, for example.
		Input: (dict) received data, (dict) check data, (dict) reply data
		Output: (bool) True - success, False - failure
		NOTE: since all function attributes in python are passed by reference
			it is possible to modify 'received', 'check' and attributes.
	"""
	info ("Looking for username and password")
	debug ("Received packet:")
	debug (received)
	debug ("Check data")
	debug (check)
	debug ("Reply data")
	debug (reply)
	
	# prepare reply message
	reply['Reply-Message'] = "It's cool, pal"
	reply['Session-Time'] =  10
	reply['Session-Timeout'] =  330
	# set up auth type
	authType = check['Auth-Type'][0]
	if not authType:
		check['Auth-Type'] = 'example'
	elif authType == 'chap' or authType == 'digest':
		# add plaintext user password to check items
		check['User-Password'] = '1016'
		check['User-Name'] = 'test'
	
	return True
	
	
	
def example_funct_authc(received, check, reply):
	"""Do some authentication tasks here. Check username and
		password against chap, md5, digest or something like that
		Input: (dict) received data, (dict) check data, (dict) reply data
		Output: (bool) True - success, False - failure
		NOTE: since all function attributes in python are passed by reference
			it is possible to modify 'received', 'check' and attributes.
	"""
	info ("Doing some authentication stuff")
	debug ('Auth-Type: ', check['Auth-Type'])
	return True


	
def example_funct_acct(received):
	"""Do some accounting tasks here. Log received accounting stop message,
		reduce user's balance.
		Input: (dict) received
		Output: none
	"""
	info ("Received accounting message")
	debug ("Acct-Status-Type: ", received['Acct-Status-Type'])
	received['Acct-Status-Type'] = ['Start']
	
	
	
def example_funct_shutdown():
	"""Do some cleanup tasks here. Close opened files and database
		connections, for example
		Input: none
		Output: none
	"""
	info ("Cleaning up")
