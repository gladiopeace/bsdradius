# tools.py
#
# Utility functions

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_6/bsdradius/pyrad/tools.py $
# Author:		$Author: valts $
# File version:	$Revision: 85 $
# Last changes:	$Date: 2005-12-01 11:11:11 +0200 (Ce, 01 Dec 2005) $


import struct


def EncodeString(str):
	assert len(str)<=253

	return str


def EncodeAddress(addr):
	(a,b,c,d)=map(int, addr.split("."))
	return struct.pack("BBBB", a, b, c, d)


def EncodeInteger(num):
	return struct.pack("!I", num)


def EncodeDate(num):
	return struct.pack("!I", num)


def DecodeString(str):
	return str


def DecodeAddress(addr):
	return ".".join(map(str, struct.unpack("BBBB", addr)))


def DecodeInteger(num):
	return (struct.unpack("!I", num))[0]


def DecodeDate(num):
	return (struct.unpack("!I", num))[0]


def EncodeAttr(datatype, value):
	if datatype=="string":
		return EncodeString(value)
	elif datatype=="ipaddr":
		return EncodeAddress(value)
	elif datatype=="integer":
		return EncodeInteger(value)
	elif datatype=="date":
		return EncodeDate(value)
	else:
		return value
	

def DecodeAttr(datatype, value):
	if datatype=="string":
		return DecodeString(value)
	elif datatype=="ipaddr":
		return DecodeAddress(value)
	elif datatype=="integer":
		return DecodeInteger(value)
	elif datatype=="date":
		return DecodeDate(value)
	else:
		return value
