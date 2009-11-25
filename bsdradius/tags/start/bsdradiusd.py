#!/usr/local/bin/python
"""
VoIP Radius
Data Tech Labs radius server.
Made specially for VoIP needs.
"""

# RCS filename:			$RCSfile$
# Author:				$Author: root $
# File version:			$Revision: 75 $
# Last changes (GMT):	$Date: 2005-11-29 21:56:55 +0200 (Ot, 29 Nov 2005) $
# Branch (or tag):		$Name$



# import modules
import sys
sys.path.insert(0, './lib')
from pyrad import server, dictionary
# bsdradius modules
import BsdRadiusServer


print "Starting server"
dict = dictionary.Dictionary('/usr/home/valdiic/dev/bsdradius/dictionaries/dictionary')
#sys.exit(0)

srv = BsdRadiusServer.BsdRadiusServer(dict=dict)
# add valid server client hosts
srv.hosts["127.0.0.1"] = server.RemoteHost("127.0.0.1","testing123","localhost")

# bind to all IP addresses
srv.BindToAddress("")

# run server
srv.Run()
