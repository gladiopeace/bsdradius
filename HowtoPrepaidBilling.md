# Introduction #

In the first document named ["HOWTO: BSDRadius and Gnugk"](HowtoBsdradiusAndGnugk.md)  we discussed basic concepts of setting up BSDRadius with GnuGK gatekeeper. We covered installation of BSDRadius, configuration of BSDRadius and GnuGK to perform simple authentication by username and password and CDR logging into database. Of course, this is far from more or less usable billing system as it cannot do important thing - cannot decrease users balance as calls are being made. One way to do it is by using triggers in database. However, this will not allow to make system really prepaid, as we need to tell GnuGK for how long the user is allowed to speak because there is no way to return database query results back to radius client. Therefore the only way is to write our own module (obviously we will use Python) which would take care of this.

For impatient or non-interested in code internals, there is list of configuration files and MySQL schema file at the end of this document. If you copy them to `etc/bsdradius/` directory of BSDRadius and create MySQL schema, it should start to work immediately. If not, please read on to see what went wrong.

**Contents of this document:**
  1. What we want to achieve
  1. Database schema
  1. Simplebill module for BSDRadius
  1. Configuring BSDRadius
  1. Testing
  1. List of files

# 1. What we want to achieve #

Here is list of requirements we set up for our simple prepaid billing system:
  * Authenticate users by username and password (plaintext and CHAP)
  * Provide enabled / disabled account status check
  * Check positive balance
  * Assign rate table to account
  * Charge calls per minute (Rate per minute)
  * Charge call connection fee (Rate per call)
  * Variuos rate increments
  * Various call grace time
  * Various minimum call duration
  * Multiple destination codes per destination
  * Enable / disable particular destination

**Notes:**
  * The above functions should work with GnuGK gatekeeper, however we may want to add support for different devices in the future (Cisco, Quintum, Mera MVTS, etc).
  * We will use MySQL database due to fact that it is more popular currently. However, we may add support for different engines (Postgres0 in the future as well.
  * We do not have authentication by ANI and IP address. This is left for future versions

# 2. Database schema #

Attached database schema is tested on MySQL 4.1.x, however it should work on MySQL 5.x as well. To be backwards compatible we will not use triggers. To take advantage of foreign keys we will use InnoDB storage engine though. To import database schema into MySQL:
```
# mysql
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 882 to server version: 4.1.18

Type 'help;' or '\h' for help. Type '\c' to clear the buffer.

mysql> create database bsdradius;
Query OK, 1 row affected (0.02 sec)

mysql> exit
Bye
# mysql bsdradius < /path/to/bsdradius/sql/simplebill.mysql.sql
```

Here is the list of tables in our billing database and description of most important tables:
  * table: users
    * name: username of calling endpoint, its H.323 ID
    * password: user password
    * status: (1/0) should be set to 1 to enable calls and allow registrations
    * rateTableId: reference to rate table to be used for this callerS
    * balance: current money amount in users account. Descreases as calls are made. Should be more than 0 for calls to be allowed and endopints to be registered
  * table: rateTables
    * rateTableName: name of the rate table, informational use only
    * table: destinations
    * destDescription: name of the destination, informational use only
  * table: destCodes
    * destCode: country or country+area code of destination
    * destinationId: reference to destination where this code belongs to
  * table: rateItems
    * ratePerCall: tariff of call, per call setup (one time)
    * ratePerMinute: tariff of call, per minute (recurring)
    * increment: tariff charge increment step in whole seconds. Must be 1 sec or more
    * grace: calls shorter than this number of seconds are not charged at all
    * minDur: calls shorter than this amount of seconds will be rounded up tp this duration when charge is applied
    * rateTableId: reference to rate table
    * destinationId: reference to destination
    * status: (1/0) should be set to 1 allow to call this destination
  * table: cdr
    * userId: reference to user who has made this call
    * setupTime: call setup time
    * startTime: call connect time (equals to setup time for unconnected calls)
    * endTime: call disconnect time
    * callingNum: calling (source) number
    * calledNum: called (destination) number
    * h323confid: H.323 conference ID of the call
    * duration: (1/0) call duration
    * callingIp: (1/0) calling IP
    * calledIp: (1/0) called IP
  * table: radiusClients - already described in previous document, please refer to it

# 3. Simplebill module for BSDRadius #

As mentioned above, we will create our own module for BSDRadius. We will call it Simplebill and it should be placed in `etc/bsdradius/user_modules` directory. We will also need configuration file for this module which will hold database driver and access information. The file is `etc/bsdradius/simplebill.conf` and its contents are fairly simple and obvious:
```
# contains settings for connecting to database
[DATABASE]

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
```

Module is written in Python and will be located in `etc/bsdradius/user_modules/simplebill.py`. It will contain several functions as required by Radius server:
  * Startup Function: simplebill\_funct\_startup
  * Authorization Function: simplebill\_funct\_authz
  * Authentication Function: simplebill\_funct\_authc
  * Accounting Function: simplebill\_funct\_acct
  * Shutdown Function: simplebill\_funct\_shutdown

These functions should be referenced in Radius server user modules configuration file

# 4. Configuring BSDRadius #

Once module is made and uploaded we have to tell BSDRadius how to use it. First, we have to make sure it can find users module directory and user modules configuration file (it is set by default, but double check will not harm). Entries in `etc/bsdradius/bsdradiusd.conf` looks like:
```
# path to directory that may contain user's custom modules
user_module_dir = %(conf_dir)s/user_modules

# path to custom (3rd party, user-made) BSD Radius modules
# configuration file.
user_modules_file = %(conf_dir)s/user_modules.conf
```

Next, we have tio configure users module behaviour. This is done in `etc/bsdradius/user_modules.conf`:
```
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

This is basically it. Server now knows where to find functions in case it needs it and if module file `simplebill.py` and its config file `simplebill.conf` is in place, it should be ready to operate.

# 5. Testing #

Testing of BSDRadius is fairly simple and is described in previous document ["HOWTO: BSDRadius and Gnugk"](HowtoBsdradiusAndGnugk.md). As usually, start BSDRadius in debug mode:
```
# cd /whatever/path/to/bsdradius/
# ./bin/bsdradius -sf
```

It will tell you if it was able to find and load all necessary modules at start time, and also if any error occurred in run time. It will log on screeen all radius requests received and also responses sent to GnuGK.

Once you are done with testing, you can start BSDRadius normally to run in background:
```
# cd /whatever/path/to/bsdradius/
# ./bin/bsdradius 
```

# 6. List of files #

Here is the list of configuration files which are used in this document. They should work if directly copied into appropriate directory. It is recommended to change default passwords though.

For BSDRadius:
  * [etc/bsdradius/bsdradiusd.conf](HowtoPrepaidBillingBsdradiusdConf.md)
  * [etc/bsdradius/simplebill.conf](HowtoPrepaidBillingSimplebillConf.md)
  * [etc/bsdradius/user\_modules.conf](HowtoPrepaidBillingUserModulesConf.md)
  * [etc/bsdradius/user\_modules/simplebill.py](HowtoPrepaidBillingSimplebillPy.md)

MySQL schema:
  * [database schema](HowtoPrepaidBillingDatabaseSchema.md)