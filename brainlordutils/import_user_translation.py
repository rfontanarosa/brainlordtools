__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import argparse, re, sqlite3
from brainlordtools.rhutils.db import insert_translation, TranslationStatus

def import_user_translation(args):
  user_name = args.user_name
  source_dump_path = args.source
  db = args.database_file
  #
  with sqlite3.connect(db) as conn:
    conn.text_factory = str
    cur = conn.cursor()
    with open(source_dump_path, 'r') as f:
      current_id = None
      buffer = []
      for line in f:
        match = re.search(r"\[ID\s+(\d+)", line)
        if match:
          if current_id is not None and buffer:
            text_decoded = "".join(buffer).strip()
            insert_translation(cur, current_id, 'TEST', user_name, text_decoded, TranslationStatus.PARTIALLY, 60, '', '')
          current_id = match.group(1)
          buffer = []
        else:
          if current_id is not None:
              buffer.append(line)
        if current_id is not None and buffer:
            text_decoded = "".join(buffer).strip()
            insert_translation(cur, current_id, 'TEST', user_name, text_decoded, TranslationStatus.PARTIALLY, 60, '', '')
    cur.close()
    conn.commit()

parser = argparse.ArgumentParser()
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
p_import_user_translation = subparsers.add_parser('import_user_translation', help='Import translations from a dump file')
p_import_user_translation.add_argument('-u', '--user', action='store', dest='user_name', required=True, help='The author of the translation')
p_import_user_translation.add_argument('-s', '--source', action='store', dest='source', required=True, help='Path to the source .txt dump file')
p_import_user_translation.add_argument('-db', '--database', action='store', dest='database_file', required=True, help='Path to the SQLite database')
p_import_user_translation.set_defaults(func=import_user_translation)

if __name__ == "__main__":
  args = parser.parse_args()
  if args.func:
      args.func(args)
  else:
      parser.print_help()
