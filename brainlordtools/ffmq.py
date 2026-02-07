__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, shutil, csv

from rhtools3.Table import Table
from rhutils.dump import read_text, write_text, get_csv_translated_texts
from rhutils.snes import snes2pc_lorom, pc2snes_lorom

def ffmq_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f, open(source_file, 'rb') as f1:
        # Locations
        filename = os.path.join(dump_path, 'locations.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f.seek(0x63ED0)
            while f.tell() < 0x64120:
                text_address = f.tell()
                text = read_text(f, text_address, length=16)
                text_encoded = table.decode(text, mte_resolver=False, dict_resolver=False)
                fields = [hex(text_address), text_encoded]
                csv_writer.writerow(fields)
        # Items
        filename = os.path.join(dump_path, 'items.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f.seek(0x64120)
            while f.tell() < 0x64420:
                text_address = f.tell()
                text = read_text(f, text_address, length=12)
                text_encoded = table.decode(text, mte_resolver=False, dict_resolver=False)
                fields = [hex(text_address), text_encoded]
                csv_writer.writerow(fields)
        # Enemy Attacks
        filename = os.path.join(dump_path, 'enemy_attacks.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f.seek(0x64420)
            while f.tell() < 0x64BA0:
                text_address = f.tell()
                text = read_text(f, text_address, length=12)
                text_encoded = table.decode(text, mte_resolver=False, dict_resolver=False)
                fields = [hex(text_address), text_encoded]
                csv_writer.writerow(fields)
        # Enemy Names
        filename = os.path.join(dump_path, 'enemy_names.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f.seek(0x64BA0)
            while f.tell() < 0x650C0:
                text_address = f.tell()
                text = read_text(f, text_address, length=16)
                text_encoded = table.decode(text, mte_resolver=False, dict_resolver=False)
                fields = [hex(text_address), text_encoded]
                csv_writer.writerow(fields)
        # Statuses
        filename = os.path.join(dump_path, 'statuses.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f1.seek(0x19f6b)
            while f1.tell() < 0x19f82:
                text_address = snes2pc_lorom(struct.unpack('I', f1.read(3) + b'\x00')[0]) + 0x8000
                f.seek(text_address)
                text = read_text(f, text_address, end_byte=b'\x00')
                text_encoded = table.decode(text, mte_resolver=False, dict_resolver=False)
                fields = [hex(text_address), text_encoded]
                csv_writer.writerow(fields)

def ffmq_misc_inserter(args):
    dest_file = args.dest_file
    table1_file = args.table1
    table2_file = args.table2
    translation_path = args.translation_path
    table = Table(table1_file)
    table2 = Table(table2_file)
    with open(dest_file, 'r+b') as f, open(dest_file, 'r+b') as f1:
        # Locations
        translation_file = os.path.join(translation_path, 'locations.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        for _, (_, t_address, t_value) in enumerate(translated_texts):
            text = table.encode(t_value, mte_resolver=False, dict_resolver=False)
            if len(text) != 16:
                sys.exit(f'{t_value} exceeds {t_value} - {len(text)}')
            write_text(f, t_address, text, length=16)
        # Items
        translation_file = os.path.join(translation_path, 'items.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        for _, (_, t_address, t_value) in enumerate(translated_texts):
            text = table.encode(t_value, mte_resolver=False, dict_resolver=False)
            if len(text) != 12:
                sys.exit(f'{t_value} exceeds {t_value} - {len(text)}')
            write_text(f, t_address, text, length=12)
        # Enemy Attacks
        translation_file = os.path.join(translation_path, 'enemy_attacks.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        for _, (_, t_address, t_value) in enumerate(translated_texts):
            text = table.encode(t_value, mte_resolver=False, dict_resolver=False)
            if len(text) != 12:
                sys.exit(f'{t_value} exceeds {t_value} - {len(text)}')
            write_text(f, t_address, text, length=12)
        # Enemy Names
        translation_file = os.path.join(translation_path, 'enemy_names.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        for _, (_, t_address, t_value) in enumerate(translated_texts):
            text = table.encode(t_value, mte_resolver=False, dict_resolver=False)
            if len(text) != 16:
                sys.exit(f'{t_value} exceeds {t_value} - {len(text)}')
            write_text(f, t_address, text, length=16)
        # Statuses
        f1.seek(0x19f6b)
        f.seek(0x7ff00)
        translation_file = os.path.join(translation_path, 'statuses.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        for _, (_, _, t_value) in enumerate(translated_texts):
            text = table.encode(t_value, mte_resolver=False, dict_resolver=False)
            f1.write(struct.pack('i', pc2snes_lorom(f.tell()))[:-1])
            f.write(text + b'\x00')

import argparse
parser = argparse.ArgumentParser()
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
dump_misc_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMP')
dump_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_misc_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_misc_parser.set_defaults(func=ffmq_misc_dumper)
insert_misc_parser = subparsers.add_parser('insert_misc', help='Execute MISC INSERTER')
insert_misc_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
insert_misc_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_misc_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_misc_parser.set_defaults(func=ffmq_misc_inserter)
args = parser.parse_args()
args.func(args)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
