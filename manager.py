__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import argparse

from brainlordtools.utils.actions import copy_file, crc_check, diff_dump, expand_file

def handle_copy_file(args):
    source_file = args.source_file
    dest_file = args.dest_file
    copy_file(source_file, dest_file)

def handle_crc_check(args):
    source_file = args.source_file
    game = args.game_id
    crc_check(source_file, game)

def handle_diff_dump(args):
    source1_dump_path = args.source1
    source2_dump_path = args.source2
    destination_dump_path = args.destination
    game = args.game_id
    diff_dump(source1_dump_path, source2_dump_path, destination_dump_path, game)

def handle_expand_file(args):
    dest_file = args.dest_file
    game_id = args.game_id
    expand_file(dest_file, game_id)

parser = argparse.ArgumentParser()
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
p_copy_file = subparsers.add_parser('copy_file', help='File COPY')
p_copy_file.add_argument('-s', '--source', dest='source_file', required=True, help='Path to the original file to be copied')
p_copy_file.add_argument('-d', '--dest', dest='dest_file', required=True, help='Path to the destination file where the copy will be saved')
p_copy_file.set_defaults(func=handle_copy_file)
p_crc_check = subparsers.add_parser('crc_check', help='Check file CRC')
p_crc_check.add_argument('-s', '--source', dest='source_file', required=True, help='Path to the file to be checked')
p_crc_check.add_argument('-g', '--game', dest='game_id', required=True, help='Game ID (e.g., som, ff6)')
p_crc_check.set_defaults(func=handle_crc_check)
p_diff_dump = subparsers.add_parser('diff_dump', help='Generate a diff between two dump files')
p_diff_dump.add_argument('-s1', '--source1', action='store', dest='source1', required=True, help='Path to the 1st source .txt dump file')
p_diff_dump.add_argument('-s2', '--source2', action='store', dest='source2', required=True, help='Path to the 2nd source .txt dump file')
p_diff_dump.add_argument('-d', '--destination', action='store', dest='destination', required=True, help='Path to the generated .txt dump')
p_diff_dump.add_argument('-g', '--game', action='store', dest='game_id', required=False, default='default', help='Optional: Game ID (e.g., som, ff6) to use for custom parsing logic')
p_diff_dump.set_defaults(func=handle_diff_dump)
p_expand = subparsers.add_parser('expand')
p_expand.add_argument('-d', '--dest', dest='dest_file', required=True, help="Path to the destination file to be expanded")
p_expand.add_argument('-g', '--game', dest='game_id', required=True, help="Game ID (e.g., som, ff6)")
p_expand.set_defaults(func=handle_expand_file)

if __name__ == "__main__":
  args = parser.parse_args()
  if args.func:
    args.func(args)
  else:
    parser.print_help()
