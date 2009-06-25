"""
brainlord_dumper
last version:
changes:
author: roberto fontanarosa (robertofontanarosa@hotmail.com)
"""

import mmap
import os
from os import SEEK_SET, SEEK_CUR, SEEK_END
import pdb


from HexByteConversion import ByteToHex
from HexByteConversion import HexToByte

from brainlord_table import table, table_dte, table_newline, table_breakline, getKey

def dec2hex(n):
	"""return the hexadecimal string representation of integer n"""
	return "%x" % n
	
def hex2dec(s):
	"""return the integer value of a hexadecimal string s"""
	return int(s, 16) 

def byte2int(b):
	"""  """
	return ord(b)
		
	
TEXT_BLOCK_START = 0x170000
TEXT_BLOCK_END = 0x17fac9
TEXT_BLOCK_LIMIT = 0x17ffff

TEXT_BLOCK_SIZE = TEXT_BLOCK_END - TEXT_BLOCK_START
TEXT_BLOCK_MAX_SIZE = TEXT_BLOCK_LIMIT - TEXT_BLOCK_START

def extract(f, start, end):
	""" extract the entire text block using the default settings for brainlord """
	f.seek(start)
	return f.read(end - start)


def dump2txt(text_extracted, table=None, filename='dump.txt', separated_byte_format=True):
	"""  """
	out = open(filename, 'w')
	if table:
		for byte in text_extracted:
			if table.get(byte2int(byte)):
				if separated_byte_format and byte2int(byte) in table_dte:
					out.write('{%s}' % table.get(byte2int(byte)))
				else:
					out.write(table.get(byte2int(byte)))
			else:
				out.write('{%s}' % ByteToHex(byte))
	else:
		out.write(text_extracted)
	out.close()
	return True
	
def txt2dump(table=None, filename='dump.txt', separated_byte_format=True):
	"""  """
	
	file = open(filename, 'rb+')
	f = mmap.mmap(file.fileno(), os.path.getsize(filename))

	if separated_byte_format:
		while True:
			byte = f.read(1)
			if not byte:
				break
			if byte == '{':
				byte = ''
				while True:
					byte += f.read(1)
					if '}' in byte:
						break
				print getKey(table, byte[0:len(byte)-1])
				
	file.close()
	f.close()

	
def value2key(dict, value):
	"""  """
	key = None
	for item in dict.iteritems():
		if value == item[1]:
			key = item[0]
	return key
			

file = open("Brain Lord (U) [!].smc", "rb+")
size = os.path.getsize("Brain Lord (U) [!].smc")
f = mmap.mmap(file.fileno(), size)
file.close()
text_extracted = extract(f, TEXT_BLOCK_START, TEXT_BLOCK_END)
f.close()


dump2txt(text_extracted, table=table, filename='dump.txt', separated_byte_format=True)
txt2dump(table=table, filename='dump.txt', separated_byte_format=True)