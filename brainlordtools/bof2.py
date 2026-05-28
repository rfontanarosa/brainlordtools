__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv
import pathlib
import shutil
import sqlite3
import struct

from rhutils.db import insert_text
from rhutils.dump import extract_binary, insert_binary
from rhutils.io import read_text
from rhutils.table import Table

POINTERS_BLOCKS = (
    (0x22e000, 0x22e7a1, 0x290000),
    (0x22e7a2, 0x22ef29, 0x2a0000),
    (0x22ef2a, 0x22fadf, 0x2b0000),
    (0x22fae0, 0x22ffff, 0x2c0000)
)

cmd_list = {b'\x03': 1, b'\x07': 1, b'\x08': 1, b'\x09': 1, b'\x0b': 1, b'\x11': 1, b'\x12': 1, b'\x13': 1}

def bof2_text_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = pathlib.Path(args.dump_path)
    db = args.database_file
    table = Table(table1_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    shutil.rmtree(dump_path, ignore_errors=True)
    dump_path.mkdir()
    with open(source_file, 'rb') as f:
        current_id, pointer_index = 1, 0
        for block, block_pointers in enumerate(POINTERS_BLOCKS, start=1):
            pointer_block_start, pointer_block_end, offset = block_pointers
            pointers = {}
            # READ POINTERS
            f.seek(pointer_block_start)
            while f.tell() < pointer_block_end:
                pointer_address = f.tell()
                pointer_value = f.read(2)
                text_address = struct.unpack('H', pointer_value)[0] + offset
                pointers.setdefault(text_address, []).append(pointer_address)
            # READ TEXT
            for _, (text_address, pointer_addresses) in enumerate(pointers.items()):
                pointer_addresses_str = ';'.join(hex(x) for x in pointer_addresses)
                text = read_text(f, text_address, end_byte=b'\x01', cmd_list=cmd_list)
                text_decoded = table.decode(text)
                ref = f'[ID={current_id} BLOCK={block} START={hex(text_address)} POINTER_INDEX={pointer_index} POINTERS={pointer_addresses_str}]'
                filename = 'dump_eng.txt'
                # dump - db
                insert_text(cur, current_id, text_decoded, text_address, pointer_addresses_str, len(text), block, ref, 'default', filename, current_id)
                # dump - txt
                with open(dump_path /filename, 'a+', encoding='utf-8') as out:
                    out.write(f'{ref}\n{text_decoded}\n\n')
                current_id += 1
                pointer_index += len(pointer_addresses)
    cur.close()
    conn.commit()
    conn.close()

def bof2_text_inserter(args):
    dest_file = args.dest_file
    table2_file = args.table2
    translation_path = pathlib.Path(args.translation_path)
    db = args.database_file
    user_name = args.user
    table = Table(table2_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    #
    entries = []
    #
    with open(translation_path / 'dump_ita.txt', 'r', encoding='utf-8') as f:
        buffer = ['', 0]
        for line in f:
            if '[ID=' in line and 'POINTERS=' in line:
                pointers_part = line.split('POINTERS=')[-1].split(']')[0]
                number_of_pointers = len(pointers_part.split(';')) if pointers_part else 0
                buffer = ['', number_of_pointers]
                entries.append(buffer)
            else:
                buffer[0] += line
    #
    with open(dest_file, 'rb+') as f:
        ptr_table_offset = 0x22e000
        current_bank_offset = 0x290000
        next_bank_offset = current_bank_offset + 0x10000

        bank_entries = []
        current_bank_entries = 0

        f.seek(current_bank_offset)
        for entry in entries:
            text, number_of_pointers = entry
            encoded_text = table.encode(text)
            current_text_offset = f.tell()
            if current_text_offset + len(encoded_text) >= next_bank_offset:
                current_bank_offset += 0x10000
                next_bank_offset = current_bank_offset + 0x10000
                bank_entries.append(current_bank_entries)
                current_text_offset = current_bank_offset
            # pointer
            f.seek(ptr_table_offset)
            new_pointer = (current_text_offset & 0x00FFFF).to_bytes(2, byteorder='little')
            for _ in range(0, number_of_pointers):
                f.write(new_pointer)
            ptr_table_offset = f.tell()
            # text
            f.seek(current_text_offset)
            f.write(encoded_text + b'x\01')
            current_bank_entries += number_of_pointers

        f.seek(0x22ddf2)
        print(bank_entries)
        for bank_entry in bank_entries:
            f.write(bank_entry.to_bytes(2, byteorder='little'))

def bof2_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = pathlib.Path(args.dump_path)
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    dump_path.mkdir()
    with open(source_file, 'rb') as f:
        # ITEMS
        with open(dump_path / 'items.csv', 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f.seek(0x70010)
            while f.tell() < 0x71000:
                text = f.read(16)
                text_decoded = table.decode(text)
                fields = [hex(f.tell()), text_decoded]
                csv_writer.writerow(fields)
        # LOCATIONS
        with open(dump_path / 'locations.csv', 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f.seek(0x55168)
            while f.tell() < 0x553e0:
                text = f.read(8)
                text_decoded = table.decode(text)
                fields = [hex(f.tell()), text_decoded]
                csv_writer.writerow(fields)

def bof2_gfx_dumper(args):
    source_file = args.source_file
    dump_path = args.dump_path
    dump_path = pathlib.Path(args.dump_path)
    with open(source_file, 'rb') as f:
        extract_binary(f, 0x176000, 0x179000 - 0x176000, dump_path / 'gfx_font.bin')

def bof2_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = pathlib.Path(args.translation_path)
    with open(dest_file, 'r+b') as f:
        insert_binary(f, 0x176000, translation_path / 'gfx_font.bin', max_length=0x179000 - 0x176000)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers()

    sub = subparsers.add_parser('dump_text', help='Dump dialogue strings to .txt and SQLite DB')
    sub.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Source ROM file')
    sub.add_argument('-t1', '--table1', action='store', dest='table1', help='Primary TBL file')
    sub.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Output directory for dump files')
    sub.add_argument('-db', '--database', action='store', dest='database_file', help='Path to the SQLite database')
    sub.set_defaults(func=bof2_text_dumper)

    sub = subparsers.add_parser('insert_text', help='Insert translated text into the destination ROM')
    sub.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Source ROM file')
    sub.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination ROM file')
    sub.add_argument('-t2', '--table2', action='store', dest='table2', help='Secondary TBL file')
    sub.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Directory containing translation files')
    sub.add_argument('-db', '--database', action='store', dest='database_file', help='Path to the SQLite database')
    sub.add_argument('-u', '--user', action='store', dest='user', help='Username to filter translations')
    sub.set_defaults(func=bof2_text_inserter)

    sub = subparsers.add_parser('dump_gfx', help='Extract graphics to a binary file')
    sub.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Source ROM file')
    sub.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Output directory for dump files')
    sub.set_defaults(func=bof2_gfx_dumper)

    sub = subparsers.add_parser('insert_gfx', help='Insert graphics into the destination ROM')
    sub.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination ROM file')
    sub.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Directory containing translation files')
    sub.set_defaults(func=bof2_gfx_inserter)

    sub = subparsers.add_parser('dump_misc', help='Dump miscellaneous texts to CSV files')
    sub.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Source ROM file')
    sub.add_argument('-t1', '--table1', action='store', dest='table1', help='Primary TBL file')
    sub.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Output directory for dump files')
    sub.set_defaults(func=bof2_misc_dumper)

    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
