"""
Define configuration defaults here
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/tags/release20050113_v_0_1_0/lib/configDefaults.py $
# Author:		$Author: valts $
# File version:	$Revision: 122 $
# Last changes:	$Date: 2006-01-13 19:46:51 +0200 (Pk, 13 Jan 2006) $


# define default values
# format: {'section' : {'option' : value}}
defaultOptions = {
	'PATHS' : {
		'prefix' : '/usr/local',
		'conf_dir' : '%(prefix)s/etc/bsdradius',
		'run_dir' : '%(prefix)s/var/run',
		'log_dir' : '%(prefix)s/var/log',
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
	},
	'DATABASE' : {
		'enable' : 'no',
		'type' : 'postgresql',
		'host' : 'localhost',
		'user' : 'bsdradius',
		'pass' : '',
		'name' : 'bsdradius',
		'refresh_rate' : '60',
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
		'debug_mode' : 'bool',
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
