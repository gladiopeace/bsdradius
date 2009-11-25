"""
Module which contains class for operating with
global thread safe dictionaries.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/webstuff/tags/release20061229_v_1_0_0/webstuff/ThreadStore.py $
# Author:		$Author: valts $
# File version:	$Revision: 42 $
# Last changes:	$Date: 2006-05-29 12:57:30 +0300 (Pr, 29 Mai 2006) $


import thread

class ThreadStore:
	"""Thread specific dictionary."""

	def __init__(self):
		self.dict = {}
		self.lock = thread.allocate_lock()

	def __setitem__(self, index, item):
		thread_id = thread.get_ident()

		self.lock.acquire()
		self.dict[thread_id][index] = item
		self.lock.release()

	def __getitem__(self, index):
		thread_id = thread.get_ident()

		self.lock.acquire()
		item = self.dict[thread_id][index]
		self.lock.release()

		return item

	def __delitem__(self, index):
		thread_id = thread.get_ident()

		self.lock.acquire()
		del self.dict[thread_id][index]
		self.lock.release()
		
	def __str__(self):
		thread_id = thread.get_ident()
		ret = ''
		
		self.lock.acquire()
		for key, value in self.dict[thread_id].iteritems():
			ret += '%s: %s\n' % (key, value)
		self.lock.release()
		return ret
		
	def __repr__(self):
		thread_id = thread.get_ident()
		
		self.lock.acquire()
		return repr(self.dict[thread_id])
		self.lock.release()
		
	def get(self, index, default = None):
		thread_id = thread.get_ident()
		
		self.lock.acquire()
		item = self.dict[thread_id].get(index, default)
		self.lock.release()
		
		return item

	def add_thread(self):
		thread_id = thread.get_ident()
		
		self.lock.acquire()
		self.dict[thread_id] = {}
		self.lock.release()

	def remove_thread(self):
		thread_id = thread.get_ident()

		self.lock.acquire()
		try:
			del self.dict[thread_id]
		except:
			pass
		self.lock.release()
