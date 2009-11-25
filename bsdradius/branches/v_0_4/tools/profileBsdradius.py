#!/usr/local/bin/python

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
Run BSD Radius server and print profiler info
"""

import pstats
import threading
import sys, traceback, os
from collections import deque
import time
import re

try:
	from resource import getrusage, RUSAGE_SELF
except ImportError:
	RUSAGE_SELF = 0
	def getrusage(who=0):
		return [0.0, 0.0] # on non-UNIX platforms cpu_time always 0.0

p_stats = None
p_start_time = None

def profiler(frame, event, arg):
    if event not in ('call','return'): return profiler
    #### gather stats ####
    rusage = getrusage(RUSAGE_SELF)
    t_cpu = rusage[0] + rusage[1] # user time + system time
    code = frame.f_code 
    fun = (code.co_name, code.co_filename, code.co_firstlineno)
    #### get stack with functions entry stats ####
    ct = threading.currentThread()
    try:
        p_stack = ct.p_stack
    except AttributeError:
        ct.p_stack = deque()
        p_stack = ct.p_stack
    #### handle call and return ####
    if event == 'call':
        p_stack.append((time.time(), t_cpu, fun))
    elif event == 'return':
        try:
            t,t_cpu_prev,f = p_stack.pop()
            assert f == fun
        except IndexError: # TODO investigate
            t,t_cpu_prev,f = p_start_time, 0.0, None
        call_cnt, t_sum, t_cpu_sum = p_stats.get(fun, (0, 0.0, 0.0))
        p_stats[fun] = (call_cnt+1, t_sum+time.time()-t, t_cpu_sum+t_cpu-t_cpu_prev)
    return profiler


def profile_on():
    global p_stats, p_start_time
    p_stats = {}
    p_start_time = time.time()
    threading.setprofile(profiler)
    sys.setprofile(profiler)


def profile_off():
    threading.setprofile(None)
    sys.setprofile(None)

def get_profile_stats():
    """
    returns dict[function_tuple] -> stats_tuple
    where
      function_tuple = (function_name, filename, lineno)
      stats_tuple = (call_cnt, real_time, cpu_time)
    """
    return p_stats



def compareStatsList(x, y, reverse = False):
	tokenId = 6
	ret = 0
	if x[tokenId] < y[tokenId]:
		ret = -1
	elif x[tokenId] == y [tokenId]:
		ret = 0
	elif x[tokenId] > y[tokenId]:
		ret = 1
	if reverse:
		ret = ret * -1
	return ret



if __name__ == '__main__':
	sys.path.insert(0, '../bsdradius')
	import bsdradiusd
	import misc
	
	profile_on()
	try:
		print "running bsdradiusd"
		bsdradiusd.main()
	except:
		print "exception"
#		profile_off()
		# prepare exception info
		exc_type = sys.exc_info()[0]
		exc_value = sys.exc_info()[1]
		extractedTb = traceback.extract_tb(sys.exc_info()[2])
	
		# print exception info
		print
		print '---[ ERROR: rlm_python ]---'
		print "Traceback (most recent call last):"
		# print all traceback stack items
		for tracebackItem in extractedTb:
			print "  File ", tracebackItem[0], ", line ", tracebackItem[1], ", in ", tracebackItem[2], "()"
			print "    ", tracebackItem[3]
		print "  ", str(exc_type), ": ", str(exc_value)
		print '---'
		print
	else:
		print "finished"
		
	from pprint import pprint
	unsortedStats = get_profile_stats()
	
	# concat all stats into one list
	stats = [stat + funct for funct, stat in unsortedStats.items()]
	# add total time per call and cpu time per call
	tmp = []
	for tokens in stats:
		totalPerCall = tokens[1] / tokens[0]
		cpuPerCall = tokens[2] / tokens[0]
		tmp.append(tokens + (totalPerCall, cpuPerCall))
	stats = tmp
	# sort results
	stats.sort(cmp=compareStatsList)

	minCalls = 100
	print 'Number of items:', len(unsortedStats)
	print "ncalls\tall time\tcputime\t\tall percall\tcpu percall\tfunction\t\tfile : line"
	print "-" * 102
	pythonLibPath = re.compile('/usr/local/lib/python2.4')
	for tokens in stats:
		# don't print any info if number of calls is too low
		if tokens[0] < minCalls:
			continue
		n = abs(len(tokens[3]) / 8) + 1
		delimiter = '\t' * (4 - n)
		totalPerCall = tokens[6]
		cpuPerCall = tokens[7]
		filePath = pythonLibPath.sub('pylib', tokens[4])
		print "%s\t%f\t%f\t%f\t%f\t%s%s%s : %s" % (tokens[0], tokens[1], tokens[2], totalPerCall, cpuPerCall, tokens[3], delimiter, filePath, tokens[5])
