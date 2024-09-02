__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os, sqlite3, time
from rhutils.db import insert_text, insert_translation, select_translation_by_author, TranslationStatus

user_name = 'clomax'
resources_path = '/Users/robertofontanarosa/git/brainlordresources/starocean'
db = os.path.join(resources_path, 'db/starocean.sqlite3')
dump_path = os.path.join(resources_path, 'dump_text')
translation_path = os.path.join(resources_path, 'translation_text')
dump_fullpath = os.path.join(dump_path, 'dump_eng.txt')
translation_user_fullpath = os.path.join(translation_path, f'dump_ita_{user_name}.txt')

dump_amazon_fullpath = os.path.join(translation_path, 'dump_ita_amazon.txt')

dump1_fullpath = os.path.join(dump_path, 'dump_eng_1.txt')
dump2_fullpath = os.path.join(dump_path, 'dump_eng_2.txt')
dump1_deepl_fullpath = os.path.join(translation_path, 'dump_ita_deepl_1.txt')
dump2_deepl_fullpath = os.path.join(translation_path, 'dump_ita_deepl_2.txt')

import_dump = False
translate_dump_amazon = False
translate_dump_deepl = False
import_user_translation = False

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

if translate_dump_amazon:
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

if translate_dump_deepl:
  import deepl
  auth_key = "708b1cef-565d-499b-8e0a-81871821c2a0:fx"  # Replace with your key
  translator = deepl.Translator(auth_key)
  try:
    # translator.translate_document_from_filepath(
    #     dump1_fullpath,
    #     dump1_deepl_fullpath,
    #     target_lang="IT",
    #     formality="more"
    # )
    translator.translate_document_from_filepath(
        dump2_fullpath,
        dump2_deepl_fullpath,
        target_lang="IT",
        formality="more"
    )
  except deepl.DocumentTranslationException as error:
      doc_id = error.document_handle.id
      doc_key = error.document_handle.key
      print(f"Error after uploading ${error}, id: ${doc_id} key: ${doc_key}")
  except deepl.DeepLException as error:
      print(error)

if import_user_translation:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  buff = starocean_dump_reader(translation_user_fullpath)
  for id, value in buff.items():
    [text, ref] = value
    text_length = len(text)
    text_decoded = text.rstrip('\n\r')
    insert_text(cur, id, b'', text_decoded, '', '', 1, ref)
    insert_translation(cur, id, 'TEST', user_name, text_decoded, TranslationStatus.DONE, time.time(), '', '')
  cur.close()
  conn.commit()
  conn.close()
