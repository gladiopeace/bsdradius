
```
    [ACCESS]
# database type
# Suppored types: postgresql, mysql
type = mysql
#type = postgresql

# db host
host = localhost

# db user
user = bsdradius

# db user password
pass = somepass 

# db name
name = bsdradius


# Define sql queries here.
# You can use whatever request attributes you like. Just replace "-" with "_" in
# attribute names and put dollar sign ("$") in front of them.
# For example, to get attribute "Called-Station-Id" use $Called_Station_Id.
# To be absolutely sure that sql module will understand you right you can put
# attribute name in brackets like this: ${Called_Station_Id}
# If you want to use dollar sign into your sql queries just use two of them
# instead of one: $$
# Don't be afraid of what happens if server doesn't receive all attributes you've
# placed into queries. The request will be logged into "failed requests" directory.
# Just be sure you haven't disabled logging of failed requests.
[AUTHORIZATION]
# sql query for looking up for user in database
# It is advisable to select username and password as 1st two attributes
# for modules which require them in authentication (chap, digest)
authz_query = select name, password from users where name = '$User_Name' and password ='$User_Password'


[ACCOUNTING]
# This query is executed when accounting start request received.
# You can use it for keeping list of active calls. To remove finished calls define some
# logic (triggers on accounting stop message query) in database.
acct_start_query = insert into calls (name, calling_num, called_num, call_duration, h323confid)
	values ('$User_Name', '$Calling_Station_Id', '$Called_Station_Id', 0, '$h323_conf_id')

# This query is executed when accounting update request received.
# Use it for updating call status in active calls' table
acct_update_query = update calls set call_duration = $Acct_Session_Time where h323confid = '$h323_conf_id'

# This query is executed when accounting stop request received.
acct_stop_query = insert into cdr (name, setup_time, start_time, end_time,
	calling_num, called_num, h323confid)
	values ('$User_Name', '$h323_setup_time', '$h323_connect_time',
	'$h323_disconnect_time', '$Calling_Station_Id', '$Called_Station_Id', '$h323_conf_id')
```