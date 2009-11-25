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

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/tags/release20050113_v_0_1_0/modules/example_module.py $
# Author:		$Author: valts $
# File version:	$Revision: 122 $
# Last changes:	$Date: 2006-01-13 19:46:51 +0200 (Pk, 13 Jan 2006) $


# you can use functions defined in logging module to use BSD RAdius's
# logging system.
from logging import *



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
	check['Auth-Type'] = 'example'
	
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
	received['Acct-Status-Type'] = 'Start'
	
	
	
def example_funct_shutdown():
	"""Do some cleanup tasks here. Close opened files and database
		connections, for example
		Input: none
		Output: none
	"""
	info ("Cleaning up")
