__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import sys, os, sqlite3, time
from rhtools3.db import insert_text, select_translation_by_author, insert_translation

user_name = 'clomax'
resources_path = '/Users/rfontanarosa/git/brainlordresources/soe'
db = os.path.join(resources_path, 'db/soe.sqlite3')
dump_path = os.path.join(resources_path, 'dump_text')
translation_path = os.path.join(resources_path, 'translation_text')
dump_fullpath = os.path.join(dump_path, 'dump_eng.txt')
dump_ita_fullpath = os.path.join(translation_path, 'dump_ita.txt')
dump_user_fullpath = os.path.join(translation_path, 'dump_ita_{}.txt'.format(user_name))

import_dump = True
import_user_translation = False
export_user_translation = True

if import_dump:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  with open(dump_fullpath, 'r') as f:
    id = 1
    text_decoded = ''
    for index, line in enumerate(f):
      if '<End>' in line:
        text_decoded += line[:-6]
        insert_text(cur, id, '', text_decoded, '', '', 1, '')
        id += 1
        text_decoded = ''
      else:
        text_decoded += line
  cur.close()
  conn.commit()
  conn.close()

if import_user_translation:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  with open(dump_user_fullpath, 'r') as f:
    id = 1
    text_decoded = ''
    for index, line in enumerate(f):
      if '<End>' in line:
        text_decoded += line[:-6]
        insert_translation(cur, id, 'TEST', user_name, text_decoded, 2, time.time(), '', '')
        id += 1
        text_decoded = ''
      else:
        text_decoded += line
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
      text_decoded = row[2]
      translation = row[5]
      text = translation if translation else text_decoded
      f.write(text)
      f.write('<End>\n')
  cur.close()
  conn.commit()
  conn.close()
