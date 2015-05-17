
```
# Configure loadable Bsdradius modules here.
# Use modules name as section name (in square brackets)
# You can use configured modules later in authorization
# and accounting sections in main configuration file.
# 
# Each module configuration must define python module name
# and function name for each section where it will be used.
# NOTE: All python modules must be loadable by python. It means
# that you can set up environment variable PYTHONPATH or use use
# standard directories where to store python modules
#
# Configuration options are:
# [module_name] - internal BSD Radius module name.
#   Don't mix it with pure python module ;)
# enable - enable or disable particular BSDRadius module
# configfile - path to custom configuration file for BSDRadius module. If path is
#   relative (doesn't contain / as 1-st symbol) BSDRadius will search the file in
#   conf_dir directory (take a look at bsdradiusd.conf).
# startup_module - name of module which holds startup_function
# startup_function - name of function which has to be called in server startup phase
#    You can use this function to open files, db connections etc.
# authorization_module - name of module which holds authorization_function
# authorization_function - name of function which has to be called in authorization phase
# authentication_module - name of module which holds authentication_function
# authentication_function - name of function which has to be called in authentication phase
# accounting_module - name of module which holds accounting_function
# accounting_function - name of function which has to be called in accounting phase
# shutdown_module - name of module which holds shutdown_function
# shutdown_function - name of function which has to be called in server
#   shutdown phase. You can use this function for cleanup purposes, close files
#   and db connections (those which you opened in startup phase, for example)

# Use this module to accept by default in authentication phase
[auto_accept]
authentication_module = authentication_default
authentication_function = auto_accept

# Use this module to reject by default in authentication phase
[auto_reject]
authentication_module = authentication_default
authentication_function = auto_reject

# packet dumping module
[dump_packet]
configfile = dump_packet.conf
authorization_module = dumpPacket
authorization_function = dumpAuthPacket
accounting_module = dumpPacket
accounting_function = dumpAcctPacket

# preapre received attributes for further processing
[preprocess]
authorization_module = preprocess
authorization_function = preprocessAuthorization
accounting_module = preprocess
accounting_function = preprocessAccounting

[chap]
authorization_module = mod_chap
authorization_function = chapAuthorization
authentication_module = mod_chap
authentication_function = chapAuthentication

[digest]
authorization_module = mod_digest
authorization_function = digestAuthorization
authentication_module = mod_digest
authentication_function = digestAuthentication

# mod_sql: simple module for keeping user data in SQL database
[sql]
enable = yes
configfile = mod_sql.conf
startup_module = mod_sql
startup_function = startup
authorization_module = mod_sql
authorization_function = authorization
authentication_module = mod_sql
authentication_function = authentication
accounting_module = mod_sql
accounting_function = accounting
shutdown_module = mod_sql
shutdown_function = shutdown

# look for user data in static file
[usersfile]
configfile = usersfile.conf
authorization_module = mod_usersfile
authorization_function = authorization
authentication_module = mod_usersfile
authentication_function = authentication
```