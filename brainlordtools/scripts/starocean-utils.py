__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, sqlite3
from collections import OrderedDict
from rhtools3.db import insert_text

resources_path = '/Users/robertofontanarosa/git/brainlordresources/starocean'
db = os.path.join(resources_path, 'db/starocean.sqlite3')
dump_path = os.path.join(resources_path, 'dump_text')
dump_fullpath = os.path.join(dump_path, 'dump_en.txt')

import_dump = True

if import_dump:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  with open(dump_fullpath, 'r') as f:
    id = 0
    buffer = OrderedDict()
    for line in f:
      if '<BLOCK ' in line:
        id += 1
        buffer[id] = ['', line]
      elif '<HEADER' in line:
        pass
      else:
        if id != 0:
          buffer[id][0] += line
    for id, value in buffer.items():
      [text, ref] = value
      text_length = len(text)
      if id == 1813:
        print(text)
      text_decoded = text.rstrip('\n\r')
      insert_text(cur, id, b'', text_decoded, '', '', 1, ref)
  cur.close()
  conn.commit()
  conn.close()
