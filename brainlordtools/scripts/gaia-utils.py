__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os, sqlite3, time
from rhutils.db import insert_text, insert_translation, select_translation_by_author, TranslationStatus

user_name = 'clomax'
resources_path = '/Users/robertofontanarosa/git/brainlordresources/gaia'
db = os.path.join(resources_path, 'db/gaia.sqlite3')
dump_path = os.path.join(resources_path, 'dump_text')
translation_path = os.path.join(resources_path, 'translation_text')
dump_fullpath = os.path.join(dump_path, 'dump_eng.txt')
translation_user_fullpath = os.path.join(translation_path, 'dump_ita.txt')

import_dump = False
import_user_translation = False

def gaia_dump_reader(dump_fullpath):
  buffer = {}
  with open(dump_fullpath, 'r') as f:
    id = 0
    for line in f:
      if line.startswith('[BLOCK '):
        id += 1
        buffer[id] = ['', line.strip('\n\r')]
      else:
        buffer[id][0] += line
  return buffer

if import_dump:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  buffer = gaia_dump_reader(dump_fullpath)
  for id, value in buffer.items():
    text, ref = value
    text_length = len(text)
    text_decoded = text.strip('\n\r')
    insert_text(cur, id, b'', text_decoded, '', '', 1, ref)
  cur.close()
  conn.commit()
  conn.close()

if import_user_translation:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  buff1 = gaia_dump_reader(translation_user_fullpath)
  buff2 = gaia_dump_reader(dump_fullpath)
  for id, value in buff1.items():
    text, ref = value
    if buff2[id][0] == text:
      continue
    text_length = len(text)
    text_decoded = text.rstrip('\n\r')
    insert_translation(cur, id, 'TEST', user_name, text_decoded, TranslationStatus.DONE, time.time(), '', '')
  cur.close()
  conn.commit()
  conn.close()
