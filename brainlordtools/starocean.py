__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv, os, shutil, struct, sys

from rhutils.dump import dump_binary, insert_binary, get_csv_translated_texts, read_text
from rhutils.table import Table

def starocean_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f, open(source_file, 'rb') as f1:
        # Menu
        filename = os.path.join(dump_path, 'menu.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            pointers = {}
            f.seek(0x3f7a4c)
            while f.tell() < 0x3f7d3a:
                pointers[f.tell()] = struct.unpack('H', f.read(2))[0] + 0x3f802a
            for key, value in pointers.items():
                text = read_text(f1, value, end_byte=b'\xff')
                text_decoded = table.decode(text)
                fields = [hex(value), text_decoded]
                csv_writer.writerow(fields)
        # Items
        filename = os.path.join(dump_path, 'items.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            pointers = {}
            f.seek(0x3c959d)
            while f.tell() < 0x3c9c97:
                pointers[f.tell()] = struct.unpack('H', f.read(2))[0] + 0x3ca393
            for key, value in pointers.items():
                text = read_text(f1, value, end_byte=b'\xff')
                text_decoded = table.decode(text)
                fields = [hex(value), text_decoded]
                csv_writer.writerow(fields)

def starocean_misc_inserter(args):
    dest_file = args.dest_file
    table1_file = args.table1
    table2_file = args.table2
    translation_path = args.translation_path
    table = Table(table1_file)
    table2 = Table(table2_file)
    with open(dest_file, 'r+b') as f1, open(dest_file, 'r+b') as f2:
        # Menu
        f1.seek(0x3f802a)
        f2.seek(0x3f7a4c)
        translation_file = os.path.join(translation_path, 'menu.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        already_pointed = {}
        for i, (_, t_address, t_value) in enumerate(translated_texts):
            if not already_pointed.get(t_address):
                already_pointed[t_address] = f1.tell()
                encoded_text = table2.encode(t_value) + b'\xff'
                if f1.tell() + len(encoded_text) > 0x3f9433 and f1.tell() + len(encoded_text) < 0x3fa440:
                    f1.seek(0x3fa440)
                f1.write(encoded_text)
            pointer = struct.pack('H', (already_pointed.get(t_address, f1.tell()) - 0x802a) & 0x00FFFF)
            f2.write(pointer)
        if f1.tell() > 0x3fa4a0:
            print(f'Inserted text exceeds by {0x3f9433 - f1.tell()} bytes')
        # Items
        f1.seek(0x3ca393)
        f2.seek(0x3c959d)
        translation_file = os.path.join(translation_path, 'items.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        already_pointed = {}
        for i, (_, t_address, t_value) in enumerate(translated_texts):
            if not already_pointed.get(t_address):
                already_pointed[t_address] = f1.tell()
                encoded_text = table2.encode(t_value) + b'\xff'
                f1.write(encoded_text)
            pointer = struct.pack('H', (already_pointed.get(t_address, f1.tell()) - 0xa393) & 0x00FFFF)
            f2.write(pointer)
        if f1.tell() > 0x3cc48b:
            print(f'Inserted text exceeds by {f1.tell() - 0x3cc48b} bytes')

def starocean_gfx_dumper(args):
    source_file = args.source_file
    dump_path = args.dump_path
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_binary(f, 0x3f0000, 3392, os.path.join(dump_path, '3F0000_font.bin'))
        dump_binary(f, 0x3f0d40, (4 * 13) + 1, os.path.join(dump_path, '3F0d40_font_vwf.bin'))
        dump_binary(f, 0xa0268, 16, os.path.join(dump_path, 'a0268_menu_hand_pointer.bin'))

def starocean_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = args.translation_path
    with open(dest_file, 'r+b') as f:
        insert_binary(f, 0x3f0000, os.path.join(translation_path, '3F0000_font_ita.bin'), max_length=3392)
        insert_binary(f, 0x3f0d40, os.path.join(translation_path, '3F0d40_font_vwf_ita.bin'), max_length=(4 * 13) + 1)
        insert_binary(f, 0xa0268, os.path.join(translation_path, 'a0268_menu_hand_pointer_ita.bin'), max_length=16)

import argparse
parser = argparse.ArgumentParser()
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
dump_misc_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMPER')
dump_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_misc_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_misc_parser.set_defaults(func=starocean_misc_dumper)
insert_misc_parser = subparsers.add_parser('insert_misc', help='Execute MISC INSERTER')
insert_misc_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
insert_misc_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_misc_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_misc_parser.set_defaults(func=starocean_misc_inserter)
dump_gfx_parser = subparsers.add_parser('dump_gfx', help='Execute GFX DUMP')
dump_gfx_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_gfx_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_gfx_parser.set_defaults(func=starocean_gfx_dumper)
insert_gfx_parser = subparsers.add_parser('insert_gfx', help='Execute GFX INSERTER')
insert_gfx_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_gfx_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_gfx_parser.set_defaults(func=starocean_gfx_inserter)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
