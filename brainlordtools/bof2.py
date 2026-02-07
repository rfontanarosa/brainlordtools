__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv, os, shutil, sqlite3, struct, sys

from rhutils.db import insert_text
from rhutils.dump import dump_binary, insert_binary, read_text
from rhutils.table import Table

POINTERS_BLOCKS = (
    (0x22e000, 0x22e7a1, 0x290000),
    (0x22e7a2, 0x22ef29, 0x2a0000),
    (0x22ef2a, 0x22fadf, 0x2b0000),
    (0x22fae0, 0x22ffff, 0x2c0000)
)

def bof2_text_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    db = args.database_file
    table = Table(table1_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    shutil.rmtree(dump_path, ignore_errors=False)
    os.mkdir(dump_path)
    if os.path.isfile(os.path.join(dump_path, 'dump_eng.txt')):
        os.remove(os.path.join(dump_path, 'dump_eng.txt'))
    with open(source_file, 'rb') as f:
        id, id2 = 1, 0
        for i, block_pointer in enumerate(POINTERS_BLOCKS):
            start, end, offset = block_pointer
            # READ POINTERS BLOCK
            pointers = {}
            f.seek(start)
            while f.tell() < end:
                p_offset = f.tell()
                p_value = struct.unpack('H', f.read(2))[0] + offset
                pointers.setdefault(p_value, []).append(p_offset)
                # if len(pointers[p_value]) > 1 and pointers[p_value][-2] != pointers[p_value][-1] - 2:
                #     pass
            # READ TEXT BLOCK
            for _, (text_address, paddresses) in enumerate(pointers.items()):
                pointer_addresses = ';'.join(hex(x) for x in paddresses)
                text = read_text(f, text_address, end_byte=b'\x01', cmd_list={b'\x03': 1, b'\x07': 1, b'\x08': 1, b'\x09': 1, b'\x11': 1, b'\x12': 1, b'\x13': 1}, append_end_byte=True)
                text_decoded = table.decode(text)
                ref = f'[ID={id} ID2={id2} BLOCK={i} START={hex(text_address)} POINTERS={pointer_addresses}]'
                # dump - db
                insert_text(cur, id, text, text_decoded, text_address, pointer_addresses, i, ref)
                # dump - txt
                filename = os.path.join(dump_path, 'dump_eng.txt')
                with open(filename, 'a+', encoding='utf-8') as out:
                    out.write(f'{ref}\n{text_decoded}\n\n')
                id += 1
                id2 += len(paddresses)
    cur.close()
    conn.commit()
    conn.close()

def bof2_text_inserter(args):
    source_file = args.source_file
    dest_file = args.dest_file
    table2_file = args.table2
    translation_path = args.translation_path
    # db = args.database_file
    # user_name = args.user
    table = Table(table2_file)
    entries = []
    #
    translation_file = os.path.join(translation_path, 'dump_ita.txt')
    with open(translation_file, 'r', encoding='utf-8') as f:
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
            f.write(encoded_text)
            current_bank_entries += number_of_pointers

        f.seek(0x22ddf2)
        print(bank_entries)
        for bank_entry in bank_entries:
            f.write(bank_entry.to_bytes(2, byteorder='little'))

def bof2_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        # ITEMS
        filename = os.path.join(dump_path, 'items.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f.seek(0x70010)
            while f.tell() < 0x71000:
                text = f.read(16)
                text_decoded = table.decode(text)
                fields = [hex(f.tell()), text_decoded]
                csv_writer.writerow(fields)
        # LOCATIONS
        filename = os.path.join(dump_path, 'locations.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
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
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_binary(f, 0x176000, 0x179000 - 0x176000, os.path.join(dump_path, 'gfx_font.bin'))

def bof2_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = args.translation_path
    with open(dest_file, 'r+b') as f:
        insert_binary(f, 0x176000, os.path.join(translation_path, 'gfx_font.bin'), max_length=0x179000 - 0x176000)

import argparse
parser = argparse.ArgumentParser()
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
dump_text_parser = subparsers.add_parser('dump_text', help='Execute TEXT DUMP')
dump_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_text_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_text_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
dump_text_parser.set_defaults(func=bof2_text_dumper)
insert_text_parser = subparsers.add_parser('insert_text', help='Execute TEXT INSERTER')
insert_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_text_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_text_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_text_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
insert_text_parser.add_argument('-u', '--user', action='store', dest='user', help='')
insert_text_parser.set_defaults(func=bof2_text_inserter)
dump_gfx_parser = subparsers.add_parser('dump_gfx', help='Execute GFX DUMP')
dump_gfx_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_gfx_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_gfx_parser.set_defaults(func=bof2_gfx_dumper)
insert_gfx_parser = subparsers.add_parser('insert_gfx', help='Execute GFX INSERTER')
insert_gfx_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_gfx_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_gfx_parser.set_defaults(func=bof2_gfx_inserter)
dump_misc_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMP')
dump_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_misc_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_misc_parser.set_defaults(func=bof2_misc_dumper)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
