__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3
from collections import OrderedDict

from rhtools.utils import crc32, int2byte, int2hex, byte2int, hex2dec
from rhtools.Table import Table

SNES_HEADER_SIZE = 0x200
SNES_BANK_SIZE = 0x8000

#CRC32_ORIGINAL = '7F0DDCCF'
CRC32 = '5497DF2A'

POINTER_BLOCK1_START = 0x11010
POINTER_BLOCK1_END = POINTER_BLOCK1_LIMIT = 0x112ac

TEXT_BLOCK1_START = 0x100000
TEXT_BLOCK1_END = TEXT_BLOCK1_LIMIT = 0x1fffff

def neugier_dumper(args):
	""" DUMP """
	source_file = args.source_file
	table1_file = args.table1
	dump_path = args.dump_path
	db = args.database_file
	if crc32(source_file) != CRC32:
		sys.exit('SOURCE ROM CHECKSUM FAILED!')
	table1 = Table(table1_file)
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	id = 1
	with open(source_file, 'rb') as f:
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
			while not byte2int(byte) == table1.getNewline():
				byte = f.read(1)
				text += byte
			text_encoded = table1.encode(text)
			# DUMP - DB
			text_binary = sqlite3.Binary(text)
			text_address = int2hex(pointer)
			text_length = len(text_binary)
			cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, ?)', (id, buffer(text_binary), text_encoded, text_address, pointer_addresses, text_length, 1))
			# DUMP - TXT
			dump_file = os.path.join(dump_path, '%s - %d.txt' % (str(id).zfill(4), len(pointers[pointer])))
			with open(dump_file, 'w') as out:
				out.write(text_encoded)
			id += 1
		cur.close()
		conn.commit()
		conn.close()

def neugier_inserter(args):
	""" INSERTER + REPOINTER """
	dest_file = args.dest_file
	table2_file = args.table2
	db = args.database_file
	user_name = args.user
	table2 = Table(table2_file)
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	with open(dest_file, 'r+b') as f:
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

import argparse
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
a_parser = subparsers.add_parser('dump', help='Execute DUMP')
a_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
a_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
a_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
a_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
a_parser.set_defaults(func=neugier_dumper)
b_parser = subparsers.add_parser('insert', help='Execute INSERTER')
b_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
b_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
b_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
b_parser.add_argument('-u', '--user', action='store', dest='user', help='')
b_parser.set_defaults(func=neugier_inserter)
args = parser.parse_args()
args.func(args)
