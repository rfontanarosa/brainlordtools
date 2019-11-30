__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3
from collections import OrderedDict

from rhtools.utils import crc32, hex2dec, int2hex, byte2int, int_address2string_address2
from rhtools.OldTable import Table

SNES_HEADER_SIZE = 0x200
SNES_BANK_SIZE = 0x8000

CRC32 = '64A91E64'

POINTER_BLOCK1_START = 0x280b4
POINTER_BLOCK1_END = POINTER_BLOCK1_LIMIT = 0x28413
POINTER_BLOCK2_START = 0x20000
POINTER_BLOCK2_END = POINTER_BLOCK2_LIMIT = 0x20267

TEXT_BLOCK1_START = 0x28418
TEXT_BLOCK1_END = TEXT_BLOCK1_LIMIT = 0x2fc73
TEXT_BLOCK1_SIZE = TEXT_BLOCK1_END - TEXT_BLOCK1_START
TEXT_BLOCK1_MAX_SIZE = TEXT_BLOCK1_LIMIT - TEXT_BLOCK1_START
TEXT_BLOCK2_START = 0x2026a
TEXT_BLOCK2_END = TEXT_BLOCK2_LIMIT = 0x229d1
TEXT_BLOCK2_SIZE = TEXT_BLOCK2_END - TEXT_BLOCK2_START
TEXT_BLOCK2_MAX_SIZE = TEXT_BLOCK2_LIMIT - TEXT_BLOCK2_START

def ys3_dumper(args):
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
		# POINTERS 1
		pointers = OrderedDict()
		f.seek(POINTER_BLOCK1_START)
		while(f.tell() < POINTER_BLOCK1_END):
			paddress = f.tell()
			pvalue = f.read(2)
			pvalue2 = struct.unpack('H', pvalue)[0] + 0x20000
			if pvalue2 not in pointers:
				pointers[pvalue2] = []
			pointers[pvalue2].append(paddress)
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
			text_encoded = table1.encode(text, separated_byte_format=False)
			# DUMP - DB
			text_binary = sqlite3.Binary(text)
			text_address = int2hex(pointer)
			text_length = len(text_binary)
			cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, 1)', (id, buffer(text_binary), text_encoded, text_address, pointer_addresses, text_length))
			# DUMP - TXT
			dump_file = os.path.join(dump_path, '%s - %s.txt' % (str(id).zfill(3), pointer_addresses))
			with open(dump_file, 'w') as out:
				out.write(text_encoded)
			id += 1
		# POINTERS 2
		pointers = OrderedDict()
		f.seek(POINTER_BLOCK2_START)
		while(f.tell() < POINTER_BLOCK2_END):
			paddress = f.tell()
			pvalue = f.read(2)
			pvalue2 = struct.unpack('H', pvalue)[0] + 0x18000
			if pvalue2 not in pointers:
				pointers[pvalue2] = []
			pointers[pvalue2].append(paddress)
		# TEXT 2
		for pointer in pointers:
			if pointer not in [98304]:
				pointer_addresses = ''
				for pointer_address in pointers[pointer]:
					pointer_addresses += str(int2hex(pointer_address)) + ';'
				f.seek(pointer)
				text = b''
				byte = b'1'
				while not byte2int(byte) == table1.getNewline():
					byte = f.read(1)
					text += byte
				text_encoded = table1.encode(text, separated_byte_format=True)
				# DUMP - DB
				text_binary = sqlite3.Binary(text)
				text_address = int2hex(pointer)
				text_length = len(text_binary)
				cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, 2)', (id, buffer(text_binary), text_encoded, text_address, pointer_addresses, text_length))
				# DUMP - TXT
				dump_file = os.path.join(dump_path, '%s - %s.txt' % (str(id).zfill(3), pointer_addresses))
				with open(dump_file, 'w') as out:
					out.write(text_encoded)
				id += 1
	cur.close()
	conn.commit()
	conn.close()

