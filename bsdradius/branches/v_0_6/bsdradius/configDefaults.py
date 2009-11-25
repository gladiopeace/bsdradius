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
Define configuration defaults here
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_6/bsdradius/configDefaults.py $
# Author:		$Author: valts $
# File version:	$Revision: 279 $
# Last changes:	$Date: 2006-11-26 16:13:13 +0200 (Sv, 26 Nov 2006) $

prefix = '/usr/local'

# define default values
# format: {'section' : {'option' : value}}
defaultOptions = {
	'PATHS' : {
		'prefix' : prefix,
		'conf_dir' : '%(prefix)s/etc/bsdradius',
		'run_dir' : '%(prefix)s/var/run',
		'log_dir' : '%(prefix)s/var/log/bsdradius',
		'user_module_dir' : '%(conf_dir)s/user_modules',
		'dictionary_dir' : '%(prefix)s/share/bsdradius/dictionaries',
		'dictionary_file' : '%(dictionary_dir)s/dictionary',
		'server_log_file' : '%(log_dir)s/bsdradiusd.log',
		'pid_file' : '%(run_dir)s/bsdradiusd.pid',
		'clients_file' : '%(conf_dir)s/clients.conf',
		'modules_file' : '%(conf_dir)s/modules.conf',
		'user_modules_file' : '%(conf_dir)s/user_modules.conf',
		'config_file' : '%(conf_dir)s/bsdradiusd.conf'
	},
	'SERVER' : {
		'home' : '',
		'user' : '',
		'group' : '',
		'auth_port' : '1812',
		'acct_port' : '1813',
		'number_of_threads' : '10',
		'foreground' : 'no',
		'no_threads' : 'no',
		'log_to_screen': 'no',
		'log_to_file' : 'no',
		'debug_mode' : 'no',
		'log_client' : '',
		'fast_accounting': 'no',
	},
	'DATABASE' : {
		'enable' : 'no',
		'type' : 'postgresql',
		'host' : 'localhost',
		'user' : 'bsdradius',
		'pass' : '',
		'name' : 'bsdradius',
		'refresh_rate' : '60',
		'clients_query' : 'select address, name, secret from radiusClients',
	},
	'AUTHORIZATION' : {
		'packet_timeout' : '5',
		'auth_queue_maxlength' : '300',
		'modules' : '',
	},
	'ACCOUNTING' : {
		'acct_queue_maxlength' : '300',
		'modules' : '',
	},
}

# Define option types.
# It is really neccessary to define only other types
# than string because Config parser converts everything
# to string by default.
# Format: {'section' : {'option' : 'type'}}
defaultTypes = {
	'SERVER' : {
		'auth_port' : 'int',
		'acct_port' : 'int',
		'number_of_threads' : 'int',
		'foreground' : 'bool',
		'no_threads' : 'bool',
		'log_to_screen': 'bool',
		'log_to_file': 'bool',
		'debug_mode' : 'bool',
		'fast_accounting': 'bool',
	},
	'DATABASE' : {
		'enable' : 'bool',
		'refresh_rate' : 'int',
	},
	'AUTHORIZATION' : {
		'packet_timeout' : 'int',
		'auth_queue_maxlength' : 'int',
	},
	'ACCOUNTING' : {
		'acct_queue_maxlength' : 'int',
	},
}



# configuration defaults for one BSD Radius module
moduleConfigDefaults = {
	'enable': 'yes',
	'configfile': '',
	'startup_module': '',
	'startup_function': '',
	'authorization_module': '',
	'authorization_function': '',
	'authentication_module': '',
	'authentication_function': '',
	'accounting_module': '',
	'accounting_function': '',
	'shutdown_module': '',
	'shutdown_function': '',
}
