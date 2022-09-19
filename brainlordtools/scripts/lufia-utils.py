__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, sqlite3
from collections import OrderedDict
from rhtools3.db import insert_text, select_translation_by_author

user_name = 'clomax'
resources_path = '/Users/robertofontanarosa/git/brainlordresources/lufia'
db = os.path.join(resources_path, 'db/lufia.sqlite3')
dump_path = os.path.join(resources_path, 'dump_text')
translation_path = os.path.join(resources_path, 'translation_text')
dump_fullpath = os.path.join(dump_path, 'dump_eng.txt')
dump_ita_fullpath = os.path.join(translation_path, 'dump_ita.txt')
dump_user_fullpath = os.path.join(translation_path, 'dump_ita_{}.txt'.format(user_name))

import_dump = True
export_user_translation = True

if import_dump:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  with open(dump_fullpath, 'r') as f:
    id = 0
    buffer = OrderedDict()
    for line in f:
      if line.startswith('[BLOCK '):
        id += 1
        buffer[id] = ['', line.strip('\n\r')]
      else:
        buffer[id][0] += line
    for id, value in buffer.items():
      [text, ref] = value
      text_length = len(text)
      text_decoded = text.strip('\n\r')
      insert_text(cur, id, b'', text_decoded, '', '', 1, ref)
  cur.close()
  conn.commit()
  conn.close()

if export_user_translation:
  if os.path.isfile(dump_user_fullpath):
    os.remove(dump_user_fullpath)
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  with open(dump_user_fullpath, 'a') as f:
    rows = select_translation_by_author(cur, user_name, ['1'])
    for row in rows:
      _, _, text_decoded, _, _, translation, ref = row
      text = translation if translation else text_decoded
      f.write(ref)
      f.write('\r\n')
      f.write(text)
      f.write('\r\n')
      f.write('\r\n')
  cur.close()
  conn.commit()
  conn.close()
