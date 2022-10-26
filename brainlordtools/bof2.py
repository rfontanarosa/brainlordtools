__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import csv, os, shutil, struct, sys
from collections import OrderedDict

from rhutils.dump import dump_binary, insert_binary, read_text
from rhutils.rom import crc32
from rhutils.table import Table

CRC32 = '67CDACC5'

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
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    # conn = sqlite3.connect(db)
    # conn.text_factory = str
    # cur = conn.cursor()
    shutil.rmtree(dump_path, ignore_errors=False)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        id = 1
        for i, block_pointer in enumerate(POINTERS_BLOCKS):
            start, end, offset = block_pointer
            # READ POINTERS BLOCK
            pointers = OrderedDict()
            f.seek(start)
            while (f.tell() < end):
                p_offset = f.tell()
                p_value = struct.unpack('H', f.read(2))[0] + offset
                pointers.setdefault(p_value, []).append(p_offset)
            # READ TEXT BLOCK
            for index, (taddress, paddresses) in enumerate(pointers.items()):
                pointer_addresses = ';'.join(hex(x) for x in paddresses)
                text = read_text(f, taddress, end_byte=b'\x01', cmd_list={b'\x03': 1, b'\x07': 1, b'\x08': 1, b'\x12': 1}, append_end_byte=True)
                text_decoded = table.decode(text)
                # dump - db
                # insert_text(cur, id, text, text_decoded, taddress, pointer_addresses, i, id)
                # dump - txt
                filename = os.path.join(dump_path, 'dump_eng.txt')
                with open(filename, 'a+') as out:
                    out.write('[ID {} - BLOCK {} - TEXT {} - POINTER {}]\n{}\n\n'.format(id, i, hex(taddress), pointer_addresses, text_decoded))
                id += 1
    # cur.close()
    # conn.commit()
    # conn.close()

def bof2_misc_dumper(args):
    source_file = args.source_file
    table1_file = args.table1
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    table = Table(table1_file)
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f, open(source_file, 'rb') as f1:
        filename = os.path.join(dump_path, 'items.csv')
        with open(filename, 'w+') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['text_address', 'text', 'trans'])
            pointers = OrderedDict()
            f.seek(0x70010)
            while f.tell() < 0x71000:
                text = f.read(16)
                text_decoded = table.decode(text)
                fields = [hex(f.tell()), text_decoded]
                csv_writer.writerow(fields)

def bof2_gfx_dumper(args):
    source_file = args.source_file
    dump_path = args.dump_path
    if not args.no_crc32_check and crc32(source_file) != CRC32:
        sys.exit('SOURCE ROM CHECKSUM FAILED!')
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_binary(f, 0x176000, 0x179000, dump_path, 'gfx_font.bin')

def bof2_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = args.translation_path
    with open(dest_file, 'r+b') as f:
        insert_binary(f, 0x176000, 0x179000, translation_path, 'gfx_font.bin')

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
dump_text_parser.set_defaults(func=bof2_text_dumper)
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