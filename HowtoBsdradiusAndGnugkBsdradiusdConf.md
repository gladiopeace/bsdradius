
```
# BSD Radius config file
# Must be located in system config file
# directory (/usr/local/etc/bsdradius/)

# Configure file and directory paths
[PATHS]

# server directory root
prefix = /home/aivis/projects/bsdradius/trunk

# path to directory that conatins configuration files
conf_dir = %(prefix)s/etc/bsdradius

# path to var/run type directory
run_dir = %(prefix)s/var/run/bsdradius

# path to log directory
log_dir = %(prefix)s/var/log/bsdradius

# path to directory that contains dictionary files
dictionary_dir = %(prefix)s/share/bsdradius/dictionaries

# path to directory that may contain user's custom modules
user_module_dir = %(conf_dir)s/user_modules

# path to dictionary file
dictionary_file = %(dictionary_dir)s/dictionary

# path to server log file
server_log_file = %(log_dir)s/bsdradiusd.log

# path to pid file
pid_file = %(run_dir)s/bsdradiusd.pid

# path to radius server clients file
# comment out this line to disable client lookup in file
clients_file = %(conf_dir)s/clients.conf

# path to BSD Radius internal modules configuration file
modules_file = %(conf_dir)s/modules.conf

# path to custom (3rd party, user-made) BSD Radius modules
# configuration file.
user_modules_file = %(conf_dir)s/user_modules.conf



# Configure server IP address, ports, etc.
[SERVER]

# home IP address
# comment out this line to bind server to all network interfaces
#home = 127.0.0.1

# After performing initial tasks BSD Radius will switch to user and
# group mentioned below. To run BSD Radius server as current user comment
# these lines
user = nobody
group = nobody

# UDP port used for authorization and authentication
auth_port = 1812

# UDP port used for accounting
acct_port = 1813

# Number of packet processing threads.
# Set it to 1 to disable parallel packet processing.
# You can achieve the same effect by passing -n or --no-threads to
# BSD Radius server through cmd line.
number_of_threads = 10

# enable or disable logging to file
log_to_file = no



# contains settings for connecting to database
[DATABASE]

# enable or disable configuration data lookup in database
enable = yes

# database type
# Suppored RDMS': postgresql, mysql
type = mysql

# db host
host = localhost

# db user
user = bsdradius

# db user password
pass = somepass

# db name
name = bsdradius

# configuration data refresh rate in seconds
refresh_rate = 60



# Authorization section
[AUTHORIZATION]

# Auhorization packet is dropped if it has been waiting at least
# auth_timeout seconds.
packet_timeout = 5

# Maximum number of packets that are allowed to be kept in queue before processing
auth_queue_maxlength = 300

# Configure order of modules for execution seperating them with commas.
# Include your custom modules if neccessary.
# Modules will be executed in order from left to right.
modules = preprocess, chap, digest, dump_packet, usersfile, sql



# Mapping auth types to corresponding modules
# Auth types can be set in authorization phase in any module for later checking
# collected data. It is useful for chap, md5 and digest authorization tools.
# Use auth type name in left side and module name in right side
[AUTH_TYPES]

# Default authorization type. (Auth-Type = None)
# Change it's value to auto_reject if you wish to reject messages without
# specific auth type by default
default = auto_reject

# Check against CHAP authentication method
chap = chap

# Check against DIGEST authentication method
digest = digest

# Example auth type that has to be handled with example module
example = example_mod

# Check if account is authorized via sql module
sql = sql

# Check if account is authorized via usersfile module
usersfile = usersfile



# Accounting section
[ACCOUNTING]

# Maximum number of packets that are allowed to be kept in queue before processing
acct_queue_maxlength = 300

# Configure order of modules for execution seperating them with commas.
# Include your custom modules if neccessary.
# Modules will be executed in order from left to right.
modules = preprocess, dump_packet, sql
```