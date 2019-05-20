__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, mmap, struct, sqlite3
from collections import OrderedDict

from _rhtools.utils import *
from _rhtools.Table import Table

SNES_HEADER_SIZE = 0x200
SNES_BANK_SIZE = 0x8000

CRC32 = 'AC443D87'

TEXT_BLOCK1_START = 0x170000
TEXT_BLOCK1_END = 0x17fac9
TEXT_BLOCK1_LIMIT = 0x17ffff
TEXT_BLOCK2_START = 0x120000
TEXT_BLOCK2_END = 0x0
TEXT_BLOCK2_LIMIT = 0x0

POINTER_BLOCK1_START = 0x50013
POINTER_BLOCK1_END = 0x50267
POINTER_BLOCK2_START = 0x6046e
POINTER_BLOCK2_END = 0x60593

filename = 'brainlord/roms/Brain Lord (U) [!].smc'
#filename2 = 'brainlord/roms/Brain Lord (I) [!].smc'
tablename = 'brainlord/tables/Brain Lord (U) [!].tbl'
#tablename2 = 'brainlord/Brain Lord (I) [!].tbl'
db = 'brainlord/db/brainlord.db'
user_name = 'clomax'
dump_path = 'brainlord/dump/'

table = Table(tablename)
#table2 = Table(tablename2)

# CHECKSUM (CRC32)
if crc32(filename) != CRC32:
	sys.exit('ROM CHECKSUM: FAIL')
else:
	print 'ROM CHECKSUM: OK'

if True:
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	id = 1
	#DUMP (TXTs + SQLITE3)
	with open(filename, 'rb') as f:
		# POINTERS 1
		pointers = OrderedDict()
		blocks = OrderedDict()
		f.seek(POINTER_BLOCK1_START)
		while(f.tell() < POINTER_BLOCK1_END):
			paddress = f.tell()
			pvalue = f.read(2)
			bvalue = f.read(1)
			bvalue2 = (byte2int(bvalue) - 0xc0) * 0x10000
			pvalue2 = struct.unpack('H', pvalue)[0]
			pvalue3 = bvalue2 + pvalue2
			if pvalue3 not in pointers:
				pointers[pvalue3] = []
			pointers[pvalue3].append(paddress)
			if bvalue2 not in blocks:
				blocks[bvalue2] = []
			blocks[bvalue2].append(paddress)
			for block in blocks.keys():
				print int2hex(block)

		# TEXT 1
		for pointer in pointers:
			pointer_addresses = ''
			for pointer_address in pointers[pointer]:
				pointer_addresses += str(int2hex(pointer_address)) + ';'
			f.seek(pointer)
			text = b''
			byte = b'1'
			while not byte2int(byte) == table.getNewline():
				byte = f.read(1)
				text += byte
			text_encoded = table.encode2(text)	
			text_binary = sqlite3.Binary(text)
			text_address = int2hex(pointer)
			text_length = len(text_binary)
			cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?)', (id, buffer(text_binary), text_encoded, text_address, pointer_addresses, text_length))				
			# DUMP - TXT
			with open('%s - %s.txt' % (dump_path + str(id).zfill(3), pointer_addresses), 'w') as out:
				out.write(text_encoded)
				pass
			id += 1

	cur.close()
	conn.commit()
	conn.close()