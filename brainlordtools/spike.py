__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv, os, shutil, sqlite3, struct, sys

from rhtools3.Table import Table
from rhutils.db import insert_text, select_translation_by_author
from rhutils.dump import read_text, write_text, get_csv_translated_texts
from rhutils.rom import crc32, expand_rom
from rhutils.snes import pc2snes_lorom

CRC32 = '8C2068D1'

POINTER_BLOCKS = (
    (0x62090, 0x622c3),
    (0x1228f, 0x122ae),
    (0x12628, 0x12657),
    (0x10104, 0x10109),
    (0x1010a, 0x10133),
    (0x10468, 0x10497),
    (0x1068e, 0x106ad),
    (0x92e, 0x97d)
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
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        id = 1
        # READ POINTER BLOCKS
        for block, pointer_block in enumerate(POINTER_BLOCKS):
            pointers = {}
            f.seek(pointer_block[0])
            while f.tell() < pointer_block[1]:
                p_offset = f.tell()
                p_value = 0
                if block == 0:
                    pointer = f.read(3)
                    p_value = struct.unpack('i', pointer[:3] + b'\x00')[0] - 0x868000
                else:
                    pointer = f.read(2)
                    p_value = struct.unpack('H', pointer)[0] + 0x10000 - 0x8000
                if p_value > 0:
                    pointers.setdefault(p_value, []).append(p_offset)
            for _, (text_address, p_addresses) in enumerate(pointers.items()):
                pointer_addresses = ';'.join(hex(x) for x in p_addresses)
                text = read_text(f, text_address, end_byte=b'\xf0', cmd_list={b'\xf4': 2, b'\xf6': 1, b'\xf8': 1, b'\xfa': 4, b'\xfc': 1, b'\xfd': 4, b'\xfe': 1, b'\xff': 2})
                text_decoded = table1.decode(text, cmd_list={0xf4: 2, 0xf6: 1, 0xf8: 1, 0xfa: 4, 0xfc: 1, 0xfd: 4, 0xfe: 1, 0xff: 2})
                ref = f'[ID {id} - BLOCK {block + 1} - {hex(text_address)} - {pointer_addresses}]'
                # dump - db
                insert_text(cur, id, text, text_decoded, text_address, pointer_addresses, str(block + 1), ref)
                # dump - txt
                filename = os.path.join(dump_path, 'dump_eng.txt')
                with open(filename, 'a+', encoding='utf-8') as out:
                    out.write(f'{ref}\n{text_decoded}\n\n')
                id += 1
    cur.close()
    conn.commit()
    conn.close()

def spike_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        # Monsters
        filename = os.path.join(dump_path, 'monsters.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f.seek(0x62303)
            while f.tell() <= 0x626dc:
                text_address = f.tell()
                text = read_text(f, text_address, end_byte=b'\xf0')
                if text:
                    text_decoded = table.decode(text, mte_resolver=False, dict_resolver=False)
                    fields = [hex(text_address), text_decoded]
                    csv_writer.writerow(fields)

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
            _, _, text_decoded, _, pointer_addresses, translation, _ = row
            text = translation if translation else text_decoded
            text_encoded = table.encode(text)
            f.seek(new_text_address)
            f.write(text_encoded)
            f.write(b'\xf0')
            next_text_address = f.tell()
            # REPOINTER X
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
        rows = select_translation_by_author(cur, user_name, ['2', '3', '4', '5', '6', '7', '8'])
        for row in rows:
            # INSERTER X
            _, _, text_decoded, _, pointer_addresses, translation, _ = row
            text = translation if translation else text_decoded
            text_encoded = table.encode(text)
            f.seek(new_text_address)
            f.write(text_encoded)
            f.write(b'\xf0')
            next_text_address = f.tell()
            # REPOINTER X
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

def spike_misc_inserter(args):
    dest_file = args.dest_file
    table1_file = args.table1
    table2_file = args.table2
    translation_path = args.translation_path
    table = Table(table1_file)
    table2 = Table(table2_file)
    with open(dest_file, 'r+b') as f:
        # Enemies
        translation_file = os.path.join(translation_path, 'monsters.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        for i, (_, t_address, t_value) in enumerate(translated_texts):
            text = table2.encode(t_value, mte_resolver=False, dict_resolver=False)
            if len(text) > 9:
                sys.exit(f"{t_value} exceeds")
            write_text(f, t_address, text)

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
dump_misc_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMP')
dump_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_misc_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_misc_parser.set_defaults(func=spike_misc_dumper)
insert_misc_parser = subparsers.add_parser('insert_misc', help='Execute MISC INSERTER')
insert_misc_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
insert_misc_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_misc_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_misc_parser.set_defaults(func=spike_misc_inserter)
expand_parser = subparsers.add_parser('expand', help='Execute EXPANDER')
expand_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
expand_parser.set_defaults(func=spike_expander)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
