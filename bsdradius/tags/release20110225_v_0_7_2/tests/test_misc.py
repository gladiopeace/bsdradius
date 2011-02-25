"""
Test bsdradius/misc.py
"""

# HeadURL		$HeadURL: svn://svn.bsdradius.org/bsdradius/trunk/setup.py $
# Author:		$Author: valts $
# File version:	$Revision: 251 $
# Last changes:	$Date: 2006-06-30 14:44:02 +0300 (Fri, 30 Jun 2006) $


import unittest
import sys, os, os.path, exceptions
import pwd, grp
import types
sys.path.insert(0, '../')

import bsdradius.misc as misc
import bsdradius.pyrad.packet as packet
from bsdradius.pyrad.client import Client
from bsdradius.pyrad.dictionary import Dictionary


# use these paths for testing
tmpdir = os.path.abspath("./tmpdir")
tmpfile = os.path.join(tmpdir, "file.tmp")
# path to radius dictionary
dictFile = os.path.abspath("../dictionaries/dictionary")



class MiscExceptionsTestCase(unittest.TestCase):
	"""Tests exception handling """
	
	def testPrintException(self):
		try:
			raise Exception("Testing misc.printException")
		except:
			misc.printException()
	
	
	def testPrintExceptionError(self):
		try:
			raise Exception("Testing misc.printExceptionError")
		except:
			misc.printExceptionError()



class MiscCheckDirTestCase(unittest.TestCase):
	"""Test misc.checkDir"""
	def tearDown(self):
		"""Remove temporary dir"""
		os.rmdir(tmpdir)
	
	
	def testcheckDir(self):
		misc.checkDir(tmpdir)
		self.failUnless(os.path.exists(tmpdir))
		self.failUnless(os.path.isdir(tmpdir))



class MiscQuitTestCase(unittest.TestCase):
	"""Test misc.quit"""
	def testQuit(self):
		try:
			misc.quit()
		except SystemExit, e:
			pass
	
	def testKillSignalHandler(self):
		try:
			# this signal handler doesn't care about frame object
			misc.killSignalHandler(0, None)
		except SystemExit, e:
			pass



class MiscMakePidfileTestCase(unittest.TestCase):
	"""Test misc.makePidfile"""
	def setUp(self):
		os.mkdir(tmpdir)
		from bsdradius.Config import main_config
		main_config['PATHS']['pid_file'] = tmpfile
	
	
	def tearDown(self):
		os.remove(tmpfile)
		os.rmdir(tmpdir)
		
		
	def testMakePidfile(self):
		misc.makePidfile()
		fh = open(tmpfile)
		self.failUnless(os.getpid() == int(fh.read()))


	
class MiscSwitchUidTestCase(unittest.TestCase):
	"""Test misc.switchUid"""
	def testSwitchUid(self):
		misc.switchUid(
			user = pwd.getpwuid(os.getuid())[0],
			group = grp.getgrgid(os.getgid())[0]
		)


	
class MiscSetOwnerTestCase(unittest.TestCase):
	"""Test misc.setOwner"""
	def setUp(self):
		os.mkdir(tmpdir)
		open(tmpfile, 'w').close()
	
	def tearDown(self):
		os.remove(tmpfile)
		os.rmdir(tmpdir)
	
	def testSetOwner(self):
		misc.setOwner(
			path = tmpfile,
			user = pwd.getpwuid(os.getuid())[0],
			group = grp.getgrgid(os.getgid())[0]
		)



class MiscRewriteDictTestCase(unittest.TestCase):
	"""Test misc.rewriteDict"""	
	def testRewriteDict_1(self):
		input = {'one': 1, 'two': 2, 3: 'three'}
		output = {'23': 23, 'aljks0': None}
		misc.rewriteDict(input, output)
		self.failUnless(input == output)
	
	
	def testRewriteDict_2(self):
		input = {}
		output = {'23': 23, 'aljks0': None}
		misc.rewriteDict(input, output)
		self.failUnless(input == output)



class MiscCopyDictWithListValues(unittest.TestCase):
	"""Test misc.copyDictWithListValues"""
	def performTest(self, input):
		output = misc.copyDictWithListValues(input)
		print "INPUT:", input
		print "RESULT:", output
		for key, value in input.iteritems():
			if isinstance(value, types.ListType):
				self.failUnless(output[key] == value)
			else:
				self.failUnless(output[key] == [value])
	
	
	def testCopyDictWithListValues_1(self):
		self.performTest({'list1' : [1, 2, 5, 7], 'list2': ['sksk'], 'list3': 'not list'})
	
	
	def testCopyDictWithListValues_2(self):
		self.performTest({})
	
	
	def testCopyDictWithListValues_3(self):
		self.performTest({'kk' : 12, '22' : [], '' : [1, 2, 5]})