def ys3_inserter(args):
	""" INSERTER + REPOINTER """
	dest_file = args.dest_file
	table1_file = args.table1
	table2_file = args.table2
	db = args.database_file
	user_name = args.user
	table1 = Table(table1_file)
	table2 = Table(table2_file)
	conn = sqlite3.connect(db)
	conn.text_factory = str
	cur = conn.cursor()
	with open(dest_file, 'r+b') as f:
		# BLOCK 1
		f.seek(TEXT_BLOCK1_START)
		cur.execute("SELECT text, new_text, text_encoded, id, new_text2, address, pointer_address, size FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text WHERE t1.block = 1" % user_name)
		for row in cur:
			# INSERTER 1
			id = row[3]
			original_text = row[2]
			new_text = row[4]
			if (new_text):
				text = new_text
				decoded_text = table2.decode(text, True)
			else:
				text = original_text
				decoded_text = table1.decode(text, True)
			new_text_address = f.tell()
			f.seek(new_text_address)
			f.write(decoded_text)
			next_text_address = f.tell()
			if next_text_address > (TEXT_BLOCK1_LIMIT + 1):
				sys.exit('CRITICAL ERROR! TEXT_BLOCK_LIMIT! %s > %s (%s)' % (next_text_address, TEXT_BLOCK1_LIMIT, (TEXT_BLOCK1_LIMIT - next_text_address)))
			# REPOINTER 1
			pointer_addresses = row[6]
			if pointer_addresses:
				for pointer_address in pointer_addresses.split(';'):
					if pointer_address:
						pointer_address = hex2dec(pointer_address)
						f.seek(pointer_address)
						f.write(int_address2string_address2(new_text_address-0x20000, switch=True, shift=2))
						if pointer_address > (POINTER_BLOCK1_LIMIT + 1):
							sys.exit('CRITICAL ERROR! POINTER_BLOCK_LIMIT! %s > %s (%s)' % (pointer_address, POINTER_BLOCK1_LIMIT, (POINTER_BLOCK1_LIMIT - pointer_address)))
			f.seek(next_text_address)
		# BLOCK 2
		f.seek(TEXT_BLOCK2_START)
		cur.execute("SELECT text, new_text, text_encoded, id, new_text2, address, pointer_address, size FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text WHERE t1.block = 2" % user_name)
		for row in cur:
			# INSERTER 2
			id = row[3]
			original_text = row[2]
			new_text = row[4]
			if (new_text):
				text = new_text
				decoded_text = table2.decode(text, True)
			else:
				text = original_text
				decoded_text = table1.decode(text, True)
			new_text_address = f.tell()
			f.seek(new_text_address)
			f.write(decoded_text)
			next_text_address = f.tell()
			if next_text_address - 0x8000 > (TEXT_BLOCK2_LIMIT + 1):
				sys.exit('CRITICAL ERROR! TEXT_BLOCK_LIMIT! %s > %s (%s)' % (next_text_address, TEXT_BLOCK2_LIMIT, (TEXT_BLOCK2_LIMIT - next_text_address)))
			# REPOINTER 2
			if id != 547:
				padresses = row[6]
				if padresses:
					for paddress in padresses.split(';'):
						if paddress:
							paddress = hex2dec(paddress)
							f.seek(paddress)
							pvalue = struct.pack('H', new_text_address - 0x18000)
							f.write(pvalue)
							if paddress - 0x8000 > (POINTER_BLOCK2_LIMIT + 1):
								sys.exit('CRITICAL ERROR! POINTER_BLOCK_LIMIT! %s > %s (%s)' % (paddress, POINTER_BLOCK2_LIMIT, (POINTER_BLOCK2_LIMIT - paddress)))
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
a_parser.set_defaults(func=ys3_dumper)
b_parser = subparsers.add_parser('insert', help='Execute INSERTER')
b_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
b_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
b_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
b_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
b_parser.add_argument('-u', '--user', action='store', dest='user', help='')
b_parser.set_defaults(func=ys3_inserter)
args = parser.parse_args()
args.func(args)
