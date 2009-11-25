#!/usr/bin/env python

"""
Run all unittests for bsdradius
"""

import unittest
import os


def listModules(path):
	"""List python files in directory
		Input: (string) directory path.
		Output: (list) directory contents.
	"""
	ret = []
	if not path:
		return ret
	for name in os.listdir(path):
		if not name.endswith(".py"):
			continue
		# exclude this script itself
		if name == "test_all.py":
			continue
		# exclude directories
		if os.path.isdir(name):
			continue
		ret.append(name[:-3])
	return ret


def main():
	for moduleName in listModules(os.getcwd()):
		print "--- Testing module: %s ---" % moduleName
		mod = __import__(moduleName)
		try:
			unittest.TextTestRunner(verbosity=2).run(mod.makeSuite())
		except AttributeError, e:
			print "ERROR:", e
			print "ERROR: All test modules must implement makeSuite() which returns unittest.TestSuite instance"


if __name__ == "__main__":
	main()
