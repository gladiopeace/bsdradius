#!/usr/bin/env python
"""
Webstuff installation script
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/webstuff/trunk/setup.py $
# Author:		$Author: valts $
# File version:	$Revision: 53 $
# Last changes:	$Date: 2006-06-29 13:00:54 +0300 (Ce, 29 Jūn 2006) $

import os, sys, os.path
import re
from distutils.core import setup


def listdir(path):
	"""List directory without .svn in results and put
		path as prefix for each result
		Input: (string) directory path.
		Output: (list) directory contents.
	"""
	ret = []
	if not path:
		return ret

	for name in os.listdir(path):
		# exclude svn directories
		if name == '.svn':
			continue
		name = '%s/%s' % (path, name)
		# exclude directories
		if os.path.isdir(name):
			continue
		ret.append(name)

	return ret


### MAIN ###

# Prepare setup data
shareDir = 'share/webstuff'
dataFiles = [
	('%s/doc' % shareDir, listdir('doc')),
	('%s/examples' % shareDir, listdir('examples')),
	('%s/examples/modules' % shareDir, listdir('examples/modules')),
	('%s/examples/static' % shareDir, listdir('examples/static')),
	('%s/examples/static/style' % shareDir, listdir('examples/static/style')),
	('%s/examples/templates' % shareDir, listdir('examples/templates')),
	('%s/examples/templates/base' % shareDir, listdir('examples/templates/base')),
	('%s/examples/templates/langfiles' % shareDir, listdir('examples/templates/langfiles')),
]

# call setup
dist = setup(
	name = 'webstuff',
	version = '0.1.0',
	author = 'Data Tech Labs',
	author_email = 'info@datatechlabs.com',
#	maintainer = 'Valts Mazurs',
#	maintainer_email = 'valts@datatechlabs.com',
	url = 'http://www.datatechlabs.com',
	description = "Web programmer's library and framework",
	packages = ['webstuff', 'webstuff.server'],
	data_files = dataFiles
)
