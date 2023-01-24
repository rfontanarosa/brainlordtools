__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv, os, shutil, sqlite3, struct, sys
from collections import OrderedDict

from rhtools3.Table import Table
from rhutils.db import insert_text, select_translation_by_author, select_most_recent_translation
from rhutils.dump import read_text, write_text, write_byte, dump_binary, insert_binary, get_csv_translated_texts
from rhutils.rom import crc32
from rhutils.snes import snes2pc_lorom, pc2snes_lorom

# CRC32_ORIGINAL = '7F0DDCCF'
CRC32 = '5497DF2A'

POINTER_BLOCK1_START = 0x11010
POINTER_BLOCK1_END = POINTER_BLOCK1_LIMIT = 0x112ac

TEXT_BLOCK1_START = 0x100000
TEXT_BLOCK1_END = TEXT_BLOCK1_LIMIT = 0x1fffff

GFX_NEW_GAME_OFFSETS = (0x1d6e0, 0x1d9e0)
GFX_TITLE = (0x1da00, 0x20000)
GFX_STATUS_OFFSETS = (0x26200, 0x26800)
GFX_FONT_OFFSETS = (0x28000, 0x28980)
GFX_INTRO_OFFSETS = (0x29200, 0x2a800)

def neugier_text_dumper(args):
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
        # TEXT POINTERS 1
        pointers = OrderedDict()
        f.seek(POINTER_BLOCK1_START)
        while f.tell() < POINTER_BLOCK1_END:
            p_address = f.tell()
            p_value = f.read(3)
            text_address = snes2pc_lorom(struct.unpack('i', p_value[1:] + bytes([p_value[0]]) + b'\x00')[0])
            pointers.setdefault(text_address, []).append(p_address)
        # TEXT 1
        id = 1
        for i, (text_address, p_addresses) in enumerate(pointers.items()):
            pointer_addresses = ';'.join(str(hex(x)) for x in p_addresses)
            text = read_text(f, text_address, end_byte=b'\x00')
            text_decoded = table.decode(text)
            ref = f'[BLOCK {id}: {hex(text_address)} to {hex(f.tell() -1)}]'
            # dump - db
            insert_text(cur, id, text, text_decoded, text_address, pointer_addresses, 1, ref)
            # dump - txt
            filename = os.path.join(dump_path, 'dump_eng.txt')
            with open(filename, 'a+', encoding='utf-8') as out:
                out.write(f'{ref}\n{text_decoded}\n\n')
            id += 1
    cur.close()
    conn.commit()
    conn.close()

