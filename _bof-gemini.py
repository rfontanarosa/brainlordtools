__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3

from _rhtools.utils import hex2dec
from _rhtools.Table2 import Table

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--insert', action='store_true', default=False, help='Execute INSERTER')
parser.add_argument('-d', '--dest',  action='store', dest='dest_file', required=True, help='Destination filename')
parser.add_argument('-t2', '--table2', action='store', dest='table2', required=True, help='Modified table filename')
parser.add_argument('-db', '--database',  action='store', dest='database_file', required=True, help='DB filename')
parser.add_argument('-u', '--user', action='store', dest='user', required=True, help='')
args = parser.parse_args()

execute_inserter = args.insert
filename2 = args.dest_file
tablename2 = args.table2
db = args.database_file
user_name = args.user

SNES_HEADER_SIZE = 0x200
SNES_BANK_SIZE = 0x8000

DICT1_POINTER_BLOCK_START = 0x180000
DICT1_POINTER_BLOCK_END = DICT1_POINTER_BLOCK_LIMIT = 0x1801ff
DICT1_BLOCK_START = 0x180200
DICT1_BLOCK_END = DICT1_BLOCK_LIMIT = 0x180fff

POINTER_BLOCK1_START = 0x188000
POINTER_BLOCK1_END = POINTER_BLOCK1_LIMIT =  0x0
POINTER_BLOCK2_START = 0x0
POINTER_BLOCK2_END = POINTER_BLOCK2_LIMIT = 0x188dff

POINTER_BLOCK_DISTANCE = 0x188000 - 0x77000

TEXT_BLOCK1_START = 0x190000
TEXT_BLOCK1_END = TEXT_BLOCK1_LIMIT = 0x19ffff
TEXT_BLOCK2_START = 0x1a0000
TEXT_BLOCK2_END = TEXT_BLOCK2_LIMIT = 0x1affff

def bofBlockLimitsResolver(block):
	""" """
	blockLimits = (0, 0)
	if block == 1:
		blockLimits = (TEXT_BLOCK1_START, TEXT_BLOCK1_LIMIT, POINTER_BLOCK1_START, POINTER_BLOCK1_END, POINTER_BLOCK1_LIMIT)
	if block == 2:
		blockLimits = (TEXT_BLOCK2_START, TEXT_BLOCK2_LIMIT, POINTER_BLOCK2_START, POINTER_BLOCK2_END, POINTER_BLOCK2_LIMIT)
	return blockLimits

if execute_inserter:
	""" INSERTER """
	table2 = Table(tablename2)
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	with open(filename2, 'r+b') as f:
		# BLOCK 1
		block = 1
		blockLimits = bofBlockLimitsResolver(block)
		TEXT_BLOCK_START = blockLimits[0]
		TEXT_BLOCK_LIMIT = blockLimits[1]
		#POINTER_BLOCK_START = blockLimits[2]
		#POINTER_BLOCK_END = blockLimits[3]
		#POINTER_BLOCK_LIMIT = blockLimits[4]
		POINTER_BLOCK_LIMIT = POINTER_BLOCK2_LIMIT
		f.seek(TEXT_BLOCK_START)
		cur.execute("SELECT text, new_text, text_encoded, id, new_text2, address, pointer_address, size FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text WHERE t1.block = %d" % (user_name, block))
		for row in cur:
			# INSERTER 1
			id = row[3]
			if id not in (207, 444):
				original_text = row[2]
				new_text = row[4]
				text = new_text if new_text else original_text
				decoded_text = table2.decode(text)
				new_text_address = f.tell()
				if new_text_address + len(decoded_text) > (TEXT_BLOCK_LIMIT + 1):
					sys.exit('CRITICAL ERROR! ID %d - BLOCK %d - TEXT_BLOCK_LIMIT! %s > %s (%s)' % (id, block, next_text_address + len(decoded_text), TEXT_BLOCK_LIMIT, (TEXT_BLOCK_LIMIT - next_text_address - len(decoded_text))))
				f.seek(new_text_address)
				f.write(decoded_text)
				next_text_address = f.tell()
				# REPOINTER 1
				pointer_addresses = row[6]
				if pointer_addresses:
					for pointer_address in pointer_addresses.split(';'):
						if pointer_address:
							pointer_address = hex2dec(pointer_address) + POINTER_BLOCK_DISTANCE
							f.seek(pointer_address)
							pvalue = struct.pack('H', new_text_address - TEXT_BLOCK_START)
							f.write(pvalue)
				f.seek(next_text_address)
		# BLOCK 2
		block = 2
		blockLimits = bofBlockLimitsResolver(block)
		TEXT_BLOCK_START = blockLimits[0]
		TEXT_BLOCK_LIMIT = blockLimits[1]
		#POINTER_BLOCK_START = blockLimits[2]
		#POINTER_BLOCK_END = blockLimits[3]
		POINTER_BLOCK_LIMIT = blockLimits[4]
		f.seek(TEXT_BLOCK_START)
		cur.execute("SELECT text, new_text, text_encoded, id, new_text2, address, pointer_address, size FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text WHERE t1.block = %d" % (user_name, block))
		for row in cur:
			# INSERTER 2
			id = row[3]
			if id not in (207, 444):
				original_text = row[2]
				new_text = row[4]
				text = new_text if new_text else original_text
				decoded_text = table2.decode(text)
				new_text_address = f.tell()
				if new_text_address + len(decoded_text) > (TEXT_BLOCK_LIMIT + 1):
					sys.exit('CRITICAL ERROR! ID %d - BLOCK %d - TEXT_BLOCK_LIMIT! %s > %s (%s)' % (id, block, next_text_address + len(decoded_text), TEXT_BLOCK_LIMIT, (TEXT_BLOCK_LIMIT - next_text_address - len(decoded_text))))
				f.seek(new_text_address)
				f.write(decoded_text)
				next_text_address = f.tell()
				# REPOINTER 2
				pointer_addresses = row[6]
				if pointer_addresses:
					for pointer_address in pointer_addresses.split(';'):
						if pointer_address:
							pointer_address = hex2dec(pointer_address) + POINTER_BLOCK_DISTANCE
							f.seek(pointer_address)
							pvalue = struct.pack('H', new_text_address - TEXT_BLOCK_START)
							f.write(pvalue)
							if pointer_address > (POINTER_BLOCK_LIMIT + 1):
								sys.exit('CRITICAL ERROR! ID %d - BLOCK %d - POINTER_BLOCK_LIMIT! %s > %s (%s)' % (id, block, pointer_address, POINTER_BLOCK_LIMIT, (POINTER_BLOCK_LIMIT - pointer_address)))
				f.seek(next_text_address)
	cur.close()
	conn.close()
