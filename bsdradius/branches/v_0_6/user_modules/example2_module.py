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

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_6/user_modules/example2_module.py $
# Author:		$Author: valts $
# File version:	$Revision: 201 $
# Last changes:	$Date: 2006-04-04 17:22:11 +0300 (Ot, 04 Apr 2006) $


# you can use functions defined in logger module to use BSD RAdius's
# logger system.
from bsdradius.logger import *
from types import *



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
	if not isinstance(reply['Reply-Message'], ListType):
		tmp = reply['Reply-Message']
		reply['Reply-Message'] = [tmp]
	reply['Reply-Message'].append("BSD Radius server rules")
	reply['Session-Time'] =  [10]
	reply['Session-Timeout'] =  630
	reply['Unworthy-value'] = 'shhhh'
	# set up auth type
	check['Auth-Type'] = ['example']
	
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
