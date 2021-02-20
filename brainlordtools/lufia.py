__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, shutil, csv
from collections import OrderedDict

from rhtools.utils import crc32
from rhtools.dump import read_text, write_text, dump_binary, insert_binary
from rhtools3.Table import Table

CRC32 = '5E1AA1A6'

def encode_text(text):
    return text

def lufia_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    # if crc32(source_file) != CRC32:
    #     sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    offsets = (119959, 120098)
    with open(source_file, 'rb') as f:
        for offset in offsets:
            offset = offset - 0x200
            text = read_text(f, offset, end_byte=b'\00', cmd_list=({b'\x1e': 8, b'\x07': 1, b'\x08': 1, b'\x09': 1, b'\x0a': 1, b'\x0b': 1, b'\x0c': 1, b'\x0d': 1}))
            text = text.split(b'\04', 1)
            text_decoded = table.decode(text[0], mte_resolver=True, dict_resolver=True)
            text_decoded += table.decode(text[1], eol_resolver=False, mte_resolver=False, dict_resolver=False)
            print(hex(offset))
            print(text_decoded)

def lufia_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    # if crc32(source_file) != CRC32:
    #     sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        # Items
        filename = os.path.join(dump_path, 'items.csv')
        with open(filename, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            pointers = OrderedDict()
            f.seek(0x55800)
            while f.tell() < 0x559ff:
                pointers[f.tell()] = struct.unpack('H', f.read(2))[0] + 0x55800
            for key, value in pointers.items():
                f.seek(value)
                text = f.read(12)
                text_decoded = table.decode(text, mte_resolver=False, dict_resolver=False)
                fields = [hex(value), text_decoded]
                csv_writer.writerow(fields)
        # Enemy names
        filename = os.path.join(dump_path, 'enemy_names.csv')
        with open(filename, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            pointers = OrderedDict()
            f.seek(0x5800)
            while f.tell() < 0x5949:
                pointers[f.tell()] = struct.unpack('H', f.read(2))[0] + 0x5800
            for key, value in pointers.items():
                f.seek(value)
                text = f.read(10)
                text_decoded = table.decode(text, mte_resolver=False, dict_resolver=False)
                fields = [hex(value), text_decoded]
                csv_writer.writerow(fields)
        # Magic
        filename = os.path.join(dump_path, 'magic.csv')
        with open(filename, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            pointers = OrderedDict()
            f.seek(0xfdb00)
            while f.tell() < 0xfdb6f:
                pointers[f.tell()] = struct.unpack('H', f.read(2))[0] + 0xfdb00
            for key, value in pointers.items():
                f.seek(value)
                text = f.read(8)
                text_decoded = table.decode(text, mte_resolver=False, dict_resolver=False)
                fields = [hex(value), text_decoded]
                csv_writer.writerow(fields)
        # Magic descriptions
        filename = os.path.join(dump_path, 'magic_descriptions.csv')
        with open(filename, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            pointers = OrderedDict()
            f.seek(0xfdb00)
            while f.tell() < 0xfdb6f:
                text_address = struct.unpack('H', f.read(2))[0] + 0xfdb00
                f1.seek(text_address + 15)
                pointers[f1.tell()] = struct.unpack('H', f1.read(2))[0] + 0xfdb00
            for key, value in pointers.items():
                text = read_text(f, value, end_byte=b'\00')
                text_decoded = table.decode(text, mte_resolver=False, dict_resolver=False)
                fields = [hex(value), text_decoded]
                print(value)
                csv_writer.writerow(fields)

import argparse
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
a_parser = subparsers.add_parser('dump_text', help='Execute DUMP')
a_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
a_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
a_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
a_parser.set_defaults(func=lufia_dumper)
e_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMP')
e_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
e_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
e_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
e_parser.set_defaults(func=lufia_misc_dumper)
args = parser.parse_args()
args.func(args)
