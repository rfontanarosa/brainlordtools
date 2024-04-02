__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, struct, sqlite3, shutil, csv

from rhtools3.Table import Table
from rhutils.db import insert_text, select_translation_by_author, select_most_recent_translation
from rhutils.dump import read_text, write_text, dump_binary, insert_binary
from rhutils.rom import crc32
from rhutils.snes import snes2pc_lorom, pc2snes_lorom

# ORIGINAL
# CRC32 = 'B3ABDDE6'

# UNPACKED GFX
CRC32 = '21AFD8C7'

TEXT_BLOCK1 = (0x60000, 0x6fdde)
TEXT_BLOCK2 = (0x70000, 0x733c1)
TEXT_BLOCK3 = (0x741f7, 0x75343)

MISC_BLOCK1 = (0x733c2, 0x741f6)
MISC_BLOCK2 = (0x75345, 0x7545f)

POINTER_BLOCKS = [(0x425db, 0x4269b)]

FONT1_BLOCK = (0x13722d, 0x13B22d)

def seventhsaga_bank_dumper(f, dump_path, table, id, block, cur, start=0x0, end=0x0):
    f.seek(start)
    while f.tell() < end:
        text_address = f.tell()
        text = read_text(f, text_address, end_byte=b'\xf7', cmd_list={b'\xfc': 5})
        text_decoded = table.decode(text, mte_resolver=True, dict_resolver=False, cmd_list={0xf6: 1, 0xfb: 5, 0xfc: 5, 0xfd: 2, 0xfe: 2, 0xff: 3})
        ref = '[BLOCK {}: {} to {}]'.format(str(id), hex(text_address), hex(f.tell()))
        # dump - db
        insert_text(cur, id, text, text_decoded, text_address, '', block, '')
        # dump - txt
        filename = os.path.join(dump_path, 'dump_eng.txt')
        with open(filename, 'a+') as out:
            out.write(ref + '\n' + text_decoded + "\n\n")
        id += 1
    return id

def dump_blocks(f, table, dump_path):
    filename = os.path.join(dump_path, 'misc1.csv')
    with open(filename, 'w+') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['text_address', 'text', 'trans'])
        f.seek(MISC_BLOCK1[0])
        while f.tell() <= MISC_BLOCK1[1]:
            text_address = f.tell()
            text = read_text(f, text_address, end_byte=b'\xf7')
            text_decoded = table.decode(text, mte_resolver=False, dict_resolver=False)
            fields = [hex(text_address), text_decoded]
            csv_writer.writerow(fields)
    filename = os.path.join(dump_path, 'misc2.csv')
    with open(filename, 'w+') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['text_address', 'text', 'trans'])
        f.seek(MISC_BLOCK2[0])
        while f.tell() <= MISC_BLOCK2[1]:
            text_address = f.tell()
            text = read_text(f, text_address, end_byte=b'\xf7')
            text_decoded = table.decode(text, mte_resolver=False, dict_resolver=False)
            fields = [hex(text_address), text_decoded]
            csv_writer.writerow(fields)

def seventhsaga_text_dumper(args):
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
        id = 1
        id = seventhsaga_bank_dumper(f, dump_path, table, id, 1, cur, TEXT_BLOCK1[0], TEXT_BLOCK1[1])
        id = seventhsaga_bank_dumper(f, dump_path, table, id, 2, cur, TEXT_BLOCK2[0], TEXT_BLOCK2[1])
        id = seventhsaga_bank_dumper(f, dump_path, table, id, 3, cur, TEXT_BLOCK3[0], TEXT_BLOCK3[1])
    cur.close()
    conn.commit()
    conn.close()

