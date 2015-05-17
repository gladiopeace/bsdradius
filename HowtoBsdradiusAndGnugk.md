# Introduction #

This step-by-step guide is attempt to explain how to setup and configure BSDRadius to perform AAA requests from GnuGK gatekeeper. This procedure generally should fit any H.323 device. The aim is to provide AAA from database, i.e. we will keep user records in database and record Accounting requests to database rather than text file.

We will perform tasks in following order:
  1. Install and Start BSDRadius
  1. Configure GnuGK
  1. Establish communication between BSDRadius and GnuGK
  1. Setup database and configure SQL modules

# 1. Install and Start BSDRadius #

Once you unpack BSDRadius tar.gz file, please look at included `README` file. It will tell versions on Python and database support libraries. Note that Python 2.4 or newer is required to compile and run BSDRadius. One of database modules also is needed. Your can choose between MySQL and Postgresql but we will discuss MySQL, leaving Postgres for later. It has some nice features which can be useful for advanced setups. However MySQL is easier to understand and maintain.

To setup BSDRadius, type:
```
# python setup.py install --prefix=/whatever/path/to/bsdradius/
```

It will install binaries, config and lib files in directory specified by prefix. Note that all config files are located in `/whatever/path/to/bsdradius/etc/bsdradius/` directory.

By default BSDRadius installs itself under `/usr/local/` directory prefix. Passing specific prefix is advisable to be able to remove whole BSDRadius installation in case when something goes wrong.

You can start the server in foreground, to see if there are no errors at start time:

```
# cd /whatever/path/to/bsdradius/
# ./bin/bsdradiusd -sf
```

Indication of successful startup is list of lines like these at the end of start screen:

```
--- Starting server ---
--- Started Listen thread ---
--- started Working thread 0 ---
--- started Working thread 1 ---
--- started Working thread 2 ---
--- started Working thread 3 ---
--- started Working thread 4 ---
--- started Working thread 5 ---
--- started Working thread 6 ---
--- started Working thread 7 ---
--- started Working thread 8 ---
--- started Working thread 9 ---
```

Once BSDRadius is started, we should configure GnuGK for it.

# 2. Configure GnuGK #

We will discuss GnuGK sections related to AAA only here. Other sections are specific to particular setup and are not discussed. For impatient, however, here is full sample config file used in this example.

To enable authentication, please configure following sections:

```
[Gatekeeper::Auth]
RadAliasAuth=required;ARQ,RRQ,SetupUnreg

[RadAliasAuth]
Servers=127.0.0.1
LocalInterface=127.0.0.1
DefaultAuthPort=1812
SharedSecret=gktest123
RequestTimeout=3500
IdCacheTimeout=9000
SocketDeleteTimeout=60000
RequestRetransmissions=2
AppendCiscoAttributes=1
IncludeEndpointIP=1
UseDialedNumber=1
```

This will make require GnuGK to send Access-Request messages to Radius server in following cases:
  1. RAS Registration request (RRQ)
  1. RAS Admission request (ARQ)
  1. Q.931 Call Setup from unregistered endpoints

Note, that in order to make 3rd case working you will need to allow calls from Unregistered Endpoints:
```
[RoutedMode]
AcceptUnregisteredCalls=1
```

The above example is simplest method of Authentication, however it is not secure as no real passwords are used. GnuGK will substitute password with endpoints H.323ID which is not secure. More secure method is to enable CHAP based passwords. BSDRadius supports it by default, so there is no configuration needed on that side, only changes in GnuGK. Main change is to use `RadAuth` method instead of `RadAliasAuth`.
```
[Gatekeeper::Auth]
RadAuth=required;ARQ,RRQ

[RadAuth]
Servers=127.0.0.1
LocalInterface=127.0.0.1
DefaultAuthPort=1812
SharedSecret=gktest123
RequestTimeout=5000
IdCacheTimeout=9000
SocketDeleteTimeout=60000
RequestRetransmissions=2
AppendCiscoAttributes=1
IncludeEndpointIP=1
UseDialedNumber=1
```

Note, that unregistered calls do not have H.235 tokens, therefore we have to either disable them or keep `RadAliasAuth` method along with it.

Finally, enable accounting:
```
[Gatekeeper::Acct]
RadAcct=required;start,stop,update,on,off

[RadAcct]
Servers=127.0.0.1
LocalInterface=127.0.0.1
DefaultAcctPort=1813
SharedSecret=gktest123
RequestTimeout=5000
IdCacheTimeout=9000
SocketDeleteTimeout=60000
RequestRetransmissions=4
AppendCiscoAttributes=1
UseDialedNumber=1
```

Do not forget to reload GnuGK configuration after changes have been made.

