__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3, shutil

from rhtools3.Table import Table
from rhutils.db import insert_text, select_translation_by_author
from rhutils.dump import read_text, dump_binary, insert_binary
from rhutils.rom import crc32

SNES_BANK_SIZE = 0x8000

CRC32 = '74F70A0B'

TEXT_BLOCK_START = 0x50fbe
TEXT_BLOCK_END = 0x594ef
TEXT_BLOCK_LIMIT = 0x594ef
TEXT_BLOCK_SIZE = TEXT_BLOCK_END - TEXT_BLOCK_START
TEXT_BLOCK_MAX_SIZE = TEXT_BLOCK_LIMIT - TEXT_BLOCK_START

POINTER_BLOCK_START = 0x50d2a
POINTER_BLOCK_END = 0x50fbd

def get_size(f, taddress):
	size = None
	if f.tell() < POINTER_BLOCK_END:
		next_pvalue = f.read(2)
		next_taddress = struct.unpack('H', next_pvalue)[0] + (SNES_BANK_SIZE * 0xa)
		f.seek(-2, os.SEEK_CUR)
		size = next_taddress - taddress
	else:
		size = TEXT_BLOCK_LIMIT - taddress
	return size

def brandish_text_dumper(args):
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
	shutil.rmtree(dump_path, ignore_errors=True)
	os.mkdir(dump_path)
	with open(source_file, 'rb') as f1, open(source_file, 'rb') as f2:
		id = 1
		f1.seek(POINTER_BLOCK_START)
		while (f1.tell() < POINTER_BLOCK_END):
			paddress = f1.tell()
			pvalue = f1.read(2)
			taddress = struct.unpack('H', pvalue)[0] + (SNES_BANK_SIZE * 0xa)
			size = get_size(f1, taddress)
			#
			f2.seek(taddress)
			text = f2.read(size)
			text_encoded = table1.encode(text, False, False)
			text_binary = sqlite3.Binary(text)
			text_address = int2hex(taddress)
			text_length = len(text_binary)
			pointer_address = int2hex(int(paddress))
			cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, 1)', (id, buffer(text_binary), text_encoded, text_address, pointer_address, text_length))
			# DUMP - TXT
			dump_file = os.path.join(dump_path, '%s - %d.txt' % (str(id).zfill(3), pointer_address))
			with open(dump_file, 'w') as out:
				out.write(text_encoded)
			id += 1
	cur.close()
	conn.commit()
	conn.close()

def brandish_text_inserter(args):
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
		""" REPOINTER """
		taddress = TEXT_BLOCK_START
		f.seek(POINTER_BLOCK_START)
		cur.execute("SELECT text, text_encoded, new_text2, id FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s') AS t2 ON t1.id=t2.id_text WHERE t1.block = 1" % user_name)
		for row in cur:
			original_text = row[1]
			new_text = row[2]
			text = new_text if new_text else original_text
			decoded_text = table2.decode(text, False, False) if new_text else table1.decode(text, False, False)
			pvalue = struct.pack('H', taddress - (SNES_BANK_SIZE * 0xa))
			f.write(pvalue) # address to write
			taddress += len(decoded_text) # next address to write
		""" INSERTER """
		f.seek(TEXT_BLOCK_START)
		cur.execute("SELECT text, text_encoded, new_text2, id FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s') AS t2 ON t1.id=t2.id_text WHERE t1.block = 1" % user_name)
		for row in cur:
			original_text = row[1]
			new_text = row[2]
			text = new_text if new_text else original_text
			decoded_text = table2.decode(text, False, False) if new_text else table1.decode(text, False, False)
			f.write(decoded_text)
			if f.tell() > TEXT_BLOCK_LIMIT:
				sys.exit('CRITICAL ERROR! TEXT_BLOCK_LIMIT! %s > %s (%s)' % (f.tell(), TEXT_BLOCK_LIMIT, (TEXT_BLOCK_LIMIT - f.tell())))
		for i in range(0, TEXT_BLOCK_LIMIT - f.tell()):
			f.write('0')
	cur.close()
	conn.close()

def brandish_gfx_dumper(args):
	source_file = args.source_file
	dump_path = args.dump_path
	if crc32(source_file) != CRC32:
		sys.exit('SOURCE ROM CHECKSUM FAILED!')
	shutil.rmtree(dump_path, ignore_errors=True)
	os.mkdir(dump_path)
	with open(source_file, 'rb') as f:
		dump_binary(f, 0x13400, 0x13800 - 0x13400, os.path.join(dump_path, 'gfx_yes-or-no.bin'))
		dump_binary(f, 0x20000, 0x21400 - 0x20000, os.path.join(dump_path, 'gfx_font.bin'))
		dump_binary(f, 0x40000, 0x4c000- 0x40000, os.path.join(dump_path, 'gfx_zones_h.bin'))

def brandish_gfx_inserter(args):
	dest_file = args.dest_file
	translation_path = args.translation_path
	with open(dest_file, 'r+b') as f:
		insert_binary(f, 0x13400, os.path.join(translation_path, 'gfx_yes-or-no.bin'), max_length=0x13800 - 0x13400)
		insert_binary(f, 0x20000, os.path.join(translation_path, 'gfx_font.bin'), max_length=0x21400 - 0x20000)
		insert_binary(f, 0x40000, os.path.join(translation_path, 'gfx_zones_h.bin'), max_length=0x4c000- 0x40000)

import argparse
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
a_parser = subparsers.add_parser('dump_text', help='Execute DUMP')
a_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
a_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
a_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
a_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
a_parser.set_defaults(func=brandish_text_dumper)
b_parser = subparsers.add_parser('insert_text', help='Execute INSERTER')
b_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
b_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
b_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
b_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
b_parser.add_argument('-u', '--user', action='store', dest='user', help='')
b_parser.set_defaults(func=brandish_text_inserter)
c_parser = subparsers.add_parser('dump_gfx', help='Execute GFX DUMP')
c_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
c_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
c_parser.set_defaults(func=brandish_gfx_dumper)
d_parser = subparsers.add_parser('insert_gfx', help='Execute GFX INSERTER')
d_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
d_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
d_parser.set_defaults(func=brandish_gfx_inserter)

if __name__ == "__main__":
	args = parser.parse_args()
	if args.func:
		args.func(args)
	else:
		parser.print_help()
