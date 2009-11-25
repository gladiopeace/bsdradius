# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/tags/release20050113_v_0_1_0/modules/example2_module.py $
# Author:		$Author: valts $
# File version:	$Revision: 115 $
# Last changes:	$Date: 2006-01-10 21:25:46 +0200 (Ot, 10 Jan 2006) $


# you can use functions defined in logging module to use BSD RAdius's
# logging system.
from logging import *



def example_funct_startup():
	info ("Example2")
	info ("Doing some file opening and stuff like that")
	
	

def example_funct_authz(received, check, reply):
	info ("Example2")
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
	reply['Session-Timeout'] =  630
	reply['Unworthy-value'] = 'shhhh'
	# set up auth type
	check['Auth-Type'] = 'example'
	
	return True
	
	
	
def example_funct_authc(received, check, reply):
	info ("Example2")
	info ("Doing some authentication stuff")
	debug ('Auth-Type: ', check['Auth-Type'])
	return True


	
def example_funct_acct(received):
	info ("Example2")
	info ("Received accounting message")
	debug ("Acct-Status-Type: ", received['Acct-Status-Type'])
	
	
	
def example_funct_shutdown():
	info ("Example2")
	info ("Cleaning up")
