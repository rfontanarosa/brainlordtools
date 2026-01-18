__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv, pathlib, shutil, sqlite3, struct, sys

from rhutils.db import insert_text, select_most_recent_translation, select_translation_by_author
from rhutils.dump import dump_binary, read_text, get_csv_translated_texts, insert_binary, write_byte
from rhutils.rom import crc32
from rhutils.snes import pc2snes_hirom
from rhutils.table import Table

CRC32 = 'D0176B24'
# CRC32 = '31114AAC' # SADNESS

import enum

class DumpType(enum.Enum):
    EVENTS = 1
    TEXTS = 2

# pointer_block_start, pointer_block_end, text_block_start, text_block_end, bank_offset, pointer_bytes, filename
POINTERS_OFFSETS = (
    (0x90000, 0x90800, 0x90800, 0x9f2d6, 0x90000, 2, DumpType.EVENTS),
    (0xa0000, 0xa0c02, 0xa0c02, 0xab573, 0xa0000, 2, DumpType.EVENTS),
    (0x33d0, 0x33f0, 0X77a8e, 0x77b23, 0x70000, 2, DumpType.TEXTS),
    (0x7780a, 0x7784c, 0x77313, 0x77693, 0x70000, 2, DumpType.TEXTS),
    (0x33b5, 0x33d0, 0x33f0, 0x0, 0x0, 3, DumpType.TEXTS),
    (0x77bb7, 0x77bc7, 0x77b6d, 0x77ba5, 0x70000, 2, DumpType.TEXTS),
    (0x5dbb, 0x5e6b, 0x5e6b, 0x637d, 0x0, 2, DumpType.TEXTS)
)

# start, end, where_to_move
DTE_OFFSETS = (0x77299, 0x77312, 0x74350)

cmd_list = {b'\x20': 1, b'\x21': 1, b'\x22': 1, b'\x23': 1, b'\x24': 1, b'\x25': 1, b'\x26': 1, b'\x27': 1, b'\x28': 1, b'\x29': 1, b'\x2a': 1, b'\x2b': 1, b'\x2c': 1, b'\x2e': 1, b'\x2f': 1, b'\x30': 2, b'\x31': 2, b'\x32': 2, b'\x33': 2, b'\x34': 2, b'\x36': 3, b'\x37': 3, b'\x38': 1, b'\x39': 3, b'\x40': 4, b'\x42': 2, b'\x49': 3, b'\x4a': 3, b'\x4b': 3, b'\x4c': 3, b'\x4d': 3, b'\x4e': 3, b'\x57': 1, b'\x59': 1, b'\x5a': 1, b'\x5b': 2}

def som_read_text(f, offset=None, length=None, end_byte=None, cmd_list=None, append_end_byte=False):
    text = b''
    if offset is not None:
        f.seek(offset)
    if length:
        text = f.read(length)
    elif end_byte:
        while True:
            byte = f.read(1)
            if cmd_list and byte in cmd_list.keys():
                bytes_to_read = cmd_list.get(byte)
                text += byte + f.read(bytes_to_read)
            elif byte[0] >> 4 in (1,):
                text += byte + f.read(1)
            elif byte in b'\x2d':
                next_byte = f.read(1)
                text += byte + next_byte
                if next_byte in (b'\x05', b'\x06'):
                    text += f.read(2)
            elif byte in end_byte:
                if append_end_byte:
                    text += byte
                break
            else:
                text += byte
    return text