def neugier_text_inserter(args):
    dest_file = args.dest_file
    table2_file = args.table2
    db = args.database_file
    user_name = args.user
    table = Table(table2_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    with open(dest_file, 'r+b') as f:
        # TEXT
        f.seek(TEXT_BLOCK1_START)
        rows = select_translation_by_author(cur, user_name, ['1'])
        for row in rows:
            # INSERTER X
            id = row[0]
            address = row[3]
            text_decoded = row[2]
            translation = row[5]
            text = translation if translation else text_decoded
            text_encoded = table.encode(text)
            new_text_address = f.tell()
            if new_text_address + len(text_encoded) > (TEXT_BLOCK1_LIMIT + 1):
                sys.exit('CRITICAL ERROR! ID {} - BLOCK {} - TEXT_BLOCK_LIMIT! {} > {} ({})'.format(id, 1, next_text_address + len(decoded_text), TEXT_BLOCK1_LIMIT, (TEXT_BLOCK1_LIMIT - next_text_address - len(decoded_text))))
            if new_text_address < TEXT_BLOCK1_START + 0x8000 and new_text_address + len(text_encoded) >= TEXT_BLOCK1_START + 0x8000:
                new_text_address = TEXT_BLOCK1_START + 0x8000
            f.seek(new_text_address)
            f.write(text_encoded)
            f.write(b'\x00')
            next_text_address = f.tell()
            # REPOINTER X
            pointer_addresses = row[4]
            if pointer_addresses:
                pvalue = struct.pack('i', pc2snes_lorom(new_text_address))
                for pointer_address in pointer_addresses.split(';'):
                    if pointer_address:
                        pointer_address = int(pointer_address, 16)
                        f.seek(pointer_address)
                        f.write(bytes([pvalue[2]]) + pvalue[:2])
                        if pointer_address > (POINTER_BLOCK1_LIMIT + 1):
                            sys.exit('CRITICAL ERROR! ID {} - BLOCK {} - POINTER_BLOCK_LIMIT! {} > {} ({})'.format(id, 1, pointer_address, POINTER_BLOCK1_LIMIT, (POINTER_BLOCK1_LIMIT - pointer_address)))
            f.seek(next_text_address)
    cur.close()
    conn.close()

def neugier_gfx_dumper(args):
    source_file = args.source_file
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_binary(f, GFX_NEW_GAME_OFFSETS[0], GFX_NEW_GAME_OFFSETS[1], dump_path, 'gfx_new_game.bin')
        dump_binary(f, GFX_TITLE[0], GFX_TITLE[1], dump_path, 'gfx_title.bin')
        dump_binary(f, GFX_STATUS_OFFSETS[0], GFX_STATUS_OFFSETS[1], dump_path, 'gfx_status.bin')
        dump_binary(f, GFX_FONT_OFFSETS[0], GFX_FONT_OFFSETS[1], dump_path, 'gfx_font.bin')
        dump_binary(f, GFX_INTRO_OFFSETS[0], GFX_INTRO_OFFSETS[1], dump_path, 'gfx_intro.bin')

def neugier_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = args.translation_path
    with open(dest_file, 'r+b') as f:
        insert_binary(f, GFX_NEW_GAME_OFFSETS[0], GFX_NEW_GAME_OFFSETS[1], translation_path, 'gfx_new_game.bin')
        insert_binary(f, GFX_TITLE[0], GFX_TITLE[1], translation_path, 'gfx_title.bin')
        insert_binary(f, GFX_STATUS_OFFSETS[0], GFX_STATUS_OFFSETS[1], translation_path, 'gfx_status.bin')
        insert_binary(f, GFX_FONT_OFFSETS[0], GFX_FONT_OFFSETS[1], translation_path, 'gfx_font.bin')
        insert_binary(f, GFX_INTRO_OFFSETS[0], GFX_INTRO_OFFSETS[1], translation_path, 'gfx_intro.bin')
        # VWF
        write_byte(f, 0x110050, b'\x07')
        write_byte(f, 0x110051, b'\x07')
        write_byte(f, 0x110052, b'\x07')
        write_byte(f, 0x110053, b'\x04')
        write_byte(f, 0x110054, b'\x07')
        write_byte(f, 0x110055, b'\x08')
        write_byte(f, 0x110056, b'\x08')

def neugier_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        # Enemy names
        filename = os.path.join(dump_path, 'enemy_names.csv')
        with open(filename, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            f.seek(0xc06d)
            while f.tell() < 0xc3e7:
                text_address = f.tell()
                text = read_text(f, text_address, end_byte=b'\x40')
                text_decoded = text.decode("utf-8")
                fields = [hex(text_address), text_decoded]
                csv_writer.writerow(fields)
        # Credits
        with open(source_file, 'rb') as f:
            dump_binary(f, 0xd0919, 0xd0f37, dump_path, 'credits.bin')

def neugier_misc_inserter(args):
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
        # Enemy names
        translation_file = os.path.join(translation_path, 'enemy_names.csv')
        translated_texts = get_csv_translated_texts(translation_file)
        for i, (t_address, t_value) in enumerate(translated_texts.items()):
            text = t_value.encode()
            if len(text) != 10:
                sys.exit("{} exceeds".format(t_value))
            write_text(f, t_address, text, length=10)
        # Credits
        insert_binary(f, 0xd0919, 0xd0f37, translation_path, 'credits.bin')

def neugier_credits_dumper(args):
    source_file = args.source_file
    table3_file = args.table3
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table3_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    filename = os.path.join(dump_path, 'credits.txt')
    with open(source_file, 'rb') as f:
        pointers = OrderedDict()
        f.seek(snes2pc_lorom(0x1aea74))
        while f.tell() < snes2pc_lorom(0x1aeaaa):
            p_address = f.tell()
            p_value = f.read(2)
            text_address = snes2pc_lorom(struct.unpack('H', p_value)[0] + 0x1a0000)
            pointers.setdefault(text_address, []).append(p_address)
        with open(filename, 'a+') as txt_file:
            for i, (text_address, p_addresses) in enumerate(pointers.items()):
                f.seek(text_address)
                number_of_lines = int.from_bytes(f.read(1), "little")
                txt_file.write(f'[{number_of_lines}]' + '\n')
                for i in range(number_of_lines):
                    text = read_text(f, f.tell() + 1, end_byte=b'\x00')
                    text_decoded = table.decode(text)
                    txt_file.write(text_decoded + '\n')

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--no_crc32_check', action='store_true', dest='no_crc32_check', required=False, default=False, help='CRC32 Check')
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
dump_text_parser = subparsers.add_parser('dump_text', help='Execute DUMP')
dump_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_text_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_text_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
dump_text_parser.set_defaults(func=neugier_text_dumper)
insert_text_parser = subparsers.add_parser('insert_text', help='Execute INSERTER')
insert_text_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_text_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
insert_text_parser.add_argument('-u', '--user', action='store', dest='user', help='')
insert_text_parser.set_defaults(func=neugier_text_inserter)
dump_gfx_parser = subparsers.add_parser('dump_gfx', help='Execute GFX DUMP')
dump_gfx_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_gfx_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_gfx_parser.set_defaults(func=neugier_gfx_dumper)
insert_gfx_parser = subparsers.add_parser('insert_gfx', help='Execute GFX INSERTER')
insert_gfx_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_gfx_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_gfx_parser.set_defaults(func=neugier_gfx_inserter)
dump_misc_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMP')
dump_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_misc_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_misc_parser.set_defaults(func=neugier_misc_dumper)
insert_misc_parser = subparsers.add_parser('insert_misc', help='Execute MISC INSERTER')
insert_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_misc_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
insert_misc_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_misc_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_misc_parser.set_defaults(func=neugier_misc_inserter)
dump_credits_parser = subparsers.add_parser('dump_credits', help='Execute CREDITS DUMP')
dump_credits_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_credits_parser.add_argument('-t3', '--table3', action='store', dest='table3', help='Credits table filename')
dump_credits_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_credits_parser.set_defaults(func=neugier_credits_dumper)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
