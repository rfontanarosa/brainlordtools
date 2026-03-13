__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv
import os
import pathlib
import shutil
import struct
import sys

from _equinox.decompress import EquinoxDecompressor
from rhutils.dump import get_csv_translated_texts
from rhutils.snes import pc2snes_lorom, snes2pc_lorom
from rhutils.table import Table

def equinox_read_text(f, offset=None, length=None, end_byte=None, cmd_list=None, append_end_byte=False):
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
            elif byte in end_byte and len(text) != 0:
                if append_end_byte:
                    text += byte
                break
            else:
                text += byte
    return text

def equinox_gfx_dumper(args):
    source_file = args.source_file
    dump_path = pathlib.Path(args.dump_path)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        rom = f.read()
        data = (
            ('gfx_intro.bin', 0x73169, 0x23BA),
            ('gfx_font.bin',  0x75523, 0x0552),
            ('gfx_font2.bin', 0x7A695, 0x07CE),
        )
        for (filename, ds_start, ds_size) in data:
            decomp = EquinoxDecompressor(rom, ds_start, ds_size)
            result = decomp.decompress()
            with open(dump_path / filename, "wb") as f:
                f.write(result)

def equinox_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        # get pointers 1
        pointers = {}
        for p_offset in [*range(0x4f4c, 0x4f6e + 1, 2), 0xc040]:
            f.seek(p_offset)
            raw = bytearray(f.read(2))
            raw = int.from_bytes(raw, byteorder='little')
            p_value = snes2pc_lorom(raw)
            pointers.setdefault(p_value, []).append(p_offset)
        # reading texts
        filename = os.path.join(dump_path, f'intro.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['pointer_address', 'text_address', 'text', 'trans'])
            for _, (text_address, pointer_addresses) in enumerate(sorted(pointers.items())):
                text = equinox_read_text(f, text_address, end_byte=b'\xff')
                text_decoded = table.decode(text)
                fields = [';'.join(hex(x) for x in pointer_addresses), hex(text_address), text_decoded]
                csv_writer.writerow(fields)
        # get pointers 2
        pointers = {}
        for p_offset in [0x501f1, 0x501d1, 0x5020e, 0x50237, 0x50251, 0x50283, 0x502c1, 0x502e7, 0x50307, 0x50316, 0x50323, 0x50330, 0x5033d, 0x5034a, 0x50357, 0x50364, 0x50371, 0x5037e, 0x5038b, 0x50398, 0x503a5, 0x503b2, 0x503c0, 0x503ce, 0x503db, 0x503e8, 0x503f6, 0x50404, 0x50411, 0x5041e, 0x5042b, 0x5070f, 0x5074f] +\
            [0x50726, 0x50732, 0x50748, 0x50a13, 0x5d2c1] +\
            [0x5146a, 0x5099a, 0x509eb, 0x50202, 0x5022b, 0x502cf, 0x502e7, 0x50245, 0x5025f, 0x50291, 0x5026b, 0x5029d, 0x502db, 0x502b5, 0x5020e, 0x5073e, 0x50411, 0x5041e]:
            f.seek(p_offset)
            raw = bytearray(f.read(2))
            raw = int.from_bytes(raw, byteorder='little')
            p_value = snes2pc_lorom(raw) + 0x50000
            pointers.setdefault(p_value, []).append(p_offset)
        # reading texts
        filename = os.path.join(dump_path, f'misc.csv')
        with open(filename, 'w+', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['pointer_address', 'text_address', 'text', 'trans'])
            for _, (text_address, pointer_addresses) in enumerate(sorted(pointers.items())):
                text = equinox_read_text(f, text_address, end_byte=b'\xff')
                text_decoded = table.decode(text)
                fields = [';'.join(hex(x) for x in pointer_addresses), hex(text_address), text_decoded]
                csv_writer.writerow(fields)

def equinox_misc_inserter(args):
    dest_file = args.dest_file
    table1_file = args.table1
    translation_path = pathlib.Path(args.translation_path)
    table = Table(table1_file)
    with open(dest_file, 'r+b') as f1, open(dest_file, 'r+b') as f2:
        # intro
        filepath = translation_path / 'intro.csv'
        translated_texts = get_csv_translated_texts(filepath)
        # misc
        filepath = translation_path / 'misc.csv'
        translated_texts = get_csv_translated_texts(filepath)
        f1.seek(0x108_000)
        for _, (pointer_addresses, _, _, translated_text) in enumerate(translated_texts):
            # pointer
            snes_offset = pc2snes_lorom(f1.tell())
            new_pointer_value = struct.pack('<I', snes_offset)[:2]
            for pointer_address in pointer_addresses:
                f2.seek(pointer_address)
                f2.write(new_pointer_value)
            # text
            encoded_text = table.encode(translated_text)
            f1.write(encoded_text + b'\xff')
            if f1.tell() > 0x108_000 + 0x8000:
                sys.exit('Text size exceeds!')

import argparse
parser = argparse.ArgumentParser()
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
dump_gfx_parser = subparsers.add_parser('dump_gfx', help='Execute GFX DUMP')
dump_gfx_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_gfx_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_gfx_parser.set_defaults(func=equinox_gfx_dumper)
dump_misc_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMP')
dump_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_misc_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_misc_parser.set_defaults(func=equinox_misc_dumper)
insert_misc_parser = subparsers.add_parser('insert_misc', help='Execute MISC INSERTER')
insert_misc_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
insert_misc_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Menu table filename')
insert_misc_parser.add_argument('-t3', '--table3', action='store', dest='table3', help='Intro table filename')
insert_misc_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_misc_parser.set_defaults(func=equinox_misc_inserter)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
