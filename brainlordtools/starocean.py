__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os, shutil
from rhutils.dump import dump_binary, insert_binary

def starocean_gfx_dumper(args):
    source_file = args.source_file
    dump_path = args.dump_path
    # if crc32(source_file) != CRC32:
    #     sys.exit('SOURCE ROM CHECKSUM FAILED!')
    shutil.rmtree(dump_path, ignore_errors=True)
    os.mkdir(dump_path)
    with open(source_file, 'rb') as f:
        dump_binary(f, 0x3f0000, 0x3f0000 + 3392, dump_path, '3F0000_font.bin')
        dump_binary(f, 0x3f0d40, 0x3f0d40 + (4 * 13) + 1, dump_path, '3F0d40_font_vwf.bin')

def starocean_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = args.translation_path
    with open(dest_file, 'r+b') as f:
        insert_binary(f, 0x3f0000, 0x3f0000 + 3392, translation_path, '3F0000_font_ita.bin')
        insert_binary(f, 0x3f0d40, 0x3f0d40 + (4 * 13) + 1, translation_path, '3F0d40_font_vwf.bin')

import argparse
parser = argparse.ArgumentParser()
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
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
