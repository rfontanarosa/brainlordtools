__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3
from collections import OrderedDict

from _rhtools.utils import *
from _rhtools.Table2 import Table

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--crc32check', action='store_true', default=False, help='Execute CRC32CHECK')
parser.add_argument('--dump', action='store_true', default=False, help='Execute DUMP')
parser.add_argument('--insert', action='store_true', default=False, help='Execute INSERTER')
parser.add_argument('--mte_finder', action='store_true', default=False, help='Find MTE')
parser.add_argument('--mte_optimizer', action='store_true', default=False, help='Optimize MTE')
parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
parser.add_argument('-d', '--dest',  action='store', dest='dest_file', required=True, help='Destination filename')
parser.add_argument('-t1', '--table1', action='store', dest='table1', required=True, help='Original table filename')
parser.add_argument('-t2', '--table2', action='store', dest='table2', required=True, help='Modified table filename')
parser.add_argument('-db', '--database',  action='store', dest='database_file', required=True, help='DB filename')
parser.add_argument('-u', '--user', action='store', dest='user', required=True, help='')
args = parser.parse_args()

execute_crc32check = args.crc32check
execute_dump = args.dump
execute_inserter = args.insert
execute_mtefinder = args.mte_finder
execute_mteoptimizer = args.mte_optimizer
filename = args.source_file
filename2 = args.dest_file
tablename = args.table1
tablename2 = args.table2
db = args.database_file
user_name = args.user
dump_path = 'neugier/dump/'

SNES_HEADER_SIZE = 0x200
SNES_BANK_SIZE = 0x8000

#CRC32_ORIGINAL = '7F0DDCCF'
CRC32 = '5497DF2A'

POINTER_BLOCK1_START = 0x11010
POINTER_BLOCK1_END = POINTER_BLOCK1_LIMIT = 0x112ac

TEXT_BLOCK1_START = 0x100000
TEXT_BLOCK1_END = TEXT_BLOCK1_LIMIT = 0x1fffff

table = Table(tablename)
table2 = Table(tablename2)

if execute_crc32check:
	""" CHECKSUM (CRC32) """
	if crc32(filename) != CRC32:
		sys.exit('ROM CHECKSUM: FAIL')
	else:
		print('ROM CHECKSUM: OK')

if execute_dump:
	""" DUMP """
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	id = 1
	with open(filename, 'rb') as f:
		# TEXT POINTERS 1
		pointers = OrderedDict()
		f.seek(POINTER_BLOCK1_START)
		while(f.tell() < POINTER_BLOCK1_END):
			paddress = f.tell()
			pValue1 = f.read(1)
			pValue2 = f.read(2)
			pValue2 = struct.unpack('H', pValue2)[0] - 0x8000 + TEXT_BLOCK1_START
			if pValue2 not in pointers:
				pointers[pValue2] = []
			pointers[pValue2].append(paddress)
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
			text_encoded = table.encode(text)
			# DUMP - DB
			text_binary = sqlite3.Binary(text)
			text_address = int2hex(pointer)
			text_length = len(text_binary)
			cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, ?)', (id, buffer(text_binary), text_encoded, text_address, pointer_addresses, text_length, 1))
			# DUMP - TXT
			with open('%s - %d.txt' % (dump_path + str(id).zfill(4), len(pointers[pointer])), 'w') as out:
				out.write(text_encoded)
				pass
			id += 1
		cur.close()
		conn.commit()
		conn.close()

if execute_inserter:
	""" INSERTER + REPOINTER """
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	with open(filename2, 'r+b') as f:
		# TEXT
		f.seek(TEXT_BLOCK1_START)
		cur.execute("SELECT text, new_text, text_encoded, id, new_text2, address, pointer_address, size FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text WHERE t1.block = %d" % (user_name, 1))
		pValue1 = int2byte(0x20)
		for row in cur:
			# INSERTER X
			id = row[3]
			original_text = row[2]
			new_text = row[4]
			if (new_text):
				text = new_text
			else:
				text = original_text
			decoded_text = table2.decode(text)
			new_text_address = f.tell()
			if new_text_address + len(decoded_text) > (TEXT_BLOCK1_LIMIT + 1):
				sys.exit('CRITICAL ERROR! ID %d - BLOCK %d - TEXT_BLOCK_LIMIT! %s > %s (%s)' % (id, 1, next_text_address + len(decoded_text), TEXT_BLOCK1_LIMIT, (TEXT_BLOCK1_LIMIT - next_text_address - len(decoded_text))))
			if new_text_address + 0x8000 - TEXT_BLOCK1_START + len(decoded_text) > 0xffff and byte2int(pValue1) == 0x20:
				pValue1 = int2byte(0x21)
				new_text_address = TEXT_BLOCK1_START + 0x8000
			f.seek(new_text_address)
			f.write(decoded_text)
			next_text_address = f.tell()
			# REPOINTER X
			pointer_addresses = row[6]
			if pointer_addresses:
				for pointer_address in pointer_addresses.split(';'):
					if pointer_address:
						pointer_address = hex2dec(pointer_address)
						f.seek(pointer_address)
						if new_text_address >= TEXT_BLOCK1_START + 0x8000:
							pValue2 = struct.pack('H', new_text_address - TEXT_BLOCK1_START)
						else:
							pValue2 = struct.pack('H', new_text_address + 0x8000 - TEXT_BLOCK1_START)
						f.write(pValue1 + pValue2)
						if pointer_address > (POINTER_BLOCK1_LIMIT + 1):
							sys.exit('CRITICAL ERROR! ID %d - BLOCK %d - POINTER_BLOCK_LIMIT! %s > %s (%s)' % (id, 1, pointer_address, POINTER_BLOCK1_LIMIT, (POINTER_BLOCK1_LIMIT - pointer_address)))
			f.seek(next_text_address)
	cur.close()
	conn.close()
