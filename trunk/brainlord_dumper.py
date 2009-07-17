__author__ = "Roberto Fontanarosa"
__license__ = "GPL"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys

try:
	from HexByteConversion import ByteToHex
	from HexByteConversion import HexToByte
except ImportError:
	sys.exit("missing HexByteConversion module!")

import os
from os import SEEK_SET, SEEK_CUR, SEEK_END
import mmap

from Table import Table

def dec2hex(n):
	"""return the hexadecimal string representation of integer n"""
	if not n:
		return None
	else:
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
TEXT_BLOCK_SIZE = (TEXT_BLOCK_END - TEXT_BLOCK_START) + 1
TEXT_BLOCK_MAX_SIZE = TEXT_BLOCK_LIMIT - TEXT_BLOCK_START

def extract(f, start=TEXT_BLOCK_START, end=TEXT_BLOCK_END):
	""" extract a block from a file creating a block """
	f.seek(start)
	return f.read(TEXT_BLOCK_SIZE)


def dump2txt(text_extracted, table=None, filename='dump.txt', separated_byte_format=True):
	"""  """
	out = open(filename, 'w')
	if table:
		for byte in text_extracted:
			if table.get(byte2int(byte)):
				if separated_byte_format and table.isDTE(byte2int(byte)):
					out.write('{%s}' % table.get(byte2int(byte)))
				else:
					out.write(table.get(byte2int(byte)))
			else:
				out.write('{%s}' % ByteToHex(byte))
	else:
		out.write(text_extracted)
	out.close()


def txt2dump(table=None, filename='dump.txt', separated_byte_format=True):
	"""  """
	
	dump = ""
	
	file = open(filename, 'rb+')
	f = mmap.mmap(file.fileno(), os.path.getsize(filename))
	if separated_byte_format:
		while True:
			byte = f.read(1)
			
			if not byte:
				break
				
			if byte == "{":
				while "}" not in byte:
					byte += f.read(1)
					
				if byte == "{END}":
					f.read(2)
					print table.table_newline
					
				else:
					print dec2hex(table.find(byte[1:len(byte)-1]))
					pass

			elif byte == "<":
				while ">" not in byte:
					byte += f.read(1)
				print dec2hex(table.find(byte))

			else:
				if byte == "\n":
					print table.table_breakline
				else:
					print dec2hex(table.find(byte))

	f.close()
	file.close()


tablepath = sys.argv[2]
table = Table(tablepath)

filepath = sys.argv[1]
file = open(filepath, "rb+")
size = os.path.getsize(filepath)
f = mmap.mmap(file.fileno(), size)
text_extracted = extract(f, TEXT_BLOCK_START, TEXT_BLOCK_END)
f.close()
file.close()

dump2txt(text_extracted, table=table, filename='dump.txt', separated_byte_format=True)
#txt2dump(table=table, filename='dump.txt', separated_byte_format=True)