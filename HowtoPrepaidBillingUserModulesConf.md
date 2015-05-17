
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


[simplebill]
configfile = simplebill.conf
startup_module = simplebill
startup_function = simplebill_funct_startup
authorization_module = simplebill
authorization_function = simplebill_funct_authz
authentication_module = simplebill
authentication_function = simplebill_funct_authc
accounting_module = simplebill
accounting_function = simplebill_funct_acct
shutdown_module = simplebill
shutdown_function = simplebill_funct_shutdown
```