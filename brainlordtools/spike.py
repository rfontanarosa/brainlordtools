__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os, shutil, sqlite3, struct, sys
from collections import OrderedDict

from rhtools.utils import crc32, expand_rom, file_copy
from rhtools3.db import insert_text, convert_to_binary, select_translation_by_author, select_most_recent_translation
from rhtools.dump import read_text
from rhtools.snes_utils import snes2pc_lorom, pc2snes_lorom
from rhtools3.Table import Table

CRC32 = '8C2068D1'

# POINTER_BLOCK_1 is empty!
# POINTER_BLOCK_1 = (0x62003, 0x6208f)

POINTER_BLOCKS = (
    (0x62090, 0x622c3),
    # (0x930, 0x97d),
    # (0x10104, 0x10109),
    # (0x1010c, 0x10133),
    # (0x10468, 0x10497),
    # (0x1068e, 0x106ad),
    (0x1228f, 0x122ae),
    (0x12628, 0x12657)
)

NEW_TEXT_OFFSET_1 = 0x140000
NEW_TEXT_OFFSET_2 = 0x148000

def spike_text_dumper(args):
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
    shutil.rmtree(dump_path, ignore_errors=False)
    os.mkdir(dump_path)
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
                    pointer = f.read(3)
                    p_value = struct.unpack('i', pointer[:3] + b'\x00')[0] - 0x868000
                else:
                    pointer = f.read(2)
                    p_value = struct.unpack('H', pointer)[0] + 0x10000 - 0x8000
                if p_value > 0:
                    pointers.setdefault(p_value, []).append(p_offset)
            for i, (taddress, paddresses) in enumerate(pointers.items()):
                pointer_addresses = ';'.join(hex(x) for x in paddresses)
                text = read_text(f, taddress, end_byte=b'\xf0', cmd_list={b'\xf4': 2, b'\xf6': 1, b'\xf8': 1, b'\xfa': 4, b'\xfc': 1, b'\xfd': 4, b'\xfe': 1, b'\xff': 2})
                text_decoded = table1.decode(text, cmd_list={0xf4: 2, 0xf6: 1, 0xf8: 1, 0xfa: 4, 0xfc: 1, 0xfd: 4, 0xfe: 1, 0xff: 2})
                # dump - db
                insert_text(cur, id, convert_to_binary(text), text_decoded, taddress, pointer_addresses, str(index + 1), id)
                # dump - txt
                filename = os.path.join(dump_path, 'dump_eng.txt')
                with open(filename, 'a+') as out:
                    out.write(str(id) + ' - ' + pointer_addresses + '\n' + text_decoded + "\n\n")
                id += 1
    cur.close()
    conn.commit()
    conn.close()

def spike_text_inserter(args):
    dest_file = args.dest_file
    table2_file = args.table2
    db = args.database_file
    user_name = args.user
    table = Table(table2_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    with open(dest_file, 'r+b') as f:
        # TEXT 1
        new_text_address = NEW_TEXT_OFFSET_1
        rows = select_translation_by_author(cur, user_name, ['1'])
        for row in rows:
            # INSERTER X
            id = row[0]
            address = row[3]
            text_decoded = row[2]
            translation = row[5]
            text = translation if translation else text_decoded
            text_encoded = table.encode(text)
            f.seek(new_text_address)
            f.write(text_encoded)
            f.write(b'\xf0')
            next_text_address = f.tell()
            # REPOINTER X
            pointer_addresses = row[4]
            if pointer_addresses:
                pvalue = struct.pack('i', pc2snes_lorom(new_text_address) + 0x800000)
                for pointer_address in pointer_addresses.split(';'):
                    if pointer_address:
                        pointer_address = int(pointer_address, 16)
                        f.seek(pointer_address)
                        f.write(bytes(pvalue[:-1]))
            new_text_address = next_text_address
        # TEXT 2
        new_text_address = NEW_TEXT_OFFSET_2
        rows = select_translation_by_author(cur, user_name, ['2', '3'])
        for row in rows:
            # INSERTER X
            id = row[0]
            address = row[3]
            text_decoded = row[2]
            translation = row[5]
            text = translation if translation else text_decoded
            text_encoded = table.encode(text)
            f.seek(new_text_address)
            f.write(text_encoded)
            f.write(b'\xf0')
            next_text_address = f.tell()
            # REPOINTER X
            pointer_addresses = row[4]
            if pointer_addresses:
                pvalue = struct.pack('i', pc2snes_lorom(new_text_address) + 0x800000)
                for pointer_address in pointer_addresses.split(';'):
                    if pointer_address:
                        pointer_address = int(pointer_address, 16)
                        f.seek(pointer_address)
                        f.write(bytes(pvalue[:2]))
            new_text_address = next_text_address
    cur.close()
    conn.close()

def spike_expander(args):
    dest_file = args.dest_file
    size_to_expand = (1048576 + 524288) - os.path.getsize(dest_file)
    expand_rom(dest_file, size_to_expand)

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
dump_text_parser.set_defaults(func=spike_text_dumper)
insert_text_parser = subparsers.add_parser('insert_text', help='Execute TEXT INSERTER')
insert_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_text_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_text_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_text_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
insert_text_parser.add_argument('-u', '--user', action='store', dest='user', help='')
insert_text_parser.set_defaults(func=spike_text_inserter)
expand_parser = subparsers.add_parser('expand', help='Execute EXPANDER')
expand_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
expand_parser.set_defaults(func=spike_expander)
file_copy_parser = subparsers.add_parser('file_copy', help='File COPY')
file_copy_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
file_copy_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
file_copy_parser.set_defaults(func=file_copy)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
