"""
Test bsdradius/BsdRadiusModule.py
"""

# HeadURL		$HeadURL: svn://svn.bsdradius.org/bsdradius/trunk/setup.py $
# Author:		$Author: valts $
# File version:	$Revision: 251 $
# Last changes:	$Date: 2006-06-30 14:44:02 +0300 (Fri, 30 Jun 2006) $


import unittest
import sys

sys.path.insert(0, '../')

from bsdradius.BsdRadiusModule import BsdRadiusModule

class BsdRadiusModuleTestCase(unittest.TestCase):
	"""Test BsdRadiusModule class"""
	def testCreateClassInstance(self):
		"""Test BsdRadiusModule against stupid syntax or typo errors"""
		mod = BsdRadiusModule()
		str(mod)

def makeSuite():
	"""Collect test cases into suite"""
	return unittest.defaultTestLoader.loadTestsFromTestCase(BsdRadiusModuleTestCase)
