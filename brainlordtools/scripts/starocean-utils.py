__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os, sqlite3, sys
from rhutils.db import insert_text

resources_path = '/Users/robertofontanarosa/git/brainlordresources/starocean'
db = os.path.join(resources_path, 'db/starocean.sqlite3')
dump_path = os.path.join(resources_path, 'dump_text')
translation_path = os.path.join(resources_path, 'translation_text')
dump_fullpath = os.path.join(dump_path, 'dump_eng.txt')
dump_amazon_fullpath = os.path.join(translation_path, f'dump_ita_amazon.txt')

import_dump = True
translate_dump_amazom = False

def starocean_dump_reader(dump_fullpath):
  buff = {}
  with open(dump_fullpath, 'r') as f:
    id = 0
    iterator = iter(f)
    for line in iterator:
      if line.startswith('<HEADER '):
        id += 1
        next_line = next(iterator)
        buff[id] = ['', line + next_line.strip('\n\r')]
      elif line.startswith('<BLOCK '):
        id += 1
        buff[id] = ['', line.strip('\n\r')]
      else:
        buff[id][0] += line
  return buff

if import_dump:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  buff = starocean_dump_reader(dump_fullpath)
  for id, value in buff.items():
    [text, ref] = value
    text_length = len(text)
    text_decoded = text.rstrip('\n\r')
    insert_text(cur, id, b'', text_decoded, '', '', 1, ref)
  cur.close()
  conn.commit()
  conn.close()

if translate_dump_amazom:
  import boto3
  client = boto3.client('translate')
  with open(dump_amazon_fullpath, 'a') as f:
    buff = starocean_dump_reader(dump_fullpath)
    for id, value in buff.items():
      [text, ref] = value
      translate_response = client.translate_text(
          Text=text,
          SourceLanguageCode='en',
          TargetLanguageCode='it',
          Settings={
              'Formality': 'INFORMAL'
          }
      )
      translated_text = translate_response['TranslatedText']
      f.write(ref)
      f.write('\n')
      f.write(translated_text)
