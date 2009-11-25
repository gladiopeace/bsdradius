"""
This module handles static files.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/webstuff/tags/release20061229_v_1_0_0/webstuff/static.py $
# Author:		$Author: valdiic $
# File version:	$Revision: 258 $
# Last changes:	$Date: 2006-10-04 14:23:07 +0300 (Tr, 04 Okt 2006) $


import os, mimetypes
import framework as fw

def getFile(path = None):
	"""Get static file contents, set mime type and pass it to user.
		Input: (string) path
		Output: none
	"""
	if path == None:
		return
	filePath = os.path.join(fw.staticFileRoot, path)
	filePath = os.path.abspath(filePath)
	
	# guess mimetype and encoding
	typeTokens = mimetypes.guess_type(filePath)
	if typeTokens[0]:
		fw.web.header("Content-Type", typeTokens[0])
	else:
		fw.web.header("Content-Type", "text/plain")
	if typeTokens[1]:
		fw.web.header("Content-Encoding", typeTokens[1])
	
	# pass file contents to user
	try:
		fh = open(filePath, 'rb')
		fw.web.output(fh.read())
	except IOError:
		fw.web.notfoundError()
	except:
		fw.webError('Error opening file %s' % filePath)
