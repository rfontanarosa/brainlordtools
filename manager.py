__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import argparse

from brainlordtools.rhutils.actions import diff_dump

def handle_diff_dump(args):
    source1_dump_path = args.source1
    source2_dump_path = args.source2
    destination_dump_path = args.destination
    game = args.game
    diff_dump(source1_dump_path, source2_dump_path, destination_dump_path, game)

parser = argparse.ArgumentParser()
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
p_diff_dump = subparsers.add_parser('diff_dump', help='Generate a diff between two dump files')
p_diff_dump.add_argument('-s1', '--source1', action='store', dest='source1', required=True, help='Path to the 1st source .txt dump file')
p_diff_dump.add_argument('-s2', '--source2', action='store', dest='source2', required=True, help='Path to the 2nd source .txt dump file')
p_diff_dump.add_argument('-d', '--destination', action='store', dest='destination', required=True, help='Output path for the generated .txt dump')
p_diff_dump.add_argument('-g', '--game', action='store', dest='game', required=False, default='default', help='Optional: Game ID(s) to use for custom parsing logic')
p_diff_dump.set_defaults(func=handle_diff_dump)

if __name__ == "__main__":
  args = parser.parse_args()
  if args.func:
    args.func(args)
  else:
    parser.print_help()
