__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3, shutil
from collections import OrderedDict

from rhtools.utils import crc32
from rhtools.dump import read_text, dump_gfx, insert_gfx, write_byte
from rhtools.Snes import snes2pc_lorom, pc2snes_lorom
from rhtools3.Table import Table

# CRC32_ORIGINAL = '7F0DDCCF'
CRC32 = '5497DF2A'

POINTER_BLOCK1_START = 0x11010
POINTER_BLOCK1_END = POINTER_BLOCK1_LIMIT = 0x112ac

TEXT_BLOCK1_START = 0x100000
TEXT_BLOCK1_END = TEXT_BLOCK1_LIMIT = 0x1fffff

GFX_NEW_GAME_OFFSETS = (0x26200, 0x26800)
GFX_FONT_OFFSETS = (0x28000, 0x28980)
GFX_STATUS_OFFSETS = (0x1d680, 0x1dc80)

def neugier_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    db = args.database_file
    if crc32(source_file) != CRC32:
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
            paddress = f.tell()
            pvalue = f.read(3)
            taddress = snes2pc_lorom(struct.unpack('i', pvalue[1:] + bytes([pvalue[0]]) + b'\x00')[0])
            pointers.setdefault(taddress, []).append(paddress)
        # TEXT 1
        id = 1
        for i, (taddress, paddresses) in enumerate(pointers.items()):
            pointer_addresses = ';'.join(str(hex(x)) for x in paddresses)
            text = read_text(f, taddress, end_byte=b'\x00')
            text += b'\x00'
            text_decoded = table.decode(text)
            # dump - db
            text_binary = sqlite3.Binary(text)
            text_length = len(text_binary)
            cur.execute('insert or replace into texts values (?, ?, ?, ?, ?, ?, ?)', (id, text_binary, text_decoded, taddress, pointer_addresses, text_length, 1))
            # dump - txt
            filename = os.path.join(dump_path, 'dump_eng.txt')
            with open(filename, 'a+') as out:
                out.write(text_decoded)
            id += 1
        cur.close()
        conn.commit()
        conn.close()

def neugier_inserter(args):
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
        cur.execute("SELECT text, new_text, text_encoded, id, new_text2, address, pointer_address, size FROM texts AS t1 LEFT OUTER JOIN (SELECT * FROM trans WHERE trans.author='%s' AND trans.status = 2) AS t2 ON t1.id=t2.id_text WHERE t1.block = %d" % (user_name, 1))
        for row in cur:
            # INSERTER X
            id = row[3]
            original_text = row[2]
            new_text = row[4]
            text = new_text if new_text else original_text
            decoded_text = table.encode(text)
            new_text_address = f.tell()
            if new_text_address + len(decoded_text) > (TEXT_BLOCK1_LIMIT + 1):
                sys.exit('CRITICAL ERROR! ID {} - BLOCK {} - TEXT_BLOCK_LIMIT! {} > {} ({})'.format(id, 1, next_text_address + len(decoded_text), TEXT_BLOCK1_LIMIT, (TEXT_BLOCK1_LIMIT - next_text_address - len(decoded_text))))
            if new_text_address < TEXT_BLOCK1_START + 0x8000 and new_text_address + len(decoded_text) >= TEXT_BLOCK1_START + 0x8000:
                new_text_address = TEXT_BLOCK1_START + 0x8000
            f.seek(new_text_address)
            f.write(decoded_text)
            next_text_address = f.tell()
            # REPOINTER X
            pointer_addresses = row[6]
            if pointer_addresses:
                for pointer_address in pointer_addresses.split(';'):
                    if pointer_address:
                        pointer_address = int(pointer_address, 16)
                        f.seek(pointer_address)
                        pvalue = struct.pack('i', pc2snes_lorom(new_text_address))
                        f.write(bytes([pvalue[2]]) + pvalue[:2])
                        if pointer_address > (POINTER_BLOCK1_LIMIT + 1):
                            sys.exit('CRITICAL ERROR! ID {} - BLOCK {} - POINTER_BLOCK_LIMIT! {} > {} ({})'.format(id, 1, pointer_address, POINTER_BLOCK1_LIMIT, (POINTER_BLOCK1_LIMIT - pointer_address)))
            f.seek(next_text_address)
    cur.close()
    conn.close()

def neugier_gfx_dumper(args):
    source_file = args.source_file
    dump_path = args.dump_path
    # if crc32(source_file) != CRC32:
    #     sys.exit('SOURCE ROM CHECKSUM FAILED!')
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_gfx(f, GFX_NEW_GAME_OFFSETS[0], GFX_NEW_GAME_OFFSETS[1], dump_path, 'gfx_new_game.bin')
        dump_gfx(f, GFX_FONT_OFFSETS[0], GFX_FONT_OFFSETS[1], dump_path, 'gfx_font.bin')
        dump_gfx(f, GFX_STATUS_OFFSETS[0], GFX_STATUS_OFFSETS[1], dump_path, 'gfx_status.bin')

def neugier_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = args.translation_path
    with open(dest_file, 'r+b') as f:
        insert_gfx(f, GFX_NEW_GAME_OFFSETS[0], GFX_NEW_GAME_OFFSETS[1], translation_path, 'gfx_new_game.bin')
        insert_gfx(f, GFX_FONT_OFFSETS[0], GFX_FONT_OFFSETS[1], translation_path, 'gfx_font.bin')
        insert_gfx(f, GFX_STATUS_OFFSETS[0], GFX_STATUS_OFFSETS[1], translation_path, 'gfx_status.bin')
        # VWF
        write_byte(f, 0x110050, b'\x07')
        write_byte(f, 0x110051, b'\x07')
        write_byte(f, 0x110052, b'\x07')
        write_byte(f, 0x110053, b'\x04')
        write_byte(f, 0x110054, b'\x07')
        write_byte(f, 0x110055, b'\x08')
        write_byte(f, 0x110056, b'\x08')

import argparse
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
a_parser = subparsers.add_parser('dump', help='Execute DUMP')
a_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
a_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
a_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
a_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
a_parser.set_defaults(func=neugier_dumper)
b_parser = subparsers.add_parser('insert', help='Execute INSERTER')
b_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
b_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
b_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
b_parser.add_argument('-u', '--user', action='store', dest='user', help='')
b_parser.set_defaults(func=neugier_inserter)
c_parser = subparsers.add_parser('dump_gfx', help='Execute GFX DUMP')
c_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
c_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
c_parser.set_defaults(func=neugier_gfx_dumper)
d_parser = subparsers.add_parser('insert_gfx', help='Execute GFX INSERTER')
d_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
d_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
d_parser.set_defaults(func=neugier_gfx_inserter)
args = parser.parse_args()
args.func(args)