def som_text_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = pathlib.Path(args.dump_path)
    db = args.database_file
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    shutil.rmtree(dump_path, ignore_errors=True)
    pathlib.Path.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        # TEXT POINTERS
        id = 1
        for block, block_pointers in enumerate(POINTERS_OFFSETS):
            pointer_block_start, pointer_block_end, _, _, bank_offset, pointer_bytes, dump_type = block_pointers
            pointers = {}
            f.seek(pointer_block_start)
            while f.tell() < pointer_block_end:
                p_address = f.tell()
                if pointer_bytes == 3:
                    p_value = f.read(3)
                    text_address = struct.unpack('i', p_value[:3] + b'\x00')[0] - 0xc00000
                else:
                    p_value = f.read(2)
                    text_address = struct.unpack('H', p_value)[0] + bank_offset
                pointers.setdefault(text_address, []).append(p_address)
            # TEXT
            for _, (text_address, p_addresses) in enumerate(pointers.items()):
                pointer_addresses = ';'.join(str(hex(x)) for x in p_addresses)
                text = som_read_text(f, text_address, end_byte=b'\x00', cmd_list=cmd_list, append_end_byte=True)
                text_decoded = table.decode(text)
                if dump_type == DumpType.EVENTS:
                    ref = f'[ID {id} - BLOCK {block + 1} - EVENT {hex(id - 1)} - {hex(text_address)} - {pointer_addresses}]'
                else:
                    ref = f'[ID {id} - BLOCK {block + 1} - {hex(text_address)} - {pointer_addresses}]'
                # dump - db
                insert_text(cur, id, text, text_decoded, text_address, pointer_addresses, block + 1, ref)
                # dump - txt
                if dump_type == DumpType.EVENTS:
                    filename = dump_path / 'dump_events_eng.txt'
                else:
                    filename = dump_path / 'dump_texts_eng.txt'
                with open(filename, 'a+') as out:
                    out.write(ref + '\n' + text_decoded + "\n\n")
                id += 1
    cur.close()
    conn.commit()
    conn.close()

