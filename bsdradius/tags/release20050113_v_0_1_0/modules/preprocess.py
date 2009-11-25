"""
BSD Radius preprocessing module. Changes and adds some
useful attributes in received packet data.
"""


from logging import *



def addMissingAttributes(received):
	"""Add missing attributes such as Client-IP-Address and
		NAS-IP-Address
		Input: (dict) received attributes
		Output: none
	"""
	if 'NAS-IP-Address' not in received:
		info ('Adding missing attribute: NAS-IP-Address')
		received['NAS-IP-Address'] = [received['Client-IP-Address'][0]]



def preprocessAuthorization(received, check, reply):
	"""Do everything that's necessary to prepare received attributes
		for authorization.
		Input: (dict) received, (dict) check, (reply) reply attributes
		Output: (bool) True - success, False - failure
	"""
	addMissingAttributes(received)
	return True
	
	
	
def preprocessAccounting(received):
	"""Do everything that's necessary to prepare received attributes
		for accounting.
		Input: (dict) received
		Output: none
	"""
	addMissingAttributes(received)