class MiscRadiusPacketTestCase(unittest.TestCase):
	"""Test misc.packetToStr, misc.authPacketToStr and acctPacketToStr"""
	def setUp(self):
		attributes = {
			'NAS-IP-Address' : ['127.0.0.1'],
			'User-Name' : ['testuser'],
			'User-Password' : ['testpassword'],
		}
		dict = Dictionary(dictFile)
		self.srv = Client(server = "127.0.0.1", dict = dict)
		self.auth_pkt = self.srv.CreateAuthPacket(code = packet.AccessRequest, **attributes)
		self.acct_pkt = self.srv.CreateAcctPacket(code = packet.AccountingRequest, **attributes)
	
	
	def testPacketToStr(self):
		output = misc.packetToStr(self.auth_pkt)
		self.failUnless(isinstance(output, types.StringTypes))
		self.failUnless(output != '')
	
	
	def testAuthPacketToStr(self):
		output = misc.authPacketToStr(self.auth_pkt)
		self.failUnless(isinstance(output, types.StringTypes))
		self.failUnless(output != '')
	
	
	def testAcctPacketToStr(self):
		output = misc.acctPacketToStr(self.acct_pkt)
		self.failUnless(isinstance(output, types.StringTypes))
		self.failUnless(output != '')


class MiscDatetimeTestCase(unittest.TestCase):
	"""Test misc.parseDatetime"""
	def testParseDatetime1(self):
		"""Test ISO datetime parsing"""
		input = "2006-03-02 12:04:59"
		right = "2006-03-02 12:04:59"
		self.failUnless(str(misc.parseDatetime(input)) == right)
		
	def testParseDatetime2(self):
		"""Test ISO datetime parsing"""
		input = "2006-03-02 12:04:59.123"
		right = "2006-03-02 12:04:59.123000"
		self.failUnless(str(misc.parseDatetime(input)) == right)
		
	def testParseDatetime3(self):
		"""Test ISO datetime parsing"""
		input = "2006-03-02 12:04:59.123456"
		right = "2006-03-02 12:04:59.123456"
		self.failUnless(str(misc.parseDatetime(input)) == right)
		
	def testParseDatetime4(self):
		"""Test CISCO datetime parsing"""
		input = "12:04:59 UTC Mon Mar 2 2006"
		right = "2006-03-02 12:04:59"
		self.failUnless(str(misc.parseDatetime(input)) == right)
		
	def testParseDatetime5(self):
		"""Test CISCO datetime parsing"""
		input = "*12:04:59.012 Western Pacific Mon Mar 2 2006"
		right = "2006-03-02 12:04:59.012000"
		self.failUnless(str(misc.parseDatetime(input)) == right)
		
	def testParseDatetime6(self):
		"""Test CISCO datetime parsing"""
		input = "+12:04:59.002345 Western Pacific Mon Mar 2 2006"
		right = "2006-03-02 12:04:59.002345"
		self.failUnless(str(misc.parseDatetime(input)) == right)
	



def makeSuite():
	"""Collect test cases into suite
	"""
	loader = unittest.defaultTestLoader
	suites = [
		loader.loadTestsFromTestCase(MiscExceptionsTestCase),
		loader.loadTestsFromTestCase(MiscCheckDirTestCase),
		loader.loadTestsFromTestCase(MiscQuitTestCase),
		loader.loadTestsFromTestCase(MiscMakePidfileTestCase),
		loader.loadTestsFromTestCase(MiscSwitchUidTestCase),
		loader.loadTestsFromTestCase(MiscSetOwnerTestCase),
		loader.loadTestsFromTestCase(MiscRewriteDictTestCase),
		loader.loadTestsFromTestCase(MiscCopyDictWithListValues),
		loader.loadTestsFromTestCase(MiscRadiusPacketTestCase),
		loader.loadTestsFromTestCase(MiscDatetimeTestCase),
	]
	return unittest.TestSuite(suites)


if __name__ == "__main__":
	unittest.TextTestRunner(verbosity=2).run(makeSuite())
