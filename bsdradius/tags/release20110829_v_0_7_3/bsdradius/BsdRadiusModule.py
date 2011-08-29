## BSDRadius is released under BSD license.
## Copyright (c) 2006, DATA TECH LABS
## All rights reserved. 
## 
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met: 
## * Redistributions of source code must retain the above copyright notice,
##   this list of conditions and the following disclaimer. 
## * Redistributions in binary form must reproduce the above copyright notice,
##   this list of conditions and the following disclaimer in the documentation
##   and/or other materials provided with the distribution. 
## * Neither the name of the DATA TECH LABS nor the names of its contributors
##   may be used to endorse or promote products derived from this software without
##   specific prior written permission. 
## 
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
## ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""
BSD Radius internal module class definion
Use this class to describe all modules that are loadable
by BSD Radius server.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_7/bsdradius/BsdRadiusModule.py $
# Author:		$Author: valts $
# File version:	$Revision: 215 $
# Last changes:	$Date: 2006-05-17 12:48:27 +0300 (Tr, 17 Mai 2006) $



class BsdRadiusModule:
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
		# Custom configuration data. Config class instance if present, None otherwise
		self.radParsedConfig = None
		# holds references to modules and functions
		self.startup_module		= None
		self.startup_funct		= None
		self.authz_module		= None
		self.authz_funct		= None
		self.authc_module		= None
		self.authc_funct		= None
		self.acct_module		= None
		self.acct_funct			= None
		self.shutdown_module	= None
		self.shutdown_funct		= None
		# shows what module is able to do
		self.startupCapable			= False
		self.authorizationCapable	= False
		self.authenticationCapable	= False
		self.accountingCapable		= False
		self.shutdownCapable		= False
		
		
		
	def __str__(self):
		"""Print module name and configuration parameters
			Input: none
			Output: (string) formatted contents for better reading
		"""
		ret = "%s\n" % self.name
		for key, value in vars(self).iteritems():
			if key == 'name' or key == 'radParsedConfig':
				continue
			ret += '  %s: %s\n' % (key, value)
		return ret
