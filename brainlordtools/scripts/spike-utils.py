__author__ = "Roberto Fontanarosa"
__license__ = "GPLv2"
__version__ = ""
__maintainer__ = "Roberto Fontanarosa"
__email__ = "robertofontanarosa@gmail.com"

import os, sqlite3
from rhutils.db import select_translation_by_author

user_name = 'clomax'
resources_path = '/Users/robertofontanarosa/git/brainlordresources/spike'
db = os.path.join(resources_path, 'db/spike.sqlite3')
translation_path = os.path.join(resources_path, 'translation_text')
dump_user_fullpath = os.path.join(translation_path, f'dump_ita_{user_name}.txt')

export_user_translation = True

if export_user_translation:
  if not os.path.isdir(translation_path):
    os.mkdir(translation_path)
  if os.path.isfile(dump_user_fullpath):
    os.remove(dump_user_fullpath)
  conn = sqlite3.connect(db)
  conn.text_factory = str
  cur = conn.cursor()
  with open(dump_user_fullpath, 'a') as f:
    rows = select_translation_by_author(cur, user_name)
    for row in rows:
      _, _, text_decoded, _, addresses, translation, ref = row
      text = translation if translation else text_decoded
      f.write(f'{ref} - {addresses}')
      f.write('\r\n')
      f.write(text)
      f.write('\r\n')
      f.write('\r\n')
  cur.close()
  conn.commit()
  conn.close()
