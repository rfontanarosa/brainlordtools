__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import pathlib
import shutil
import sqlite3
import struct

from rhutils.db import insert_text, select_translation_by_author
from rhutils.io import read_text
from rhutils.snes import pc2snes_hirom
from rhutils.table import Table

BLOCK_BANKS_OFFSETS = (0xC7D9, 0xC7EC)
BLOCK_POINTERS_OFFSET = (0xC7EC, 0xC812)

POINTER_TABLES_SIZES = (22, 22, 17, 37, 20, 21, 18, 17, 15, 115, 26, 3, 21, 30, 2, 4, 35, 1, 2)

def ignition_text_dumper(args):
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
    with open(source_file, 'rb') as f1, open(source_file, 'rb') as f2:
        current_id = 1
        block_pointers = []
        f1.seek(BLOCK_BANKS_OFFSETS[0])
        f2.seek(BLOCK_POINTERS_OFFSET[0])
        while f1.tell() < BLOCK_BANKS_OFFSETS[1]:
            p_offset1 = f1.tell()
            p_offset2 = f2.tell()
            p_value = struct.unpack('i', f2.read(2) + f1.read(1) + b'\x00')[0] & 0x3fffff
            block_pointers.append((p_value, p_offset1, p_offset2))
        #
        for block, block_pointer in enumerate(block_pointers, start=1):
            b_address = block_pointer[0]
            p_qty = POINTER_TABLES_SIZES[block -1]
            pointers = []
            f1.seek(b_address)
            for _ in range(0, p_qty):
                pointer_address = f1.tell()
                pointer_value = f1.read(2)
                text_address = struct.unpack('H', pointer_value)[0] + (b_address & 0xff0000)
                pointers.append((text_address, [pointer_address]))
            for index, (text_address, pointer_addresses) in enumerate(pointers):
                pointer_addresses_str = ';'.join(hex(x) for x in pointer_addresses)
                text = read_text(f1, text_address, end_byte=b'\xff', cmd_list={b'\xfc': 2}, append_end_byte=True)
                text_decoded = table.decode(text)
                ref = f'[ID={current_id} BLOCK={block} ORDER={index} START={hex(text_address)} POINTERS={pointer_addresses_str}]'
                filename = 'dump_eng.txt'
                # dump - db
                insert_text(cur, current_id, text_decoded, text_address, pointer_addresses_str, len(text), block, ref, 'default', filename, current_id)
                # dump - txt
                with open(dump_path / filename, 'a+', encoding='utf-8') as out:
                    out.write(f'{ref}\n{text_decoded}\n\n')
                current_id += 1
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
            _, _, text_decoded, _, _, translation, _, _, _ = row
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
    sub.set_defaults(func=ignition_text_dumper)

    sub = subparsers.add_parser('insert_text', help='Insert translated text into the destination ROM')
    sub.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Source ROM file')
    sub.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination ROM file')
    sub.add_argument('-t2', '--table2', action='store', dest='table2', help='Secondary TBL file')
    sub.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Directory containing translation files')
    sub.add_argument('-db', '--database', action='store', dest='database_file', help='Path to the SQLite database')
    sub.add_argument('-u', '--user', action='store', dest='user', help='Username to filter translations')
    sub.set_defaults(func=ignition_text_inserter)

    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