def som_text_inserter(args):
    dest_file = args.dest_file
    table2_file = args.table2
    db = args.database_file
    user_name = args.user
    table = Table(table2_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    with open(dest_file, 'r+b') as f:
        for block, block_pointers in enumerate(POINTERS_OFFSETS):
            _, _, text_block_start, text_block_end, _, _, dump_type = block_pointers
            if dump_type == DumpType.EVENTS:
                f.seek(text_block_start)
                current_text_address = f.tell()
                rows = select_translation_by_author(cur, 'clomax', [str(block + 1),])
                for row in rows:
                    _, _, text_decoded, _, pointer_address, translation, _ = row
                    text = translation if translation else text_decoded
                    text_encoded = table.encode(text)
                    if f.tell() + len(text_encoded) > text_block_end:
                        print('BANK CROSSED')
                        sys.exit()
                    f.write(text_encoded)
                    # REPOINTER
                    new_pointer_value = struct.pack('<I', current_text_address)[:2]
                    current_text_address = f.tell()
                    f.seek(int(pointer_address, 16))
                    f.write(new_pointer_value)
                    f.seek(current_text_address)
            else:
                if block + 1 == 5:
                    f.seek(0xb3800)
                    current_text_address = f.tell()
                    rows = select_translation_by_author(cur, 'clomax', [str(block + 1),])
                    for row in rows:
                        _, _, text_decoded, _, pointer_address, translation, _ = row
                        text = translation if translation else text_decoded
                        text_encoded = table.encode(text)
                        if f.tell() + len(text_encoded) > 0xb3fff:
                            print('BANK CROSSED')
                            sys.exit()
                        f.write(text_encoded)
                        # REPOINTER
                        snes_offset = pc2snes_hirom(current_text_address)
                        new_pointer_value = struct.pack('<I', snes_offset)[:3]
                        current_text_address = f.tell()
                        f.seek(int(pointer_address, 16))
                        f.write(new_pointer_value)
                        f.seek(current_text_address)
                elif block + 1 == 7:
                    f.seek(text_block_start)
                    current_text_address = f.tell()
                    rows = select_translation_by_author(cur, 'clomax', [str(block + 1),])
                    for row in rows:
                        _, _, text_decoded, _, pointer_address, translation, _ = row
                        text = translation if translation else text_decoded
                        text_encoded = table.encode(text)
                        if f.tell() + len(text_encoded) > text_block_end:
                            print('BANK CROSSED')
                            sys.exit()
                        f.write(text_encoded)
                        # REPOINTER
                        new_pointer_value = struct.pack('<I', current_text_address)[:2]
                        current_text_address = f.tell()
                        f.seek(int(pointer_address, 16))
                        f.write(new_pointer_value)
                        f.seek(current_text_address)
                else:
                    pass
        f.seek(0x74900)
        current_text_address = f.tell()
        rows = select_translation_by_author(cur, 'clomax', ['3', '4', '6'])
        for row in rows:
            id, _, text_decoded, _, pointer_addresses, translation, _ = row
            # SKIP
            if id in (2579, 2580, 2582, 2583, 2585, 2586, 2588, 2589, 2591, 2592, 2594, 2595, 2596, 2597, 2599, 2600, 2602, 2603, 2605):
                continue
            # INSERTER
            text = translation if translation else text_decoded
            text_encoded = table.encode(text)
            if f.tell() + len(text_encoded) > 0x74fff:
                sys.exit('BANK CROSSED')
            f.write(text_encoded)
            # REPOINTER
            new_pointer_value = struct.pack('<I', current_text_address)[:2]
            current_text_address = f.tell()
            for pointer_address in pointer_addresses.split(';'):
                f.seek(int(pointer_address, 16))
                f.write(new_pointer_value)
            f.seek(current_text_address)
    cur.close()
    conn.close()

def som_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = pathlib.Path(args.dump_path)
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    pathlib.Path.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        # DTE
        filepath = dump_path / 'dte.csv'
        with filepath.open('w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f.seek(DTE_OFFSETS[0])
            while f.tell() < DTE_OFFSETS[1]:
                text_address_start = f.tell()
                text = read_text(f, text_address_start, length=2)
                text_decoded = table.decode(text)
                fields = [hex(text_address_start), text_decoded]
                csv_writer.writerow(fields)

def som_tilemap_dumper(args):
    source_file = args.source_file
    dump_path = pathlib.Path(args.dump_path)
    with open(source_file, 'rb') as f:
        # INTRO TILEMAP
        dump_binary(f, 0x14a6, 928, dump_path / 'intro-tilemap.bin')

def som_misc_inserter(args):
    dest_file = args.dest_file
    table1_file = args.table1
    translation_path = pathlib.Path(args.translation_path)
    table1 = Table(table1_file)
    with open(dest_file, 'r+b') as f:
        # DTE
        filepath = translation_path / 'dte.csv'
        translated_texts = get_csv_translated_texts(filepath)
        f.seek(DTE_OFFSETS[2])
        for _, (_, _, text_value) in enumerate(translated_texts):
            encoded_text = table1.encode(text_value)
            f.write(encoded_text)
            if f.tell() > DTE_OFFSETS[2] + (2 * 69):
                sys.exit('Text size exceeds!')
        # CARDINALS
        insert_binary(f, 0x7FB00, translation_path / '7FB00_cardinals.bin', max_length=160)
        # INTRO
        with open(dest_file, 'r+b') as f:
            insert_binary(f, 0x77C00, translation_path / 'intro-code-compressed.bin', max_length=14437)
            insert_binary(f, 0x7B480, translation_path / 'intro-data-compressed.bin', max_length=3390)
            insert_binary(f, 0x1CE800, translation_path / 'title-compressed.bin', max_length=2096)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--no_crc32_check', action='store_true', dest='no_crc32_check', required=False, default=False, help='CRC32 Check')
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
dump_text_parser = subparsers.add_parser('dump_text', help='Execute TEXT DUMP')
dump_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_text_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_text_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Menu table filename')
dump_text_parser.add_argument('-t3', '--table3', action='store', dest='table3', help='Intro table filename')
dump_text_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
dump_text_parser.set_defaults(func=som_text_dumper)
insert_text_parser = subparsers.add_parser('insert_text', help='Execute TEXT INSERTER')
insert_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_text_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_text_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_text_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
insert_text_parser.add_argument('-u', '--user', action='store', dest='user', help='')
insert_text_parser.set_defaults(func=som_text_inserter)
dump_misc_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMP')
dump_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_misc_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Menu table filename')
dump_misc_parser.add_argument('-t3', '--table3', action='store', dest='table3', help='Intro table filename')
dump_misc_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_misc_parser.set_defaults(func=som_misc_dumper)
dump_tilemap_parser = subparsers.add_parser('dump_tilemap', help='Execute TILEMAP DUMP')
dump_tilemap_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_tilemap_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_tilemap_parser.set_defaults(func=som_tilemap_dumper)
insert_misc_parser = subparsers.add_parser('insert_misc', help='Execute MISC INSERTER')
insert_misc_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
insert_misc_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Menu table filename')
insert_misc_parser.add_argument('-t3', '--table3', action='store', dest='table3', help='Intro table filename')
insert_misc_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_misc_parser.set_defaults(func=som_misc_inserter)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
