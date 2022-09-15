__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

from rhtools.dump import insert_binary

def starocean_gfx_inserter(args):
    dest_file = args.dest_file
    translation_path = args.translation_path
    with open(dest_file, 'r+b') as f:
        insert_binary(f, 0x3f0000, 0x3f0000 + 3392, translation_path, '3F0000_font_ita.bin')

import argparse
parser = argparse.ArgumentParser()
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
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

