__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os, sqlite3
from rhutils.db import insert_text

resources_path = '/Users/robertofontanarosa/git/brainlordresources/starocean'
db = os.path.join(resources_path, 'db/starocean.sqlite3')
dump_path = os.path.join(resources_path, 'dump_text')
dump_fullpath = os.path.join(dump_path, 'dump_eng.txt')

import_dump = True

if import_dump:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  with open(dump_fullpath, 'r') as f:
    id = 0
    buffer = {}
    iterator = iter(f)
    for line in iterator:
      if line.startswith('<HEADER '):
        next_line = next(iterator)
        buffer[id] = ['', line + next_line.strip('\n\r')]
      elif line.startswith('<BLOCK '):
        id += 1
        buffer[id] = ['', line.strip('\n\r')]
      else:
        if id != 0:
          buffer[id][0] += line
    for id, value in buffer.items():
      [text, ref] = value
      text_length = len(text)
      text_decoded = text.rstrip('\n\r')
      insert_text(cur, id, b'', text_decoded, '', '', 1, ref)
  cur.close()
  conn.commit()
  conn.close()