def seventhsaga_text_inserter(args):
    source_file = args.source_file
    dest_file = args.dest_file
    table2_file = args.table2
    translation_path = args.translation_path
    db = args.database_file
    user_name = args.user
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table2_file)
    conn = sqlite3.connect(db)
    conn.text_factory = str
    cur = conn.cursor()
    # find pointers
    NEW_TEXT_BLOCK1_START = NEW_TEXT_BLOCK1_END = 0x300000
    new_pointers = {}
    with open(dest_file, 'r+b') as fw:
        fw.seek(NEW_TEXT_BLOCK1_START)
        # db
        rows = select_most_recent_translation(cur, ['1', '2', '3', '4', '5', '6', '7'])
        for row in rows:
            id, _, text_decoded, address, _, translation, _, _, _ = row
            text = translation if translation else text_decoded
            if id == 66:
                print(text)
            encoded_text = table.encode(text, mte_resolver=True, dict_resolver=False)
            if fw.tell() < 0x310000 and fw.tell() + len(encoded_text) > 0x30ffff:
                fw.seek(0x310000)
            new_pointers[int(address)] = fw.tell()
            fw.write(encoded_text)
            fw.write(b'\xf7')
        NEW_TEXT_BLOCK1_END = fw.tell()
    # pointer block 1
    with open(dest_file, 'r+b') as fw:
        fw.seek(POINTER_BLOCKS[0][0])
        while (fw.tell() < POINTER_BLOCKS[0][1]):
            repoint_text(fw, fw.tell(), new_pointers)
    # text block pointers
    with open(dest_file, 'r+b') as fw:
        fw.seek(NEW_TEXT_BLOCK1_START)
        while (fw.tell() < NEW_TEXT_BLOCK1_END):
            byte = fw.read(1)
            if byte in (b'\xfb', b'\xfc'):
                fw.read(2)
                repoint_text(fw, fw.tell(), new_pointers)
            elif byte == b'\xff':
                repoint_text(fw, fw.tell(), new_pointers)
    cur.close()
    conn.commit()
    conn.close()

def seventhsaga_gfx_dumper(args):
    source_file = args.source_file
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_binary(f, FONT1_BLOCK[0], FONT1_BLOCK[1], dump_path, 'gfx_font1.bin')

def seventhsaga_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = args.translation_path
    with open(dest_file, 'r+b') as f:
        insert_binary(f, FONT1_BLOCK[0], FONT1_BLOCK[1], translation_path, 'gfx_font1.bin')

def seventhsaga_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_blocks(f, table, dump_path)

def repoint_text(fw, offset, new_pointers):
    fw.seek(offset)
    pointer = fw.read(3)
    unpacked = struct.unpack('i', pointer + b'\x00')[0] - 0xc00000
    new_pointer = new_pointers.get(unpacked)
    if new_pointer:
        fw.seek(-3, os.SEEK_CUR)
        packed = struct.pack('i', new_pointer + 0xc00000)
        fw.write(packed[:-1])
    else:
        if unpacked == 0x173419:
            fw.seek(-3, os.SEEK_CUR)
            packed = struct.pack('i', fw.tell() + 3 + 0xc00000)
            fw.write(packed[:-1])
        else:
            print('TEXT - Pointer offset: ' + hex(offset) + ' Text offset: ' + hex(unpacked))

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--no_crc32_check', action='store_true', dest='no_crc32_check', required=False, default=False, help='CRC32 Check')
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
dump_text_parser = subparsers.add_parser('dump_text', help='Execute TEXT DUMP')
dump_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_text_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_text_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
dump_text_parser.set_defaults(func=seventhsaga_text_dumper)
insert_text_parser = subparsers.add_parser('insert_text', help='Execute TEXT INSERTER')
insert_text_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
insert_text_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_text_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
insert_text_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_text_parser.add_argument('-db', '--database', action='store', dest='database_file', help='DB filename')
insert_text_parser.add_argument('-u', '--user', action='store', dest='user', help='')
insert_text_parser.set_defaults(func=seventhsaga_text_inserter)
dump_gfx_parser = subparsers.add_parser('dump_gfx', help='Execute GFX DUMP')
dump_gfx_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_gfx_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_gfx_parser.set_defaults(func=seventhsaga_gfx_dumper)
insert_gfx_parser = subparsers.add_parser('insert_gfx', help='Execute GFX INSERTER')
insert_gfx_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
insert_gfx_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
insert_gfx_parser.set_defaults(func=seventhsaga_gfx_inserter)
dump_misc_parser = subparsers.add_parser('dump_misc', help='Execute MISC DUMP')
dump_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
dump_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
dump_misc_parser.add_argument('-dp', '--dump_path', action='store', dest='dump_path', help='Dump path')
dump_misc_parser.set_defaults(func=seventhsaga_misc_dumper)
# insert_misc_parser = subparsers.add_parser('insert_misc', help='Execute MISC INSERTER')
# insert_misc_parser.add_argument('-s', '--source', action='store', dest='source_file', required=True, help='Original filename')
# insert_misc_parser.add_argument('-d', '--dest', action='store', dest='dest_file', required=True, help='Destination filename')
# insert_misc_parser.add_argument('-t1', '--table1', action='store', dest='table1', help='Original table filename')
# insert_misc_parser.add_argument('-t2', '--table2', action='store', dest='table2', help='Modified table filename')
# insert_misc_parser.add_argument('-tp', '--translation_path', action='store', dest='translation_path', help='Translation path')
# insert_misc_parser.set_defaults(func=brainlord_misc_inserter)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
