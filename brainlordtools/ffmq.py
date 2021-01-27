import sys, os, struct, sqlite3, shutil, csv
from collections import OrderedDict

from rhtools.utils import crc32, int2hex
from rhtools.dump import read_text, write_text
from rhtools3.Table import Table

CRC32 = '2C52C792'

def get_csv_translated_texts(filename):
    translated_texts = OrderedDict()
    with open(filename, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            trans = row.get('trans') or row.get('text')
            text_address = int(row['text_address'], 16)
            translated_texts[text_address] = trans
    return translated_texts

def ffmq_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    if crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        # Locations
        filename = os.path.join(dump_path, 'locations.csv')
        with open(filename, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f.seek(0x63ED0)
            while f.tell() < 0x64120:
                text_address = f.tell()
                text = read_text(f, text_address, length=16)
                text_encoded = table.decode(text, mte_resolver=False, dict_resolver=False)
                fields = [int2hex(text_address), text_encoded]
                csv_writer.writerow(fields)
        # Items
        filename = os.path.join(dump_path, 'items.csv')
        with open(filename, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f.seek(0x64120)
            while f.tell() < 0x64420:
                text_address = f.tell()
                text = read_text(f, text_address, length=12)
                text_encoded = table.decode(text, mte_resolver=False, dict_resolver=False)
                fields = [int2hex(text_address), text_encoded]
                csv_writer.writerow(fields)
        # Enemy Attacks
        filename = os.path.join(dump_path, 'enemy_attacks.csv')
        with open(filename, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f.seek(0x64420)
            while f.tell() < 0x64BA0:
                text_address = f.tell()
                text = read_text(f, text_address, length=12)
                text_encoded = table.decode(text, mte_resolver=False, dict_resolver=False)
                fields = [int2hex(text_address), text_encoded]
                csv_writer.writerow(fields)
        # Enemy Names
        filename = os.path.join(dump_path, 'enemy_names.csv')
        with open(filename, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f.seek(0x64BA0)
            while f.tell() < 0x650C0:
                text_address = f.tell()
                text = read_text(f, text_address, length=16)
                text_encoded = table.decode(text, mte_resolver=False, dict_resolver=False)
                fields = [int2hex(text_address), text_encoded]
                csv_writer.writerow(fields)

def ffmq_misc_inserter(args):
    source_file = args.source_file
    dest_file = args.dest_file
    table1_file = args.table1
    table2_file = args.table2
    translation_path = args.translation_path
    if crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    table2 = Table(table2_file)
    with open(dest_file, 'r+b') as f:
        # Locations
        translation_file = os.path.join(translation_path, 'locations.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        for i, (t_address, t_value) in enumerate(translated_texts.items()):
            text = table.encode(t_value, mte_resolver=False, dict_resolver=False)
            if len(text) != 16:
                sys.exit("{} exceeds".format(t_value))
            write_text(f, t_address, text, length=16)
        # Items
        translation_file = os.path.join(translation_path, 'items.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        for i, (t_address, t_value) in enumerate(translated_texts.items()):
            text = table.encode(t_value, mte_resolver=False, dict_resolver=False)
            if len(text) != 12:
                sys.exit("{} exceeds".format(t_value))
            write_text(f, t_address, text, length=12)
        # Enemy Attacks
        translation_file = os.path.join(translation_path, 'enemy_attacks.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        for i, (t_address, t_value) in enumerate(translated_texts.items()):
            text = table.encode(t_value, mte_resolver=False, dict_resolver=False)
            if len(text) != 12:
                sys.exit("{} exceeds {} - {}".format(t_value, len(t_value), len(text)))
            write_text(f, t_address, text, length=12)
        # Enemy Names
        translation_file = os.path.join(translation_path, 'enemy_names.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        for i, (t_address, t_value) in enumerate(translated_texts.items()):
            text = table.encode(t_value, mte_resolver=False, dict_resolver=False)
            if len(text) != 16:
                sys.exit("{} exceeds".format(t_value))
            write_text(f, t_address, text, length=16)

import argparse
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
a_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMP')
a_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
a_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
a_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
a_parser.set_defaults(func=ffmq_misc_dumper)
b_parser = subparsers.add_parser('insert_misc', help='Execute MISC INSERTER')
b_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
b_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
b_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
b_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
b_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
b_parser.set_defaults(func=ffmq_misc_inserter)
args = parser.parse_args()
args.func(args)
