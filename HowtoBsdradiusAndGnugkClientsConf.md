
```
# configure radius server clients
# use client's hostname or ip address as section name.
# section's name must be unique.


# Example IP - localhost. You can use named hosts too.
[127.0.0.1]
# client's name. Ex: test1, john etc.
name = local
# secret password. 
# It's known by both - server and client - but never sent over network
secret = gktest123


# Another example.
# Don't use it in real environment :)
#[10.1.3.4]
#name = local network host 4
#secret = shouldntwork
```