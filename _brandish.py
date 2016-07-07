__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, mmap, struct, sqlite3
from collections import OrderedDict

from _rhtools.utils import *
from _rhtools.Table2 import Table

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--crc32check', action='store_true', default=False, help='Execute CRC32CHECK')
parser.add_argument('--dump', action='store_true', default=False, help='Execute DUMP')
parser.add_argument('--insert', action='store_true', default=False, help='Execute INSERTER')
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
filename = args.source_file
filename2 = args.dest_file
tablename = args.table1
tablename2 = args.table2
db = args.database_file
user_name = args.user
dump_path = 'brandish/dump/'

SNES_HEADER_SIZE = 0x200
SNES_BANK_SIZE = 0x8000

CRC32 = '74F70A0B'

TEXT_BLOCK_START = 0x50fbe
TEXT_BLOCK_END = 0x594ef
TEXT_BLOCK_LIMIT = 0x594ef
TEXT_BLOCK_SIZE = TEXT_BLOCK_END - TEXT_BLOCK_START
TEXT_BLOCK_MAX_SIZE = TEXT_BLOCK_LIMIT - TEXT_BLOCK_START

POINTER_BLOCK_START = 0x50d2a
POINTER_BLOCK_END = 0x50fbd

table = Table(tablename)
table2 = Table(tablename2)

if execute_crc32check:
	""" CHECKSUM (CRC32) """
	if crc32(filename) != CRC32:
		sys.exit('ROM CHECKSUM: FAIL')
	else:
		print 'ROM CHECKSUM: OK'

if execute_dump:
	""" DUMP """
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	with open(filename, 'rb') as f:
		id = 1
		f.seek(POINTER_BLOCK_START)
		while(f.tell() < POINTER_BLOCK_END):
			curr_pointer_address = f.tell()
			curr_pointer_value = struct.unpack('H', f.read(2))[0] + (SNES_BANK_SIZE * 0xa)
			next_pointer_address = f.tell()
			if (next_pointer_address < POINTER_BLOCK_END):
				next_pointer_value = struct.unpack('H', f.read(2))[0] + (SNES_BANK_SIZE * 0xa)
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
				text_encoded = table.encode(text, False, False)
				text_binary = sqlite3.Binary(text)
				text_address = int2hex(curr_pointer_value)
				text_length = len(text_binary)
				pointer_address = int2hex(int(curr_pointer_address))
				cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, 1)', (id, buffer(text_binary), text_encoded, text_address, pointer_address, text_length))
				# DUMP - TXT
				with open('%s - %s.txt' % (dump_path + str(id).zfill(3), pointer_address), 'w') as out:
					out.write(text_encoded)
					pass
				id += 1
	cur.close()
	conn.commit()
	conn.close()

if execute_inserter:
	""" REPOINTER """
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	with open(filename2, 'r+b') as f:
		address = TEXT_BLOCK_START
		f.seek(POINTER_BLOCK_START)
		cur.execute("SELECT text, text_encoded, new_text2, id FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s') AS t2 ON t1.id=t2.id_text WHERE t1.block = 1" % user_name)
		for row in cur:
			original_text = row[1]
			new_text = row[2]
			if (new_text):
				text = new_text
				decoded_text = table2.decode(text, False, False)
			else:
				text = original_text
				decoded_text = table.decode(text, False, False)
			pvalue = struct.pack('H', address - (SNES_BANK_SIZE * 0xa)) 
			f.write(pvalue) # address to write
			address += len(decoded_text) # next address to write
	cur.close()
	conn.close()

if execute_inserter:
	""" INSERTER """
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	with open(filename2, 'r+b') as f:
		f.seek(TEXT_BLOCK_START)
		cur.execute("SELECT text, text_encoded, new_text2, id FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s') AS t2 ON t1.id=t2.id_text WHERE t1.block = 1" % user_name)
		for row in cur:
			original_text = row[1]
			new_text = row[2]
			if (new_text):
				text = new_text
				decoded_text = table2.decode(text, False, False)
			else:
				text = original_text
				decoded_text = table.decode(text, False, False)
			f.write(decoded_text)
			if f.tell() > TEXT_BLOCK_LIMIT:
				sys.exit('CRITICAL ERROR! TEXT_BLOCK_LIMIT! %s > %s (%s)' % (f.tell(), TEXT_BLOCK_LIMIT, (TEXT_BLOCK_LIMIT - f.tell())))
		for i in range(0, TEXT_BLOCK_LIMIT - f.tell()):
			f.write('0')
	cur.close()
	conn.close()