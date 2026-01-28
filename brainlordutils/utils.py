__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import argparse, re, sqlite3
from brainlordtools.rhutils.db import select_translation_by_author, insert_translation, TranslationStatus

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

def export_user_translation(args):
  user_name = args.user_name
  destination_dump_path = args.destination
  db = args.database_file
  blocks = args.blocks
  #
  with sqlite3.connect(db) as conn:
    conn.text_factory = str
    cur = conn.cursor()
    with open(destination_dump_path, 'w') as f:
      rows = select_translation_by_author(cur, user_name, blocks)
      for row in rows:
        _, _, text_decoded, _, _, translation, ref = row
        text = translation if translation else text_decoded
        f.write(f"{ref}\r\n{text}\r\n\r\n")
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
p_export_user_translation = subparsers.add_parser('export_user_translation', help='Export translations to a dump file')
p_export_user_translation.add_argument('-u', '--user', action='store', dest='user_name', required=True, help='The author whose translations you want to export')
p_export_user_translation.add_argument('-d', '--destination', action='store', dest='destination', required=True, help='Output path for the generated .txt dump')
p_export_user_translation.add_argument('-db', '--database', action='store', dest='database_file', required=True, help='Path to the SQLite database')
p_export_user_translation.add_argument('-b', '--blocks', action='store', dest='blocks', required=False, nargs='+', help='Optional: Filter by specific block IDs')
p_export_user_translation.set_defaults(func=export_user_translation)

if __name__ == "__main__":
  args = parser.parse_args()
  if args.func:
    args.func(args)
  else:
    parser.print_help()