# 3. Establish communication between BSDRadius and GnuGK #

There are 2 methods of keeping GnuGK IP and shared secret in BSDRadius configuration. Simplest way is to keep them in file. You can modify sample entry in `etc/bsdradius/clients.conf` file:
```
[127.0.0.1]
name = local
secret = gktest123
```

After this you can make test RRQ or ARQ on GnuGK. It will not work, but you should be able to see at least successful message in BSDRadius console. It will call all enabled modules in attempt of authenticating client. Output will be like this:
```
thread "Working thread 7" grabbed a packet for processing
--AuthPacket--------------------------------------------------
'User-Password': '\xfb\xf9\xc0\xd1\x93\x8d1C\xc6\xa4\xb1t\x9d\xa23\x81'
'NAS-IP-Address': '127.0.0.1'
'User-Name': '10002'
'Cisco-AVPair': 'h323-ivr-out=terminal-alias:10002,10002;'
'Framed-IP-Address': '10.1.1.242'
'Request-Authenticator': 'KoV\xba\xb4Nz\x0e\x8b1\n\x93\x88\x9b_\x16'
'Service-Type': 'Login-User'
'NAS-Identifier': 'aivis'
'Client-IP-Address': '127.0.0.1'
'NAS-Port-Type': 'Virtual'
```

The other method is to keep NAS data in database. It is useful if you have many of them and you want to do some reporting based on particular gatekeeper. To make it work, we need to setup database.

# 4. Setup database and configure SQL modules #

Default database schema is located in original source directory of BSDRadius, in sql/ directory. To import database schema into MySQL:
```
# mysql
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 882 to server version: 4.1.18

Type 'help;' or '\h' for help. Type '\c' to clear the buffer.

mysql> create database bsdradius;
Query OK, 1 row affected (0.02 sec)

mysql> exit
Bye
# mysql bsdradius < /path/to/bsdradius/sql/bsdradius.mysql.sql
```

Created schema will allow both to keep NAS data in database and also do AAA from same database. Let's first put NAS data into it. If you don't want to do it, you can keep it file.
```
mysql> grant select, update, insert, delete on bsdradius.* to bsdradius@localhost identified by 'somepass';
mysql> insert into radiusClients (address, name, secret) values ('127.0.0.1','gnugk','gktest123');
```

Configure database support in main BSDRadius config file `etc/bsdradius/bsdradiusd.conf`:
```
# contains settings for connecting to database
[DATABASE]

# enable or disable configuration data lookup in database
enable = yes

type = mysql

host = localhost

user = bsdradius

pass = somepass

name = bsdradius
```

Once this is done, we can configure SQL modules for endpoint authorization. Built-in default SQL module is not enabled by default, but can be enabled simply by setting `enable = yes` in `[sql]` section of `etc/bsdradius/modules.conf` file. The section should look like this:
```
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
```

It also tells location of SQL module configuration file: `mod_sql.conf` - we should tell what database to use and provide access info for module. in `etc/bsdradius/mod_sql.conf`
```
[ACCESS]
type = mysql

host = localhost

user = bsdradius

pass = somepass

name = bsdradius
```

It is also necessary to disable dummy `example_mod` and `example_mod2` as they always send accept, but actually do nothing. (Probably they should be disabled in future releases?). In `etc/bsdradius/bsdradiusd.conf`:
```
......
[AUTHORIZATION]
modules = preprocess, chap, digest, dump_packet, usersfile, sql
......
[ACCOUNTING]
......
modules = preprocess, dump_packet, sql
......
```

Let's enter some user info into database:
```
mysql> insert into users (name, password) values ('10001','10001');
```

This should be it. After making call, CDRs are located in cdr table. To retrieve them, do following query:
```
mysql> select * from cdr;
```

As mentioned at the beginning, this was simple example which shows how to set simple authentication and CDR logging into database. Next time we will discuss more advanced things such as: checking and controlling number of simultaneous calls, rate tables, etc.

Here is the list of configuration files which are used in this document. They should work if directly copied into appropriate directory. It is recommended to change default passwords though.

For gnugk:
  * [gnugk.ini](HowtoBsdradiusAndGnugkGnugkIni.md)

For BSDRadius:
  * [etc/bsdradius/bsdradiusd.conf](HowtoBsdradiusAndGnugkBsdradiusdConf.md)
  * [etc/bsdradius/clients.conf](HowtoBsdradiusAndGnugkClientsConf.md)
  * [etc/bsdradius/mod\_sql.conf](HowtoBsdradiusAndGnugkModSqlConf.md)
  * [etc/bsdradius/modules.conf](HowtoBsdradiusAndGnugkModulesConf.md)