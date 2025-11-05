__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv, os, re, shutil, sqlite3, struct, sys

from rhutils.db import insert_text, select_translation_by_author, select_most_recent_translation
from rhutils.dump import read_text
from rhutils.rom import crc32, expand_rom
from rhutils.snes import pc2snes_hirom, snes2pc_hirom
from rhutils.table import Table

CRC32 = 'D0176B24'

BLOCK_POINTERS_OFFSET = (
    (0x90000, 0x90800),
    (0xa0000, 0xa0c02)
)

cmd_list = {b'\x20': 1, b'\x21': 1, b'\x22': 1, b'\x23': 1, b'\x24': 1, b'\x25': 1, b'\x26': 1, b'\x27': 1, b'\x28': 1, b'\x29': 1, b'\x2a': 1, b'\x2b': 1, b'\x2c': 1, b'\x2e': 1, b'\x2f': 1, b'\x30': 2, b'\x31': 2, b'\x32': 2, b'\x34': 2, b'\x36': 3, b'\x37': 3, b'\x38': 1, b'\x39': 3, b'\x40': 4, b'\x42': 2, b'\x49': 3, b'\x4a': 3, b'\x4b': 3, b'\x4c': 3, b'\x4d': 3, b'\x4e': 3, b'\x57': 1, b'\x59': 1, b'\x5a': 1, b'\x5b': 2}

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
    dump_path = args.dump_path
    db = args.database_file
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        # TEXT POINTERS
        id = 1
        for block, block_pointers in enumerate(BLOCK_POINTERS_OFFSET):
            pointers = {}
            f.seek(block_pointers[0])
            while f.tell() < block_pointers[1]:
                p_address = f.tell()
                p_value = f.read(2)
                text_address = struct.unpack('H', p_value)[0] + block_pointers[0]
                pointers.setdefault(text_address, []).append(p_address)
            # TEXT
            for _, (text_address, p_addresses) in enumerate(pointers.items()):
                pointer_addresses = ';'.join(str(hex(x)) for x in p_addresses)
                text = som_read_text(f, text_address, end_byte=b'\x00', cmd_list=cmd_list, append_end_byte=True)
                text_decoded = table.decode(text)
                ref = f'[ID {id} - EVENT {hex(id - 1)} - {hex(text_address)} - {pointer_addresses}]'
                # dump - db
                insert_text(cur, id, text, text_decoded, text_address, pointer_addresses, block + 1, ref)
                # dump - txt
                filename = os.path.join(dump_path, 'dump_eng.txt')
                with open(filename, 'a+') as out:
                    out.write(ref + '\n' + text_decoded + "\n\n")
                id += 1
    cur.close()
    conn.commit()
    conn.close()


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

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
