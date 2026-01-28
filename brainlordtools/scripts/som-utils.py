__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os, re, sqlite3
from rhutils.db import insert_translation, select_texts, TranslationStatus

# user_name = 'clomax'
user_name= 'mog'
# user_name = 'reborn'
# user_name = 'sadnes'

resources_path = '/Users/robertofontanarosa/git/brainlordresources/som'
db = os.path.join(resources_path, 'db/som.sqlite3')
translation_path = os.path.join(resources_path, 'translation_text')

mark_as_done = False

if mark_as_done:
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  rows = select_texts(cur, ['1', '2'])
  for row in rows:
    id, text_decoded = row
    clear_text = re.sub(r'\[.*?\]\n?', '', text_decoded)
    if clear_text == '':
      insert_translation(cur, id, 'TEST', user_name, text_decoded, TranslationStatus.DONE, 60, '', '')
  cur.close()
  conn.commit()
  conn.close()
