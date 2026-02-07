__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import argparse
import os
import shutil
import sys
import zlib

from _config import CRC_TABLE

def copy_file(args):
    try:
        shutil.copy(args.source_file, args.dest_file)
        print(f"Successfully copied to {args.dest_file}")
    except Exception as e:
        print(f"Copy failed: {e}")
        sys.exit(1)

def crc_check(args):
    source_file = args.source_file
    game_id = args.game_id

    if game_id not in CRC_TABLE:
        print(f"Error: Game ID '{game_id}' not found in database.")
        return sys.exit(1)

    if not os.path.exists(source_file):
        print(f"Error: File '{source_file}' not found.")
        return sys.exit(1)

    expected = CRC_TABLE[game_id].upper()

    with open(source_file, 'rb') as f:
        calc_crc = format(zlib.crc32(f.read()) & 0xFFFFFFFF, '08X')

    if calc_crc != expected:
        print(f"[{game_id.upper()}] CHECKSUM FAILED!")
        print(f"Expected: {expected}, Got: {calc_crc}")
        return sys.exit(1)

    print(f"[{game_id.upper()}] Checksum Verified: {calc_crc} [OK]")
    return True
    return True

parser = argparse.ArgumentParser(description="Utilities")
parser.set_defaults(func=None)
subparsers = parser.add_subparsers(dest="command")
p_copy_file = subparsers.add_parser('copy_file', help='File COPY')
p_copy_file.add_argument('-s', '--source', dest='source_file', required=True, help='Path to the original file')
p_copy_file.add_argument('-d', '--dest', dest='dest_file', required=True, help='Path to the destination file')
p_copy_file.set_defaults(func=copy_file)
p_crc_check = subparsers.add_parser('crc_check', help='Check file CRC')
p_crc_check.add_argument('-s', '--source', dest='source_file', required=True, help='Path to the file file')
p_crc_check.add_argument('-g', '--game', dest='game_id', required=True, help='Game ID (e.g., som, ff6)')
p_crc_check.set_defaults(func=crc_check)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()
