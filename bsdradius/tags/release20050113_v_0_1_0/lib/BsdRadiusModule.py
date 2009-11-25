"""
BSD Radius internal module class definion
Use this class to describe all modules that are loadable
by BSD Radius server.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/tags/release20050113_v_0_1_0/lib/BsdRadiusModule.py $
# Author:		$Author: valts $
# File version:	$Revision: 110 $
# Last changes:	$Date: 2006-01-09 21:37:06 +0200 (Pr, 09 Jan 2006) $


from UserDict import UserDict


class BsdRadiusModule(UserDict):
	"""Class that describes internal BSD Radius server modules. Modules have to
		be configured by user in appropiate config file.
	"""
	
	def __init__(self, name = ''):
		"""Constructor
			Input: (string) module name
			Output: (BsdRadiusModule) class instance
		"""
		# BSD Radius module name
		self.name = name
		# holds references to modules and functions
		self.data = {
			'startup_module':	None,
			'startup_funct':	None,
			'authz_module':		None,
			'authz_funct':		None,
			'authc_module':		None,
			'authc_funct':		None,
			'acct_module':		None,
			'acct_funct':		None,
			'shutdown_module':	None,
			'shutdown_funct':	None,
		}
		self.startupCapable			= False
		self.authorizationCapable		= False
		self.authenticationCapable	= False
		self.accountingCapable		= False
		self.shutdownCapable			= False
		
		
		
	def __str__(self):
		"""Print module name and configuration parameters
			Input: none
			Output: (string) formatted contents for better reading
		"""
		ret = "%s\n" % self.name
		for key, value in self.items():
			ret += '  %s: %s\n' % (key, value)
		return ret
