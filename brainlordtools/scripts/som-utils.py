__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os, re, sqlite3, time
from rhutils.db import insert_translation, select_texts, select_translation_by_author, TranslationStatus

user_name = 'sadnes'
user_name1 = 'clomax'
resources_path = '/Users/robertofontanarosa/git/brainlordresources/som'
db = os.path.join(resources_path, 'db/som.sqlite3')
translation_path = os.path.join(resources_path, 'translation_text')
dump_ita_fullpath = os.path.join(translation_path, 'dump_ita.txt')
dump_user_fullpath = os.path.join(translation_path, f'dump_ita_{user_name}.txt')

import_user_translation = False
export_user_translation = False
mark_as_done = True

if import_user_translation:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  with open(dump_user_fullpath, 'r') as f:
    id = 1
    buffer = ''
    lines = f.readlines()
    for i, line in enumerate(lines):
      if '[ID ' in line or i == len(lines) - 1:
        if buffer != '':
          text_decoded = buffer.rstrip('\n\r')
          insert_translation(cur, id, 'TEST', user_name, text_decoded, TranslationStatus.DONE, time.time(), '', '')
          id += 1
          buffer = ''
        else:
          pass
      else:
        buffer += line
  cur.close()
  conn.commit()
  conn.close()

if mark_as_done:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  cur1 = conn.cursor()
  rows = select_texts(cur, ['1', '2'])
  for row in rows:
    id, text_decoded = row
    clear_text = re.sub(r'\[.*?\]\n?', '', text_decoded)
    if clear_text == '':
      insert_translation(cur1, id, 'TEST', user_name1, text_decoded, TranslationStatus.DONE, time.time(), '', '')
  cur.close()
  cur1.close()
  conn.commit()
  conn.close()

if export_user_translation:
  if os.path.isfile(dump_user_fullpath):
    os.remove(dump_user_fullpath)
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  with open(dump_user_fullpath, 'a') as f:
    rows = select_translation_by_author(cur, user_name)
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
