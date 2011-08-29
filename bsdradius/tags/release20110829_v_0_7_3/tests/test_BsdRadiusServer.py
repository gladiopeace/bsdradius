"""
Test bsdradius/BsdRadiusModule.py
"""

# HeadURL		$HeadURL: svn://svn.bsdradius.org/bsdradius/trunk/setup.py $
# Author:		$Author: valts $
# File version:	$Revision: 251 $
# Last changes:	$Date: 2006-06-30 14:44:02 +0300 (Fri, 30 Jun 2006) $


import unittest
import sys, threading

sys.path.insert(0, '../')

from bsdradius.BsdRadiusServer import BsdRadiusServer, RemoteHost, BaseThread, \
	WorkingThread, ListenThread


class BsdRadiusServerTestCase(unittest.TestCase):
	"""Test BsdRadiusServer class"""
	def setUp(self):
		self.srv = BsdRadiusServer(addresses = ['127.0.0.1'])
		
	def tearDown(self):
		del self.srv

	def testCreateClassInstance(self):
		"""Test BsdRadiusModule against stupid sytax or typo errors"""
		str(self.srv)
	
	def testBindToAddress(self):
		# we need to free the binding address at first
		del self.srv
		self.srv = BsdRadiusServer()
		self.srv.BindToAddress("localhost")
		
	def testRun(self):
		self.srv.Run()
		threads = threading.enumerate()
		tCurrent = threading.currentThread()
		for th in threads:
			if th != tCurrent:
				th.exit()
				th.join()
				
	def testAddClientHosts(self):
		clients = {
			'127.0.0.1': {'name' : 'name1', 'secret': 'secret1'},
			'127.0.0.2': {'name' : 'name2', 'secret': 'secret2'},
		}
		self.srv.addClientHosts(clients)
		self.failUnless(self.srv.hosts.keys().sort() == ['127.0.0.1', '127.0.0.2'].sort())
		for addr, attrs in clients.iteritems():
			self.failUnless(self.srv.hosts[addr].address == addr)
			self.failUnless(self.srv.hosts[addr].secret == attrs['secret'])
			self.failUnless(self.srv.hosts[addr].name == attrs['name'])


class BaseThreadTestCase(unittest.TestCase):
	"""Test BaseThread class"""
	def setUp(self):
		self.srv = BsdRadiusServer()
		self.th = BaseThread(self.srv)
	
	def tearDown(self):
		del self.srv
		del self.th
	
	def testExit(self):
		self.th.exit()
		self.failUnless(self.th.threadMayRun == False)	


def makeSuite():
	"""Collect test cases into suite"""
	loader = unittest.defaultTestLoader
	suites = [
		loader.loadTestsFromTestCase(BsdRadiusServerTestCase),
		loader.loadTestsFromTestCase(BaseThreadTestCase),
	]
	return unittest.TestSuite(suites)
