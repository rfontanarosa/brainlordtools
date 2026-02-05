__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import argparse, re, sqlite3, time
from brainlordtools.rhutils.db import select_most_recent_translation, select_texts, select_translation_by_author, insert_text, insert_translation, TranslationStatus

def _parse_metadata(text: str) -> dict:
  matches = re.findall(r'(\w+)=([^\s\]]+)', text)
  return dict(matches)

def _parse_dump(file_path: str) -> dict:
  buffer = {}
  with open(file_path, 'r', encoding='utf-8') as f:
    current_id = None
    for line in f:
      if line.startswith('[ID='):
        metadata = _parse_metadata(line)
        current_id = metadata.get('ID')
        if current_id is not None:
          buffer[current_id] = ['', line.strip()]
      elif current_id is not None:
        buffer[current_id][0] += line
  return buffer

def _parse_soe_dump(file_path: str) -> dict:
  buffer = {}
  with open(file_path, 'r', encoding='utf-8') as f:
    real_id = 1
    current_text = ""
    for line in f:
      if '<End>' in line:
        clean_text = current_text + line.replace('<End>', '')
        buffer[real_id] = [clean_text.strip(), ''] 
        real_id += 1
        current_text = ""
      else:
        current_text += line
  return buffer

def _parse_starocean_dump(file_path: str) -> dict:
  buff = {}
  with open(file_path, 'r', encoding='utf-8') as f:
    current_id = 0
    iterator = iter(f)
    for line in iterator:
      if line.startswith('<HEADER '):
        current_id += 1
        next_line = next(iterator)
        buff[current_id] = ['', line + next_line.strip('\r\n')]
      elif line.startswith('<BLOCK '):
        current_id += 1
        buff[current_id] = ['', line.strip('\r\n')]
      else:
        buff[current_id][0] += line
  return buff

GAME_PARSERS = {
  'soe': _parse_soe_dump,
  'starocean': _parse_starocean_dump,
  'default': _parse_dump
}

def import_dump(args) -> None:
  db = args.database_file
  source_dump_path = args.source
  game = args.game
  parse_dump_func = GAME_PARSERS.get(game, GAME_PARSERS['default'])
  with sqlite3.connect(db) as conn:
    conn.text_factory = str
    cur = conn.cursor()
    entries = parse_dump_func(source_dump_path)
    for incremental_id, (text, ref) in entries.items():
      should_parse = game not in {'evermore', 'starocean'} and ref != ''
      metadata = _parse_metadata(ref) if should_parse else {}
      current_id = metadata.get('ID') or incremental_id
      block = metadata.get('BLOCK', 1)
      text_decoded = text.strip('\r\n')
      insert_text(cur, current_id, b'', text_decoded, '', '', block, ref)

def import_translation(args) -> None:
  db = args.database_file
  source_dump_path = args.source
  user_name = args.user_name
  original_dump_path = args.original_dump
  game = args.game
  parse_dump_func = GAME_PARSERS.get(game, GAME_PARSERS['default'])
  with sqlite3.connect(db) as conn:
    conn.text_factory = str
    cur = conn.cursor()
    translation_dump = parse_dump_func(source_dump_path)
    original_dump = parse_dump_func(original_dump_path) if original_dump_path else None
    for current_id, (text, _) in translation_dump.items():
      if original_dump and original_dump.get(current_id, [None])[0] == text:
        continue
      text_decoded = text.rstrip('\r\n')
      insert_translation(cur, current_id, 'TEST', user_name, text_decoded, TranslationStatus.PARTIALLY, time.time(), '', '')

def export_translation(args) -> None:
  db = args.database_file
  destination_dump_path = args.destination
  user_name = args.user_name
  blocks = args.blocks
  #
  with sqlite3.connect(db) as conn:
    conn.text_factory = str
    cur = conn.cursor()
    with open(destination_dump_path, 'w') as f:
      if user_name:
        rows = select_translation_by_author(cur, user_name, blocks)
      else:
        rows = select_most_recent_translation(cur, blocks)
      for row in rows:
        _, _, text_decoded, _, _, translation, _, ref, _ = row
        text = translation if translation else text_decoded
        f.write(f"{ref}\r\n{text}\r\n\r\n")

def mark_empty_texts_as_translated(args) -> None:
  user_name = args.user_name
  db = args.database_file
  with sqlite3.connect(db) as conn:
    conn.text_factory = str
    read_cur = conn.cursor()
    write_curr = conn.cursor()
    rows = select_texts(read_cur)
    for row in rows:
      id, text_decoded = row
      clear_text = re.sub(r'\[.*?\]\n?', '', text_decoded)
      if clear_text == '':
        insert_translation(write_curr, id, 'TEST', user_name, text_decoded, TranslationStatus.DONE, 60, '', '')

parser = argparse.ArgumentParser()
parser.set_defaults(func=None)
subparsers = parser.add_subparsers()
p_import_dump = subparsers.add_parser('import_dump', help='Import dump from a dump file')
p_import_dump.add_argument('-db', '--database', action='store', dest='database_file', required=True, help='Path to the SQLite database')
p_import_dump.add_argument('-s', '--source', action='store', dest='source', required=True, help='Path to the source .txt dump file')
p_import_dump.add_argument('-g', '--game', action='store', dest='game', required=False, help='Optional: Game ID(s) to use for custom parsing logic')
p_import_dump.set_defaults(func=import_dump)
p_import_translation = subparsers.add_parser('import_translation', help='Import translations from a dump file')
p_import_translation.add_argument('-db', '--database', action='store', dest='database_file', required=True, help='Path to the SQLite database')
p_import_translation.add_argument('-s', '--source', action='store', dest='source', required=True, help='Path to the source .txt translated dump file')
p_import_translation.add_argument('-u', '--user', action='store', dest='user_name', required=True, help='The author of the translation')
p_import_translation.add_argument('-od', '--original_dump', action='store', dest='original_dump', required=False, help='Path to the source .txt original dump file')
p_import_translation.add_argument('-g', '--game', action='store', dest='game', required=False, help='Optional: Game ID(s) to use for custom parsing logic')
p_import_translation.set_defaults(func=import_translation)
p_export_translation = subparsers.add_parser('export_translation', help='Export translations to a dump file')
p_export_translation.add_argument('-db', '--database', action='store', dest='database_file', required=True, help='Path to the SQLite database')
p_export_translation.add_argument('-d', '--destination', action='store', dest='destination', required=True, help='Output path for the generated .txt dump')
p_export_translation.add_argument('-u', '--user', action='store', dest='user_name', required=False, help='The author whose translations you want to export')
p_export_translation.add_argument('-b', '--blocks', action='store', dest='blocks', required=False, nargs='+', help='Optional: Filter by specific block IDs')
p_export_translation.set_defaults(func=export_translation)
p_mark_empty = subparsers.add_parser('mark_empty', help='Mark empty texts as done')
p_mark_empty.add_argument('-db', '--database', dest='database_file', required=True)
p_mark_empty.add_argument('-u', '--user', dest='user_name', required=True)
p_mark_empty.set_defaults(func=mark_empty_texts_as_translated)

if __name__ == "__main__":
  args = parser.parse_args()
  if args.func:
    args.func(args)
  else:
    parser.print_help()
