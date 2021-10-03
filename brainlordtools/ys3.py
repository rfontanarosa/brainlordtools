__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv, os, shutil, sqlite3, struct, sys
from collections import OrderedDict

from rhtools.utils import crc32, hex2dec, int_address2string_address2
from rhtools3.db import insert_text, convert_to_binary
from rhtools.dump import read_text, dump_binary
from rhtools3.Table import Table

CRC32 = '64A91E64'

GFX_BLOCK = (0xf300, 0xff00)

POINTER_BLOCKS = (
    (0x280b4, 0x28413),
    (0x20000, 0x20267)
)

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

def ys3_text_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    db = args.database_file
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table1 = Table(table1_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    shutil.rmtree(dump_path, ignore_errors=True)
    os.makedirs(dump_path)
    id = 1
    with open(source_file, 'rb') as f:
        # READ POINTER BLOCKS
        for index, pointer_block in enumerate(POINTER_BLOCKS):
            pointers = OrderedDict()
            f.seek(pointer_block[0])
            while f.tell() < pointer_block[1]:
                p_offset = f.tell()
                p_value = 0
                if index == 0:
                    pointer = f.read(2)
                    p_value = struct.unpack('H', pointer)[0] + 0x20000
                else:
                    pointer = f.read(2)
                    p_value = struct.unpack('H', pointer)[0] + 0x18000
                if p_value > 0:
                    pointers.setdefault(p_value, []).append(p_offset)
            # TEXT 1
            for i, (taddress, paddresses) in enumerate(pointers.items()):
                pointer_addresses = ';'.join(hex(x) for x in paddresses)
                text = read_text(f, taddress, end_byte=b'\xff', cmd_list={b'\xf0': 2, b'\xf1': 2, b'\xf2': 1, b'\xf3': 1, b'\xf6': 1, b'\xf7': 1})
                text_decoded = table1.decode(text, cmd_list={0xf0: 2, 0xf1: 2, 0xf2: 1, 0xf3: 1, 0xf6: 1, 0xf7: 1})
                # dump - db
                insert_text(cur, id, convert_to_binary(text), text_decoded, taddress, pointer_addresses, 1, id)
                # dump - txt
                filename = os.path.join(dump_path, 'dump_eng.txt')
                with open(filename, 'a+') as out:
                    out.write(str(id) + ' - ' + pointer_addresses + '\n' + text_decoded + "\n\n")
                id += 1
    cur.close()
    conn.commit()
    conn.close()

def ys3_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f, open(source_file, 'rb') as f1:
        filename = os.path.join(dump_path, 'misc.csv')
        with open(filename, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f.seek(0x3bab)
            text_address = f.tell()
            text = read_text(f, f.tell(), end_byte=b'\x1d')
            text_encoded = table.decode(text)
            fields = [hex(text_address), text_encoded]
            csv_writer.writerow(fields)

def ys3_gfx_dumper(args):
    source_file = args.source_file
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_binary(f, GFX_BLOCK[0], GFX_BLOCK[1], dump_path, 'gfx_1.bin')

def ys3_text_inserter(args):
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
parser.add_argument('--no_crc32_check', action='store_true', dest='no_crc32_check', required=False, default=False, help='CRC32 Check')
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
dump_text_parser = subparsers.add_parser('dump_text', help='Execute DUMP')
dump_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_text_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_text_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
dump_text_parser.set_defaults(func=ys3_text_dumper)
insert_text_parser = subparsers.add_parser('insert_text', help='Execute INSERTER')
insert_text_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_text_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
insert_text_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
insert_text_parser.add_argument('-u', '--user', action='store', dest='user', help='')
insert_text_parser.set_defaults(func=ys3_text_inserter)
dump_gfx_parser = subparsers.add_parser('dump_gfx', help='Execute GFX DUMP')
dump_gfx_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_gfx_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_gfx_parser.set_defaults(func=ys3_gfx_dumper)
dump_misc_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMP')
dump_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_misc_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_misc_parser.set_defaults(func=ys3_misc_dumper)
args = parser.parse_args()
args.func(args)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()

