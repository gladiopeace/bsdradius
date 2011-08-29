# bidict.py
#
# Bidirectional map

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_6/bsdradius/pyrad/bidict.py $
# Author:		$Author: valts $
# File version:	$Revision: 85 $
# Last changes:	$Date: 2005-12-01 11:11:11 +0200 (Ce, 01 Dec 2005) $


class BiDict:
	def __init__(self):
		self.forward={}
		self.backward={}
	

	def Add(self, one, two):
		self.forward[one]=two
		self.backward[two]=one


	def __len__(self):
		return len(self.forward)


	def __getitem__(self, key):
		return self.GetForward(key)


	def __delitem__(self, key):
		if self.forward.has_key(key):
			del self.backward[self.forward[key]]
			del self.forward[key]
		else:
			del self.forward[self.backward[key]]
			del self.backward[key]

	def __str__(self):
		return str(self.forward)
		

	def GetForward(self, key):
		return self.forward[key]


	def HasForward(self, key):
		return self.forward.has_key(key)


	def GetBackward(self, key):
		return self.backward[key]


	def HasBackward(self, key):
		return self.backward.has_key(key)
