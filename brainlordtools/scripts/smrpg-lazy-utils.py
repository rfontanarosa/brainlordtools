__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os, sqlite3, time
from rhutils.db import insert_text, select_translation_by_author, insert_translation

user_name = 'ombra'
resources_path = '/Users/robertofontanarosa/git/brainlordresources/smrpg'
db = os.path.join(resources_path, 'db/smrpg.sqlite3')
dump_path = os.path.join(resources_path, 'dump_text')
translation_path = os.path.join(resources_path, 'translation_text')
dialogues_fullpath = os.path.join(dump_path, 'dialogues.txt')
dialogues_ita_fullpath = os.path.join(translation_path, 'dialogues_ita.txt')
dialogues_user_fullpath = os.path.join(translation_path, f'dialogues_ita_{user_name}.txt')
battle_dialogues_fullpath = os.path.join(dump_path, 'battleDialogues.txt')
battle_dialogues_ita_fullpath = os.path.join(translation_path, 'battleDialogues_ita.txt')
battle_dialogues_user_fullpath = os.path.join(translation_path, f'battleDialogues_ita_{user_name}.txt')

import_dump = True
import_user_translation = False
export_user_translation = True

if import_dump:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  id = 1
  with open(dialogues_fullpath, 'r') as f:
    for line in f:
      splittedLine = line.split('\t')
      ref = splittedLine[0].replace('{', '').replace('}', '')
      text_decoded = splittedLine[1].replace('\r', '').replace('\n', '')
      insert_text(cur, id, '', text_decoded, '', '', 1, ref)
      id += 1
  with open(battle_dialogues_fullpath, 'r') as f:
    for line in f:
      splittedLine = line.split('\t')
      ref = splittedLine[0].replace('{', '').replace('}', '')
      text_decoded = splittedLine[1].replace('\r', '').replace('\n', '')
      insert_text(cur, id, '', text_decoded, '', '', 2, ref)
      id += 1
  cur.close()
  conn.commit()
  conn.close()

if import_user_translation:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  id = 1
  with open(dialogues_user_fullpath, 'r') as f:
    for line in f:
      splittedLine = line.split('\t')
      ref = splittedLine[0].replace('{', '').replace('}', '')
      if user_name == 'lorenzooone':
        line1 = next(f)
        splittedLine = line1.split('\t')
        ref = splittedLine[0].replace('{', '').replace('}', '').replace('I:', '')
      if len(splittedLine) == 2:
        text_decoded = splittedLine[1].replace('\r', '').replace('\n', '')
        id = int(ref) + 1
        insert_translation(cur, id, 'TEST', user_name, text_decoded, 1, time.time(), '', '')
      id += 1
  with open(battle_dialogues_user_fullpath, 'r') as f:
    for line in f:
      splittedLine = line.split('\t')
      ref = splittedLine[0].replace('{', '').replace('}', '')
      if user_name == 'lorenzooone':
        line1 = next(f)
        splittedLine = line1.split('\t')
        ref = splittedLine[0].replace('{', '').replace('}', '').replace('I:', '')
      if len(splittedLine) == 2:
        text_decoded = splittedLine[1].replace('\r', '').replace('\n', '')
        id = int(ref) + 4097
        insert_translation(cur, id, 'TEST', user_name, text_decoded, 2, time.time(), '', '')
      id += 1
  cur.close()
  conn.commit()
  conn.close()

if export_user_translation:
  if os.path.isfile(dialogues_user_fullpath):
    os.remove(dialogues_user_fullpath)
  if os.path.isfile(battle_dialogues_user_fullpath):
    os.remove(battle_dialogues_user_fullpath)
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  with open(dialogues_user_fullpath, 'a') as f:
    rows = select_translation_by_author(cur, user_name, ['1'])
    for row in rows:
      _, _, text_decoded, _, _, translation, ref = row
      text = translation if translation else text_decoded
      f.write('{' + ref + '}' + '\t' + text)
      f.write('\n')
  with open(battle_dialogues_user_fullpath, 'a') as f:
    rows = select_translation_by_author(cur, user_name, ['2'])
    for row in rows:
      _, _, text_decoded, _, _, translation, ref = row
      text = translation if translation else text_decoded
      f.write('{' + ref + '}' + '\t' + text)
      f.write('\n')
  cur.close()
  conn.commit()
  conn.close()
