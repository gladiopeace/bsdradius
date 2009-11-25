"""
This module defines some functions which can
be used for default actions in authentication phase
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/tags/release20050113_v_0_1_0/modules/authentication_default.py $
# Author:		$Author: valts $
# File version:	$Revision: 110 $
# Last changes:	$Date: 2006-01-09 21:37:06 +0200 (Pr, 09 Jan 2006) $


from logging import *


def auto_accept(received, check, reply):
	return True
	
def auto_reject(received, check, reply):
	return False
