__author__ = "Roberto Fontanarosa"
__license__ = "GPL"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys
import os
import mmap

try:
	from HexByteConversion import ByteToHex
	from HexByteConversion import HexToByte
except ImportError:
	sys.exit('Missing HexByteConversion module!')

try:
	from Table import Table
	from Dump import Dump
	from utils import *
except ImportError:
	sys.exit('Missing BrainlordTools module!')

CRC32 = 'AC443D87'
	
TEXT_BLOCK_START = 0x170000
TEXT_BLOCK_END = 0x17fac9
TEXT_BLOCK_LIMIT = 0x17ffff
TEXT_BLOCK_SIZE = TEXT_BLOCK_END - TEXT_BLOCK_START
TEXT_BLOCK_MAX_SIZE = TEXT_BLOCK_LIMIT - TEXT_BLOCK_START

TEXT_POINTER_BLOCK_START = 0x50010
TEXT_POINTER_BLOCK_END = 0x55567

"""
TEXT_BLOCK2_START = 0x66618
TEXT_BLOCK2_END = 0x67100

TEXT_POINTER1_BLOCK_START = 0xf9e
TEXT_POINTER1_BLOCK_END = 0xfef

## there are 20 (?) pointers in this block and every pointer starts with 0x01
#FAERIES_POINTER_START_BYTE = 0x01
FAERIES_POINTER_BLOCK_START = 0x18ea0
FAERIES_POINTER_BLOCK_END = 0x18f9b

SHOP_POINTER_BLOCK_START = 0x23000
SHOP_POINTER_BLOCK_END = 0x25000
"""

filename = 'roms/Brain Lord (U) [!].smc'
filename2 = 'roms/Brain Lord (U) [!] - Copy.smc'
tablename = 'tbls/Brain Lord (U) [!].tbl'
dumpname_txt = 'dump/brainlord_dump.txt'
dumpname_xml = 'dump/brainlord_dump.xml'
db = '/Program Files/Apache Software Foundation/Apache2.2/htdocs/brainlord/db/brainlord.db'

table = Table(tablename)

# CHECKSUM (CRC32)
if crc32(filename) != CRC32:
	sys.exit('CHECKSUM: FAIL')
else:
	print 'CHECKSUM: OK'
	
#DUMP (SQLITE3)
import sqlite3
conn = sqlite3.connect(db)
conn.text_factory = str
cur = conn.cursor()
with open(filename, "rb") as f:
	id = 1
	f.seek(TEXT_POINTER_BLOCK_START)
	while(f.tell() < TEXT_POINTER_BLOCK_END):
		curr_pointer_address = f.tell()
		curr_pointer_value = string_address2int_address(f.read(2), switch=True, offset=327680)
		next_pointer_address = f.tell()
		if (next_pointer_address < TEXT_POINTER_BLOCK_END):
			next_pointer_value = string_address2int_address(f.read(2), switch=True, offset=327680)
			f.seek(f.tell() - 2)
		else:
			next_pointer_value = None
		with open(filename, 'rb') as f2:
			f2.seek(curr_pointer_value)
			if (next_pointer_value):
				size = next_pointer_value - curr_pointer_value
			else:
				size = TEXT_BLOCK_LIMIT - f2.tell()
			text = f2.read(size)
			text_bynary = sqlite3.Binary(text)
			text_encoded = table.encode(text, separated_byte_format=True)
			#text_encoded_binary = sqlite3.Binary(text_encoded)
			text_address = int2hex(curr_pointer_value)
			pointer_address = int2hex(int(curr_pointer_address))
			cur.execute("insert or replace into texts values (?, ?, ?, ?, ?, ?)", (id, buffer(text_bynary), buffer(text_encoded), text_address, pointer_address, size))
			id += 1
cur.close()
conn.commit()
conn.close()