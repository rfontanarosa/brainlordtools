__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os, sqlite3
from brainlordtools.rhutils.db import select_translation_by_author

def export_user_translation(args):
  user_name = args.user_name
  destination_dump_path = args.destination
  db = args.database_file
  blocks = args.blocks
  #
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  #
  if os.path.isfile(destination_dump_path):
    os.remove(destination_dump_path)
  with open(destination_dump_path, 'a') as f:
    rows = select_translation_by_author(cur, user_name, blocks)
    for row in rows:
      _, _, text_decoded, _, _, translation, ref = row
      text = translation if translation else text_decoded
      f.write(ref)
      f.write('\r\n')
      f.write(text)
      f.write('\r\n')
      f.write('\r\n')
  #
  cur.close()
  conn.commit()
  conn.close()

import argparse
parser = argparse.ArgumentParser()
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
export_user_translation_parser = subparsers.add_parser('export_user_translation', help='Execute EXPORT')
export_user_translation_parser.add_argument('-u', '--user', action='store', dest='user_name', required=True, help='Username')
export_user_translation_parser.add_argument('-d', '--destination', action='store', dest='destination', required=True, help='Destination dump path')
export_user_translation_parser.add_argument('-db', '--database', action='store', dest='database_file', required=True, help='DB filename')
export_user_translation_parser.add_argument('-b', '--block',  action='store', dest='blocks', required=True, nargs='+', help='Block(s)')
export_user_translation_parser.set_defaults(func=export_user_translation)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.func:
        args.func(args)
    else:
        parser.print_help()


