__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv, os, shutil, sqlite3, struct, sys
from collections import OrderedDict

from rhtools3.db import insert_text, select_translation_by_author, select_most_recent_translation
from rhtools.dump import read_text, write_text, get_csv_translated_texts
from rhutils.snes import pc2snes_hirom
from rhutils.rom import crc32, expand_rom
from rhutils.table import Table

CRC32 = 'EE441564'

BLOCK_BANKS_OFFSETS = (0xC7D9, 0xC7EC)
BLOCK_POINTERS_OFFSET = (0xC7EC, 0xC812)

POINTER_TABLES_SIZES = (22, 22, 17, 37, 20, 21, 18, 17, 15, 115, 26, 3, 21, 30, 2, 4, 35, 1, 2)

def ignition_text_dumper(args):
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
    if not os.path.isdir(dump_path):
        os.mkdir(dump_path)
    if os.path.isfile(os.path.join(dump_path, 'dump_eng.txt')):
        os.remove(os.path.join(dump_path, 'dump_eng.txt'))
    id = 1
    with open(source_file, 'rb') as f1, open(source_file, 'rb') as f2:
        block_pointers = []
        f1.seek(BLOCK_BANKS_OFFSETS[0])
        f2.seek(BLOCK_POINTERS_OFFSET[0])
        while f1.tell() < BLOCK_BANKS_OFFSETS[1]:
            p_offset1 = f1.tell()
            p_offset2 = f2.tell()
            p_value = struct.unpack('i', f2.read(2) + f1.read(1) + b'\x00')[0] & 0x3fffff
            block_pointers.append((p_value, p_offset1, p_offset2))
        #
        for i, block_pointer in enumerate(block_pointers):
            b_address = block_pointer[0]
            p_qty = POINTER_TABLES_SIZES[i]
            pointers = []
            f1.seek(b_address)
            for k in range(0, p_qty):
                p_offset = f1.tell()
                p_value = struct.unpack('H', f1.read(2))[0] + (b_address & 0xff0000)
                pointers.append((p_value, p_offset))
            for index, (taddress, paddresses) in enumerate(pointers):
                pointer_addresses = hex(paddresses)
                text = read_text(f1, taddress, end_byte=b'\xff', cmd_list={b'\xfc': 2}, append_end_byte=True)
                text_decoded = table1.decode(text)
                # dump - db
                insert_text(cur, id, text, text_decoded, taddress, pointer_addresses, str(index + 1), id)
                # dump - txt
                filename = os.path.join(dump_path, 'dump_eng.txt')
                with open(filename, 'a+') as out:
                    out.write('[ID {} - BLOCK {} - ORDER {} - {} - {}]\n{}'.format(id, i, index, hex(taddress), pointer_addresses, text_decoded))
                id += 1
            # sys.exit()
    cur.close()
    conn.commit()
    conn.close()

def ignition_text_inserter(args):
    dest_file = args.dest_file
    table2_file = args.table2
    db = args.database_file
    user_name = args.user
    table = Table(table2_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    with open(dest_file, 'r+b') as f:
        #
        new_pointer_table_offset = 0x78c00
        for index, size in enumerate(POINTER_TABLES_SIZES):
            new_pointer = pc2snes_hirom(new_pointer_table_offset)
            block_banks_offset = BLOCK_BANKS_OFFSETS[0] + index
            f.seek(block_banks_offset)
            f.write(bytes([new_pointer >> 16]))
            block_pointers_offset = BLOCK_POINTERS_OFFSET[0] + (index * 2)
            f.seek(block_pointers_offset)
            block_pointer = (new_pointer & 0x00ffff).to_bytes(2, byteorder='little')
            f.write(block_pointer)
            new_pointer_table_offset += (size * 2)
        # TEXT 1
        new_pointer_table_offset = 0x78c00
        new_text_address = 0x78f50
        rows = select_translation_by_author(cur, user_name)
        for row in rows:
            # INSERTER X
            _, _, text_decoded, _, _, translation, _ = row
            text = translation if translation else text_decoded
            text_encoded = table.encode(text)
            f.seek(new_text_address)
            f.write(text_encoded)
            f.write(b'\xff')
            # REPOINTER X
            pvalue = (pc2snes_hirom(new_text_address) & 0x00ffff).to_bytes(2, byteorder='little')
            new_text_address = f.tell()
            f.seek(new_pointer_table_offset)
            f.write(pvalue)
            new_pointer_table_offset = f.tell()
    cur.close()
    conn.close()

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--no_crc32_check', action='store_true', dest='no_crc32_check', required=False, default=False, help='CRC32 Check')
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
dump_text_parser = subparsers.add_parser('dump_text', help='Execute TEXT DUMP')
dump_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_text_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_text_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
dump_text_parser.set_defaults(func=ignition_text_dumper)
insert_text_parser = subparsers.add_parser('insert_text', help='Execute TEXT INSERTER')
insert_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_text_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_text_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_text_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
insert_text_parser.add_argument('-u', '--user', action='store', dest='user', help='')
insert_text_parser.set_defaults(func=ignition_text_inserter)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
