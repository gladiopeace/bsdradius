"""
Test bsdradius/RadClient.py
"""

# HeadURL		$HeadURL: svn://svn.bsdradius.org/bsdradius/trunk/setup.py $
# Author:		$Author: valts $
# File version:	$Revision: 251 $
# Last changes:	$Date: 2006-06-30 14:44:02 +0300 (Fri, 30 Jun 2006) $


import unittest
import sys
import re

sys.path.insert(0, '../')

from bsdradius.RadClient import RadClient

class RadClientTestCase(unittest.TestCase):
	"""Test RadClient class"""
	dictFile = "../dictionaries/dictionary"
	
	def setUp(self):
		self.client = RadClient(dictFile = self.dictFile)
	
	def testCreateClassInstance(self):
		"""Test RadClient against stupid syntax or typo errors"""
		cl = RadClient(dictFile = self.dictFile,
			host = '127.0.0.1',
			authport = 1812,
			acctport = 1813,
			secret = 'testing123',
			retries = 3,
			timeout = 5
		)
		#print str(cl)
		
	def testGetAuthPacket1(self):
		"""Test getAuthPacket with attributes as dict"""
		pkt = self.client.getAuthPacket({
			'User-Name' : 'Tester',
			'User-Password' : 'password',
		})
		#print str(pkt)
		
	def testGetAuthPacket2(self):
		"""Test getAuthPacket with attributes as dict"""
		pkt = self.client.getAuthPacket(
			User_Name = 'Tester',
			User_Password = 'password',
		)
		#print str(pkt)
		
	def testGetAcctPacket1(self):
		"""Test getAcctPacket with attributes as dict"""
		pkt = self.client.getAcctPacket({
			'User-Name' : 'Tester',
			'Acct-Status-Type' : 'Stop',
		})
		#print str(pkt)
		
	def testGetAcctPacket2(self):
		"""Test getAcctPacket with attributes as dict"""
		pkt = self.client.getAcctPacket(
			User_Name = 'Tester',
			Acct_Status_Type = 'Start',
		)
		#print str(pkt)
		
	def testGenAcctSessionId1(self):
		"""Test genAcctSessionId with default attributes"""
		length = 16
		sessid = self.client.genAcctSessionId()
		self.failUnless(len(sessid) == length)
		for char in sessid:
			self.failUnless(char in self.client.hexSymbols)
		#print sessid
		
	def testGenAcctSessionId2(self):
		"""Test genAcctSessionId with specified attributes"""
		symbols = 'abc123'
		length = 12
		sessid = self.client.genAcctSessionId(length = length, symbols = symbols)
		self.failUnless(len(sessid) == length)
		for char in sessid:
			self.failUnless(char in symbols)
		#print sessid
		
	def testGenH323ConfId(self):
		"""Test genH323ConfId"""
		sessid = self.client.genH323ConfId()
		#print "sessid:", sessid
		self.failUnless(len(sessid) == 35)
		self.failUnless(
			re.match(r'^([%(hex)s]{8} ){3}[%(hex)s]{8}$' % {'hex' : self.client.hexSymbols},
			sessid)
		)
		

def makeSuite():
	"""Collect test cases into suite"""
	return unittest.defaultTestLoader.loadTestsFromTestCase(RadClientTestCase)
