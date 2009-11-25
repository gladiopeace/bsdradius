
from webstuff.framework import *

def list(type):
#	web.header("Content-Type", "text/plain")
	web.output("you wish to list accounts with type: <b>%s</b>" % type)


def edit(id):
	web.header("Content-Type", "text/plain")
	web.output("you wish to <i>edit</i> account with id: " + id)
